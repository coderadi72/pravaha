"""Explainable, bounded dependency exposure. No invented float or forecast dates."""
from collections import defaultdict,deque
from backend.app.services.execution_intelligence import day


def downstream(activities,edges):
    rows={a['activityId']:a for a in activities};out=defaultdict(list)
    for e in sorted(edges,key=lambda e:(e['predecessorId'],e['successorId'],e['type'],e['lagDays'],e['id'])):
        if e['predecessorId'] in rows and e['successorId'] in rows:out[e['predecessorId']].append(e)
    items=[]
    for source_id,source in sorted(rows.items()):
        if source['delayDays']<=0:continue
        queue=deque([(source_id,0,None,[source_id])]);best={}
        while queue:
            current,depth,inherited,path=queue.popleft()
            for edge in out[current]:
                target_id=edge['successorId'];target=rows[target_id];pred=rows[current];kind=edge['type']
                if target_id in path:return {'status':'UNKNOWN','reason':'Persisted graph contains a cycle.','items':[]}
                start_constraint=kind in {'FS','SS'}
                source_start=kind in {'SS','SF'}
                source_date=day(pred['plannedStart'] if source_start else pred['plannedEnd'])
                target_date=day(target['plannedStart'] if start_constraint else target['plannedEnd'])
                signal=pred['startVarianceDays'] if source_start else max(pred['finishVarianceDays'] or 0,pred['overdueDays'])
                if inherited is not None:signal=max(signal or 0,inherited)
                slack=(target_date-source_date).days-edge['lagDays'] if source_date and target_date else None
                started=bool(target.get('actualStart') or (target.get('confirmedProgress') or 0)>0)
                not_applicable=target['status']=='COMPLETED' or (start_constraint and started)
                exposure=max(0,(signal or 0)-max(0,slack)) if signal is not None and slack is not None else None
                state='NOT_APPLICABLE' if not_applicable else 'UNKNOWN' if exposure is None else 'ESTIMATED' if exposure>0 else 'NOT_APPLICABLE'
                if exposure is not None and best.get(target_id,-1)>=exposure:continue
                best[target_id]=exposure if exposure is not None else 0
                evidence={'dependencyId':edge['id'],'sourceVersionId':edge['versionId'],'predecessorId':current,'successorId':target_id,'type':kind,'lagDays':edge['lagDays'],'plannedSlackDays':slack,'sourceVarianceDays':signal,'path':path+[target_id],'downstreamAlreadyStarted':started,'downstreamTiming':target['timing']}
                items.append({'sourceActivityId':source_id,'activityId':target_id,'depth':depth+1,'status':state,'potentialExposureDays':exposure,'reason':'Potential dependency exposure, not an exact forecast.' if state=='ESTIMATED' else 'Constraint already satisfied by downstream execution.' if not_applicable else 'Insufficient date evidence.' if state=='UNKNOWN' else 'Planned slack absorbs the current delay signal.','evidence':evidence})
                if len(items)>5000:return {'status':'UNKNOWN','reason':'Dependency impact exceeds the 5,000-result capacity; no partial prediction is returned.','items':[]}
                if exposure and not not_applicable:queue.append((target_id,depth+1,exposure,path+[target_id]))
    return {'status':'KNOWN' if edges else 'NOT_APPLICABLE','reason':f'{len(edges)} persisted relationships evaluated.','items':items}
