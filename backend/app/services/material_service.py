"""Inventory is a ledger; receipt/issue and audit share the caller transaction."""
from uuid import uuid4
from sqlalchemy import case, func, select
from backend.app import models as m
from backend.app.core.errors import ApiError
from backend.app.core.permissions import actor
from backend.app.db.repository import append_audit
from backend.app.db.organization_repository import public


def balance(session, organization_id, store_id, material_id):
    return session.scalar(select(func.coalesce(func.sum(case((m.MaterialMovement.kind == 'RECEIPT', m.MaterialMovement.quantity), else_=-m.MaterialMovement.quantity)), 0)).where(
        m.MaterialMovement.organization_id == organization_id, m.MaterialMovement.store_id == store_id, m.MaterialMovement.material_id == material_id))


def stock_page(session, organization_id, query, limit, offset):
    statement = select(m.Store.id.label('store_id'), m.Store.name.label('store'), m.Material.id.label('material_id'), m.Material.name.label('material'), m.Material.unit,
        func.sum(case((m.MaterialMovement.kind == 'RECEIPT', m.MaterialMovement.quantity), else_=-m.MaterialMovement.quantity)).label('balance')).join(m.MaterialMovement, m.MaterialMovement.store_id == m.Store.id).join(m.Material, m.Material.id == m.MaterialMovement.material_id).where(m.Store.organization_id == organization_id).group_by(m.Store.id, m.Material.id)
    if query:
        pattern = '%' + query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_') + '%'
        statement = statement.where(m.Material.name.ilike(pattern, escape='\\') | m.Store.name.ilike(pattern, escape='\\'))
    total = session.scalar(select(func.count()).select_from(statement.subquery()))
    rows = session.execute(statement.order_by(m.Store.id,m.Material.id).limit(limit).offset(offset)).mappings()
    return {'items':[{**row, 'balance':float(row['balance'])} for row in rows], 'total':total,'limit':limit,'offset':offset}


def receive(session, user, data):
    order = session.get(m.PurchaseOrder, data['order_id'])
    request = session.get(m.MaterialRequest, order.request_id)
    received = session.scalar(select(func.coalesce(func.sum(m.GoodsReceipt.quantity), 0)).where(m.GoodsReceipt.order_id == order.id))
    if order.status != 'ORDERED' or data['quantity'] <= 0 or received + data['quantity'] > order.quantity:
        raise ApiError(409, 'INVALID_RECEIPT', 'Receipt must be positive and cannot exceed the ordered quantity.')
    receipt = m.GoodsReceipt(id='GR-'+str(uuid4()), organization_id=user.organization_id, **data)
    session.add(receipt)
    session.flush()
    session.add(m.MaterialMovement(id='MM-'+str(uuid4()), organization_id=user.organization_id, material_id=request.material_id,
        store_id=data['store_id'], project_id=request.project_id, team_id=request.team_id, receipt_id=receipt.id, quantity=data['quantity'], kind='RECEIPT', occurred_on=data['received_on']))
    if received + data['quantity'] == order.quantity:
        order.status = 'RECEIVED'
    append_audit(session, actor(user), 'Goods received and stock credited', 'goods_receipt', receipt.id, {'projectId': request.project_id, 'orderId': order.id, 'quantity': float(data['quantity'])})
    return public(receipt)


def issue(session, user, data):
    if data['quantity'] <= 0 or balance(session, user.organization_id, data['store_id'], data['material_id']) < data['quantity']:
        raise ApiError(409, 'INSUFFICIENT_STOCK', 'Issue requires positive quantity and sufficient recorded stock.')
    movement = m.MaterialMovement(id='MM-'+str(uuid4()), organization_id=user.organization_id, receipt_id=None, kind='ISSUE', **data)
    session.add(movement)
    append_audit(session, actor(user), 'Material issued to execution', 'material_movement', movement.id, {'projectId': data['project_id'], 'quantity': float(data['quantity'])})
    return public(movement)
