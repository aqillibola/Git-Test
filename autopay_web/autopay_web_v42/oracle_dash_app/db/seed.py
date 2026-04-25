from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session
from oracle_dash_app.db.schema import Base, Client, Contract, Policy, Payment, PrintTemplate, ApiModule


def create_demo_data(engine) -> None:
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        exists = session.scalar(select(Client.id).limit(1))
        if exists:
            return

        clients = [
            Client(full_name="Абдуллаев Бекзод", pinfl_inn="30201010010001", phone="+998901111111", address="Ташкент"),
            Client(full_name="ООО Navruz Servis", client_type="company", pinfl_inn="309876543", phone="+998909999999", address="Самарканд"),
            Client(full_name="Каримова Дилноза", pinfl_inn="30201010010002", phone="+998933333333", address="Бухара"),
        ]
        session.add_all(clients)
        session.flush()

        contracts = [
            Contract(contract_no="VI-2026-0001", client_id=clients[0].id, insurance_type="Travel", issue_date="2026-04-01", start_date="2026-04-10", end_date="2026-05-10", premium=120000, liability=50000000, status="active"),
            Contract(contract_no="VI-2026-0002", client_id=clients[1].id, insurance_type="Property", issue_date="2026-04-02", start_date="2026-04-05", end_date="2027-04-04", premium=9800000, liability=1500000000, status="active"),
            Contract(contract_no="VI-2026-0003", client_id=clients[2].id, insurance_type="Accident", issue_date="2026-04-03", start_date="2026-04-07", end_date="2027-04-06", premium=450000, liability=120000000, status="draft"),
        ]
        session.add_all(contracts)
        session.flush()

        policies = [
            Policy(policy_series="AA", policy_number="0001001", contract_id=contracts[0].id, issue_date="2026-04-10", printed=1, fund_status="sent", defect_status="none"),
            Policy(policy_series="AB", policy_number="0001002", contract_id=contracts[1].id, issue_date="2026-04-05", printed=1, fund_status="pending", defect_status="none"),
            Policy(policy_series="AC", policy_number="0001003", contract_id=contracts[2].id, issue_date="2026-04-07", printed=0, fund_status="new", defect_status="none"),
        ]
        session.add_all(policies)

        payments = [
            Payment(contract_id=contracts[0].id, payment_date="2026-04-10", amount=120000, payment_type="card", document_no="PAY-001", status="booked"),
            Payment(contract_id=contracts[1].id, payment_date="2026-04-05", amount=5000000, payment_type="bank", document_no="PAY-002", status="partial"),
            Payment(contract_id=contracts[1].id, payment_date="2026-04-06", amount=4800000, payment_type="bank", document_no="PAY-003", status="booked"),
        ]
        session.add_all(payments)

        session.add_all([
            PrintTemplate(code="CONTRACT", title="Договор страхования", sql_text="select * from contracts where id = :id", body_text="Шаблон договора"),
            PrintTemplate(code="POLICY", title="Полис", sql_text="select * from policies where id = :id", body_text="Шаблон полиса"),
        ])
        session.add_all([
            ApiModule(api_name="FOND_SEND_POLICY", api_desc="Отправка полиса в ФОНД", active=1),
            ApiModule(api_name="FOND_SEND_DEFECT", api_desc="Отправка испорченного полиса", active=1),
            ApiModule(api_name="PAYMENT_STATUS_SYNC", api_desc="Синхронизация платежей", active=0),
        ])

        session.commit()
