from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey, func


class Base(DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_type: Mapped[str] = mapped_column(String(20), default="person")
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    pinfl_inn: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(32), default="")
    address: Mapped[str] = mapped_column(String(255), default="")


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contract_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    insurance_type: Mapped[str] = mapped_column(String(128), index=True)
    issue_date: Mapped[str] = mapped_column(String(20))
    start_date: Mapped[str] = mapped_column(String(20))
    end_date: Mapped[str] = mapped_column(String(20))
    premium: Mapped[float] = mapped_column(Float, default=0)
    liability: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(32), default="draft")


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    policy_series: Mapped[str] = mapped_column(String(16), index=True)
    policy_number: Mapped[str] = mapped_column(String(32), index=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"), index=True)
    issue_date: Mapped[str] = mapped_column(String(20))
    printed: Mapped[int] = mapped_column(Integer, default=0)
    fund_status: Mapped[str] = mapped_column(String(32), default="new")
    defect_status: Mapped[str] = mapped_column(String(32), default="none")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"), index=True)
    payment_date: Mapped[str] = mapped_column(String(20))
    amount: Mapped[float] = mapped_column(Float, default=0)
    payment_type: Mapped[str] = mapped_column(String(64), default="cash")
    document_no: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(32), default="booked")


class PrintTemplate(Base):
    __tablename__ = "print_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    sql_text: Mapped[str] = mapped_column(String(4000), default="")
    body_text: Mapped[str] = mapped_column(String(4000), default="")


class ApiModule(Base):
    __tablename__ = "api_modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_name: Mapped[str] = mapped_column(String(128), unique=True)
    api_desc: Mapped[str] = mapped_column(String(500), default="")
    active: Mapped[int] = mapped_column(Integer, default=1)
    request_input_type: Mapped[str] = mapped_column(String(32), default="json")
    response_output_type: Mapped[str] = mapped_column(String(32), default="json")
