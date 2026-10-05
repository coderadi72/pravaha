"""Normalized request, procurement, receipt and inventory movement ledger."""
from datetime import date
from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base
from backend.app.models.organization import OrgRecord


class Vendor(OrgRecord, Base):
    __tablename__ = 'vendors'
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text, default='')


class Material(OrgRecord, Base):
    __tablename__ = 'materials'
    name: Mapped[str] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(Text)


class Store(OrgRecord, Base):
    __tablename__ = 'stores'
    name: Mapped[str] = mapped_column(Text)
    location_id: Mapped[str] = mapped_column(ForeignKey('locations.id'))


class MaterialRequest(OrgRecord, Base):
    __tablename__ = 'material_requests'
    __table_args__ = (CheckConstraint('quantity > 0', name='ck_material_request_quantity'),)
    project_id: Mapped[str] = mapped_column(ForeignKey('projects.id'))
    team_id: Mapped[str | None] = mapped_column(ForeignKey('teams.id'))
    activity_id: Mapped[str | None] = mapped_column(ForeignKey('schedule_activities.id'))
    material_id: Mapped[str] = mapped_column(ForeignKey('materials.id'))
    quantity: Mapped[float] = mapped_column(Numeric(18, 3))
    required_on: Mapped[date] = mapped_column(Date)
    requested_by: Mapped[str] = mapped_column(ForeignKey('users.id'))
    status: Mapped[str] = mapped_column(Text, default='REQUESTED')


class PurchaseOrder(OrgRecord, Base):
    __tablename__ = 'purchase_orders'
    request_id: Mapped[str] = mapped_column(ForeignKey('material_requests.id'), unique=True)
    vendor_id: Mapped[str] = mapped_column(ForeignKey('vendors.id'))
    quantity: Mapped[float] = mapped_column(Numeric(18, 3))
    unit_price: Mapped[float] = mapped_column(Numeric(18, 2))
    status: Mapped[str] = mapped_column(Text, default='ORDERED')


class GoodsReceipt(OrgRecord, Base):
    __tablename__ = 'goods_receipts'
    order_id: Mapped[str] = mapped_column(ForeignKey('purchase_orders.id'))
    store_id: Mapped[str] = mapped_column(ForeignKey('stores.id'))
    quantity: Mapped[float] = mapped_column(Numeric(18, 3))
    received_on: Mapped[date] = mapped_column(Date)


class MaterialMovement(OrgRecord, Base):
    __tablename__ = 'material_movements'
    __table_args__ = (CheckConstraint("kind IN ('RECEIPT','ISSUE')", name='ck_material_movement_kind'),
        CheckConstraint('quantity > 0', name='ck_material_movement_quantity'))
    material_id: Mapped[str] = mapped_column(ForeignKey('materials.id'))
    store_id: Mapped[str] = mapped_column(ForeignKey('stores.id'))
    project_id: Mapped[str] = mapped_column(ForeignKey('projects.id'))
    team_id: Mapped[str | None] = mapped_column(ForeignKey('teams.id'))
    receipt_id: Mapped[str | None] = mapped_column(ForeignKey('goods_receipts.id'), unique=True)
    quantity: Mapped[float] = mapped_column(Numeric(18, 3))
    kind: Mapped[str] = mapped_column(Text)
    occurred_on: Mapped[date] = mapped_column(Date)
