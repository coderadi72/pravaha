"""Commercial traceability to an existing project."""
from sqlalchemy import ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base
from backend.app.models.organization import OrgRecord


class Client(OrgRecord, Base):
    __tablename__ = 'clients'
    name: Mapped[str] = mapped_column(Text)
    sector: Mapped[str] = mapped_column(Text, default='')


class Contact(OrgRecord, Base):
    __tablename__ = 'client_contacts'
    client_id: Mapped[str] = mapped_column(ForeignKey('clients.id'))
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text)


class Opportunity(OrgRecord, Base):
    __tablename__ = 'opportunities'
    client_id: Mapped[str] = mapped_column(ForeignKey('clients.id'))
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default='OPEN')


class Tender(OrgRecord, Base):
    __tablename__ = 'tenders'
    opportunity_id: Mapped[str] = mapped_column(ForeignKey('opportunities.id'))
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default='OPEN')


class Proposal(OrgRecord, Base):
    __tablename__ = 'proposals'
    tender_id: Mapped[str] = mapped_column(ForeignKey('tenders.id'))
    title: Mapped[str] = mapped_column(Text)
    amount: Mapped[float] = mapped_column(Numeric(18, 2))
    status: Mapped[str] = mapped_column(Text, default='DRAFT')


class CommercialContract(OrgRecord, Base):
    __tablename__ = 'commercial_contracts'
    proposal_id: Mapped[str] = mapped_column(ForeignKey('proposals.id'))
    project_id: Mapped[str] = mapped_column(ForeignKey('projects.id'), unique=True)
    title: Mapped[str] = mapped_column(Text)
    amount: Mapped[float] = mapped_column(Numeric(18, 2))
    status: Mapped[str] = mapped_column(Text, default='ACTIVE')
