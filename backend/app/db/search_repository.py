"""SQL-filtered, paginated search with authorization embedded in every branch."""
from sqlalchemy import select,union_all,func,literal,cast,Text,or_
from backend.app.core.errors import ApiError
from backend.app.models import Project,ProjectManagerAssignment,Team,TeamLeaderAssignment,ScheduleActivity,FieldUpdate,ScheduleVersion,ExecutionWarning,AuditEvent


def search(session,user,query,kind,limit,offset):
    if user.role not in {'ADMIN','PROJECT_MANAGER','TEAM_LEADER'}:
        raise ApiError(403, 'FORBIDDEN', 'This account has no execution-search permissions.')
    projects=select(Project.id).where(Project.organization_id==user.organization_id)
    team_ids=None
    if user.role=='PROJECT_MANAGER':projects=projects.join(ProjectManagerAssignment,ProjectManagerAssignment.project_id==Project.id).where(ProjectManagerAssignment.user_id==user.id)
    if user.role=='TEAM_LEADER':
        team_ids=select(Team.id).join(TeamLeaderAssignment,TeamLeaderAssignment.team_id==Team.id).where(TeamLeaderAssignment.user_id==user.id,Team.organization_id==user.organization_id)
        projects=projects.where(Project.id.in_(select(Team.project_id).where(Team.id.in_(team_ids))))
    term='%'+query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%'
    branches=[]
    def add(label,model,id_col,project_col,title,extra=()):
        if kind not in {'all',label}:return
        branches.append(select(literal(label).label('kind'),id_col.label('id'),project_col.label('projectId'),title.label('title')).where(project_col.in_(projects),title.ilike(term,escape='\\'),*extra))
    add('projects',Project,Project.id,Project.id,Project.name)
    add('activities',ScheduleActivity,ScheduleActivity.id,ScheduleActivity.project_id,ScheduleActivity.payload_json['activityName'].astext, [ScheduleActivity.payload_json['archived'].astext.is_distinct_from('true')]+([ScheduleActivity.team_id.in_(team_ids)] if team_ids is not None else []))
    add('field-updates',FieldUpdate,FieldUpdate.id,FieldUpdate.project_id,FieldUpdate.payload_json['rawText'].astext,[FieldUpdate.team_id.in_(team_ids)] if team_ids is not None else [])
    if user.role!='TEAM_LEADER':
        add('versions',ScheduleVersion,ScheduleVersion.id,ScheduleVersion.project_id,ScheduleVersion.filename)
        add('warnings',ExecutionWarning,ExecutionWarning.id,ExecutionWarning.project_id,ExecutionWarning.payload_json['reason'].astext)
        if kind in {'all','audit','memory'}:
            scope=or_(AuditEvent.details_json['projectId'].astext.in_(projects), (AuditEvent.entity=='project') & AuditEvent.entity_id.in_(projects))
            if user.role=='ADMIN':scope=literal(True)
            branches.append(select(literal('memory' if kind=='memory' else 'audit').label('kind'),AuditEvent.id.label('id'),AuditEvent.details_json['projectId'].astext.label('projectId'),AuditEvent.action.label('title')).where(AuditEvent.organization_id==user.organization_id,scope,or_(AuditEvent.action.ilike(term,escape='\\'),cast(AuditEvent.details_json,Text).ilike(term,escape='\\'))))
    if not branches:return {'items':[],'total':0,'limit':limit,'offset':offset}
    combined=union_all(*branches).subquery()
    total=session.scalar(select(func.count()).select_from(combined))
    rows=session.execute(select(combined).order_by(combined.c.kind,combined.c.id).limit(limit).offset(offset)).mappings().all()
    return {'items':[dict(r) for r in rows],'total':total,'limit':limit,'offset':offset}
