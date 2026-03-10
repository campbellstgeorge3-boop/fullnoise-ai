"""Postgres models: clients, reports, questions."""
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid_str() -> str:
    return str(uuid4())


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid_str)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_report_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    reports: Mapped[list["Report"]] = relationship("Report", back_populates="client", order_by="Report.created_at.desc()")
    questions: Mapped[list["Question"]] = relationship("Question", back_populates="client", order_by="Question.created_at.desc()")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid_str)
    client_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    month: Mapped[str] = mapped_column(String(7), nullable=False)  # YYYY-MM
    revenue: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    costs: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    profit: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    jobs: Mapped[int] = mapped_column(nullable=False, default=0)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    client: Mapped["Client"] = relationship("Client", back_populates="reports")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid_str)
    client_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    client: Mapped["Client"] = relationship("Client", back_populates="questions")


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid_str)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
