from __future__ import annotations

from oracle_dash_app.db.oracle_helpers import first_existing_column


def _client_name_expr(alias: str = "k") -> str:
    return f"""case
        when nvl(trim({alias}.TB_ORGNAME), 'x') <> 'x' then {alias}.TB_ORGNAME
        else trim(nvl({alias}.TB_SURNAME,'') || ' ' || nvl({alias}.TB_NAME,'') || ' ' || nvl({alias}.TB_PATRONYM,''))
    end"""


def clients_query() -> str:
    pinfl_col = first_existing_column("INS_KONTRAGENT", ["TB_PINFL", "PINFL"])
    inn_col = first_existing_column("INS_KONTRAGENT", ["TB_ORGINN", "ORGINN", "INN"])
    phone_col = first_existing_column("INS_KONTRAGENT", ["TB_PHONE", "PHONE", "TEL", "TEL1"])

    pinfl_expr = "null"
    search_parts = [
        "upper(nvl(k.TB_SURNAME,'')) like '%' || upper(:search) || '%'",
        "upper(nvl(k.TB_NAME,'')) like '%' || upper(:search) || '%'",
        "upper(nvl(k.TB_PATRONYM,'')) like '%' || upper(:search) || '%'",
        "upper(nvl(k.TB_ORGNAME,'')) like '%' || upper(:search) || '%'",
    ]

    if pinfl_col and inn_col:
        pinfl_expr = f"nvl(k.{pinfl_col}, k.{inn_col})"
        search_parts.append(f"nvl(k.{pinfl_col}, k.{inn_col}) like '%' || :search || '%'")
    elif pinfl_col:
        pinfl_expr = f"k.{pinfl_col}"
        search_parts.append(f"k.{pinfl_col} like '%' || :search || '%'")
    elif inn_col:
        pinfl_expr = f"k.{inn_col}"
        search_parts.append(f"k.{inn_col} like '%' || :search || '%'")

    if phone_col:
        search_parts.append(f"nvl(k.{phone_col},'') like '%' || :search || '%'")

    phone_expr = f"k.{phone_col}" if phone_col else "null"

    return f"""
select * from (
    select
        k.TB_ID as client_id,
        {_client_name_expr('k')} as client_name,
        k.TB_FIZYUR as client_type,
        {pinfl_expr} as pinfl_inn,
        {phone_expr} as phone,
        trim(nvl(k.TB_ULICA,'') || ' ' || nvl(k.TB_DOM,'') || ' ' || nvl(k.TB_KV,'')) as address,
        k.USER_ID as user_id
    from INS_KONTRAGENT k
    where k.TB_OLD = 0
      and (
            :search is null or :search = '' or
            {' or '.join(search_parts)}
          )
    order by k.TB_ID desc
)
where rownum <= :limit_rows
"""


def contracts_query() -> str:
    status_col = first_existing_column("INS_ANKETA", ["STATUS", "TB_STATUS", "INS_STATUS", "STAT", "INS_STAT"])
    policy_contract_fk = first_existing_column("INS_POLIS", ["TB_ANKETA", "ANKETA_ID"])
    branch_col = first_existing_column("INS_ANKETA", ["FILIAL", "TB_FILIAL", "FILIAL_NAME", "BRANCH_NAME", "BRANCH_ID"])
    division_col = first_existing_column("INS_ANKETA", ["DIVISION", "TB_DIVISION", "PODRAZDELENIE", "DIVISION_NAME", "DEPARTMENT_NAME"])
    policy_col = first_existing_column("INS_ANKETA", ["POLIS", "POLIS_NUM", "POLIS_NUMBER", "POLICY_NO"])
    code_col = first_existing_column("INS_ANKETA", ["KOD", "CODE", "PRODUCT_CODE"])
    checked_col = first_existing_column("INS_ANKETA", ["PROVERENO", "CHECKED", "IS_CHECKED"])
    product_col = first_existing_column("INS_ANKETA", ["INS_PRODUCT", "PRODUCT_NAME", "INS_KIND", "INS_OBJECT"])
    phones_col = first_existing_column("INS_KONTRAGENT", ["TB_PHONE", "PHONE", "TEL", "TEL1"])
    address_col = first_existing_column("INS_KONTRAGENT", ["TB_ULICA", "ADDRESS", "ADRES"])
    beneficiary_col = first_existing_column("INS_ANKETA", ["BENEFICIAR", "BENEFICIARY", "VIGODOPRIOBRETATEL"])
    liability_sum_col = first_existing_column("INS_ANKETA", ["INS_OTV_SUM", "OTV_SUM", "RESP_SUM", "INS_OTV"])
    transh_col = first_existing_column("INS_ANKETA", ["TRANSHI", "TRANCHES", "TRANCH_CNT"])
    premium_sum_col = first_existing_column("INS_ANKETA", ["PREM_SUM", "INS_PREM_SUM", "POLIS_PREM", "INS_PREM"])
    fact_amount_col = first_existing_column("INS_ANKETA", ["FACT_POSTUP", "FACT_SUM", "POSTUP_SUM", "PAYED_SUM"])
    policy_premium_col = first_existing_column("INS_ANKETA", ["POLIS_PREM", "POLICY_PREMIUM", "PREM_POLIS"])
    refund_sum_col = first_existing_column("INS_ANKETA", ["RETURN_SUM", "REFUND_SUM", "VOZVRAT_SUM"])
    last_payment_col = first_existing_column("INS_ANKETA", ["LAST_PAY_DATE", "DATE_LAST_PAY", "PAY_DATE_LAST"])
    pay_condition_col = first_existing_column("INS_ANKETA", ["PAY_CONDITION", "PAY_TERMS", "USLOV_OPLATI"])
    class_col = first_existing_column("INS_ANKETA", ["CLASS", "CLASS_ID", "RISK_CLASS"])
    created_by_col = first_existing_column("INS_ANKETA", ["CREATED_BY", "USER_ID", "TB_USER", "CREATE_USER"])
    created_at_col = first_existing_column("INS_ANKETA", ["CREATED_AT", "CREATED_DATE", "DATE_CREATE", "INS_DATE"])
    updated_at_col = first_existing_column("INS_ANKETA", ["UPDATED_AT", "MODIFIED_DATE", "DATE_MODIFY", "DATE_UPDATE"])
    commission_col = first_existing_column("INS_ANKETA", ["COMMISSION", "COMMISSION_SUM", "AGENT_COMMISSION"])
    total_losses_col = first_existing_column("INS_ANKETA", ["TOTAL_LOSSES", "LOSS_COUNT", "UBITOK_CNT"])
    last_claim_col = first_existing_column("INS_ANKETA", ["LAST_CLAIM_DATE", "DATE_LAST_EVENT", "LAST_EVENT_DATE"])
    total_paid_col = first_existing_column("INS_ANKETA", ["TOTAL_PAID", "PAYED_SUM", "VSEGO_VYPLACHENO"])
    last_payout_col = first_existing_column("INS_ANKETA", ["LAST_PAYOUT_DATE", "DATE_LAST_PAYOUT", "LAST_PAYMENT_OUT_DATE"])
    rate_col = first_existing_column("INS_ANKETA", ["RATE", "STAVKA", "TARIFF_RATE"])
    region_col = first_existing_column("INS_ANKETA", ["REGION", "REGION_ID", "TB_REGION"])
    pay_type_col = first_existing_column("INS_ANKETA", ["PAY_TYPE", "TIP_OPLATI", "OPL_TYPE"])
    files_col = first_existing_column("INS_ANKETA", ["FILES_CNT", "FILE_CNT", "FILES_COUNT"])
    lessee_col = first_existing_column("INS_ANKETA", ["ZAEMSHIK", "LESSEE_NAME", "LIZING_CLIENT", "CLIENT_LESSEE"])
    requisites_col = first_existing_column("INS_ANKETA", ["REKVIZIT", "REQUISITES", "BANK_REKVIZIT"])
    birthdate_col = first_existing_column("INS_KONTRAGENT", ["TB_BIRTHDAY", "BIRTHDAY", "DATE_BIRTH"])
    active_col = first_existing_column("INS_ANKETA", ["ACTIVE", "IS_ACTIVE", "AKTIV"])
    ben_mfo_col = first_existing_column("INS_ANKETA", ["BEN_MFO", "MFO", "BANK_MFO"])
    declaration_col = first_existing_column("INS_ANKETA", ["DECLARATION", "DEKLARATSIYA"])
    old_contract_col = first_existing_column("INS_ANKETA", ["OLD_CONTRACT_NO", "OLD_INS_NUM", "PREV_CONTRACT_NO"])
    prop_address_col = first_existing_column("INS_ANKETA", ["IMUSH_ADDRESS", "PROPERTY_ADDRESS", "OBJECT_ADDRESS"])
    borrower_pinfl_col = first_existing_column("INS_ANKETA", ["ZAEM_PINFL", "BORROWER_PINFL", "PINFL_BORROWER"])
    borrower_doc_col = first_existing_column("INS_ANKETA", ["ZAEM_DOC", "BORROWER_DOC", "PASSPORT_INN"])
    lot_id_col = first_existing_column("INS_ANKETA", ["LOT_ID", "LOTID"])
    country_col = first_existing_column("INS_ANKETA", ["INS_COUNTRY", "COUNTRY_ID", "STRANA_STRAHOVATELYA"])

    def sel(alias: str, col: str | None, out: str) -> str:
        return f", {alias}.{col} as {out}" if col else f", cast(null as varchar2(4000)) as {out}"

    has_policy_expr = (
        f"(select case when exists (select 1 from INS_POLIS p2 where p2.{policy_contract_fk} = a.INS_ID) then 1 else 0 end from dual)"
        if policy_contract_fk else "0"
    )

    return f"""
select * from (
    select
        {has_policy_expr} as policy_issued,
        a.INS_ID as contract_id,
        a.INS_NUM as contract_no,
        {_client_name_expr('k')} as client_name,
        a.OWNER as client_id,
        a.INS_TYPE as insurance_type_id,
        a.INS_DATE as issue_date,
        a.INS_DATEF as start_date,
        a.INS_DATET as end_date,
        a.INS_PREM as premium,
        a.INS_OTV as liability
        {sel('a', status_col, 'status')}
        {sel('a', branch_col, 'branch_name')}
        {sel('a', division_col, 'division_name')}
        {sel('a', policy_col, 'policy_no')}
        {sel('a', code_col, 'code')}
        {sel('a', checked_col, 'checked_flag')}
        {sel('a', product_col, 'insurance_product')}
        {sel('k', phones_col, 'phones')}
        {sel('k', address_col, 'address')}
        {sel('a', beneficiary_col, 'beneficiary')}
        {sel('a', liability_sum_col, 'liability_sum')}
        {sel('a', transh_col, 'transhi')}
        {sel('a', premium_sum_col, 'premium_sum')}
        {sel('a', fact_amount_col, 'fact_received')}
        {sel('a', policy_premium_col, 'policy_premium')}
        {sel('a', refund_sum_col, 'refund_sum')}
        {sel('a', last_payment_col, 'last_payment_date')}
        {sel('a', pay_condition_col, 'payment_condition')}
        {sel('a', class_col, 'risk_class')}
        {sel('a', created_by_col, 'created_by')}
        {sel('a', created_at_col, 'created_at')}
        {sel('a', updated_at_col, 'updated_at')}
        {sel('a', commission_col, 'commission')}
        {sel('a', total_losses_col, 'total_losses')}
        {sel('a', last_claim_col, 'last_claim_date')}
        {sel('a', total_paid_col, 'total_paid')}
        {sel('a', last_payout_col, 'last_payout_date')}
        {sel('a', rate_col, 'rate')}
        {sel('a', region_col, 'region_name')}
        {sel('a', pay_type_col, 'payment_type_name')}
        {sel('a', files_col, 'files_count')}
        {sel('a', lessee_col, 'lessee_name')}
        {sel('a', requisites_col, 'requisites')}
        {sel('k', birthdate_col, 'birthdate')}
        {sel('a', active_col, 'active_flag')}
        {sel('a', ben_mfo_col, 'beneficiary_mfo')}
        {sel('a', declaration_col, 'declaration')}
        {sel('a', old_contract_col, 'old_contract_no')}
        {sel('a', prop_address_col, 'property_address')}
        {sel('a', borrower_pinfl_col, 'borrower_pinfl')}
        {sel('a', borrower_doc_col, 'borrower_doc')}
        {sel('a', lot_id_col, 'lot_id')}
        {sel('a', country_col, 'insured_country')}
    from INS_ANKETA a
    left join INS_KONTRAGENT k on k.TB_ID = a.OWNER
    where (
        :search is null or :search = '' or
        upper(nvl(a.INS_NUM, '')) like '%' || upper(:search) || '%' or
        upper({_client_name_expr('k')}) like '%' || upper(:search) || '%'
    )
    and (
        :date_from is null or
        (
            (:date_field = 'issue_date' and trunc(a.INS_DATE) >= to_date(:date_from, 'YYYY-MM-DD')) or
            (:date_field = 'start_date' and trunc(a.INS_DATEF) >= to_date(:date_from, 'YYYY-MM-DD')) or
            (:date_field = 'end_date' and trunc(a.INS_DATET) >= to_date(:date_from, 'YYYY-MM-DD'))
        )
    )
    and (
        :date_to is null or
        (
            (:date_field = 'issue_date' and trunc(a.INS_DATE) <= to_date(:date_to, 'YYYY-MM-DD')) or
            (:date_field = 'start_date' and trunc(a.INS_DATEF) <= to_date(:date_to, 'YYYY-MM-DD')) or
            (:date_field = 'end_date' and trunc(a.INS_DATET) <= to_date(:date_to, 'YYYY-MM-DD'))
        )
    )
    order by a.INS_ID desc
)
where rownum <= :limit_rows
"""


def policies_query() -> str:
    series_col = first_existing_column("INS_POLIS", ["POLIS_SERY", "TB_SERY", "SERY", "SERIES"])
    number_col = first_existing_column("INS_POLIS", ["POLIS_NUMBER", "TB_NUMBER", "NUMBER1", "NUM"])
    anketa_col = first_existing_column("INS_POLIS", ["TB_ANKETA", "ANKETA_ID"])
    issue_col = first_existing_column("INS_POLIS", ["DATA_VIDACHI", "TB_DATECONTROL", "DATE_VIDACHI", "TB_DATE_BEGIN"])
    fund_status_col = first_existing_column("INS_POLIS", ["FOND_STATUS", "TB_STATUS", "STATUS"])
    policy_uuid_col = first_existing_column("INS_POLIS", ["POLISUUID", "UUID", "FOND_UUID"])
    division_col = first_existing_column("INS_POLIS", ["TB_DIVISION", "DIVISION_ID", "INS_DIV"])
    user_col = first_existing_column("INS_POLIS", ["TB_USER", "USER_ID"])
    status_col = first_existing_column("INS_POLIS", ["TB_STATUS", "STATUS"])

    series_expr = f"p.{series_col}" if series_col else "null"
    number_expr = f"p.{number_col}" if number_col else "null"
    join_expr = f"a.INS_ID = p.{anketa_col}" if anketa_col else "1=0"
    issue_expr = f"p.{issue_col}" if issue_col else "null"
    fund_status_expr = f"p.{fund_status_col}" if fund_status_col else "null"
    uuid_expr = f"p.{policy_uuid_col}" if policy_uuid_col else "null"
    division_expr = f"p.{division_col}" if division_col else "null"
    user_expr = f"p.{user_col}" if user_col else "null"
    status_expr = f"p.{status_col}" if status_col else "null"

    return f"""
select * from (
    select
        p.TB_ID as policy_id,
        {series_expr} as policy_series,
        {number_expr} as policy_number,
        a.INS_NUM as contract_no,
        a.INS_ID as contract_id,
        {_client_name_expr('k')} as client_name,
        {issue_expr} as issue_date,
        {status_expr} as policy_status,
        {fund_status_expr} as fund_status,
        {uuid_expr} as policy_uuid,
        {division_expr} as division_id,
        {user_expr} as user_id
    from INS_POLIS p
    left join INS_ANKETA a on {join_expr}
    left join INS_KONTRAGENT k on k.TB_ID = a.OWNER
    where (
        :search is null or :search = '' or
        upper(nvl(a.INS_NUM, '')) like '%' || upper(:search) || '%' or
        upper(nvl({series_expr}, '')) like '%' || upper(:search) || '%' or
        upper(nvl({number_expr}, '')) like '%' || upper(:search) || '%' or
        upper({_client_name_expr('k')}) like '%' || upper(:search) || '%'
    )
    and (
        :date_from is null or
        (:date_field = 'issue_date' and trunc({issue_expr}) >= to_date(:date_from, 'YYYY-MM-DD'))
    )
    and (
        :date_to is null or
        (:date_field = 'issue_date' and trunc({issue_expr}) <= to_date(:date_to, 'YYYY-MM-DD'))
    )
    order by p.TB_ID desc
)
where rownum <= :limit_rows
"""


def payments_query() -> str:
    contract_fk = first_existing_column("INS_OPLATA", ["ANKETA_ID", "TB_ANKETA"])
    amount_col = first_existing_column("INS_OPLATA", ["OPL_SUMMA", "OPLATA"])
    doc_col = first_existing_column("INS_OPLATA", ["DOC_NUM", "DOCUMENT_NO"])
    policy_series_col = first_existing_column("INS_OPLATA", ["POLIS_SERY", "TB_SERY"])
    policy_number_col = first_existing_column("INS_OPLATA", ["POLIS_NUMBER", "TB_NUMBER"])
    insurance_type_col = first_existing_column("INS_OPLATA", ["INS_TYPE", "TB_TYPE"])

    join_expr = f"a.INS_ID = o.{contract_fk}" if contract_fk else "1=0"
    amount_expr = f"o.{amount_col}" if amount_col else "null"
    doc_expr = f"o.{doc_col}" if doc_col else "null"
    series_expr = f"o.{policy_series_col}" if policy_series_col else "null"
    number_expr = f"o.{policy_number_col}" if policy_number_col else "null"
    ins_type_expr = f"o.{insurance_type_col}" if insurance_type_col else "null"

    return f"""
select * from (
    select
        o.INS_ID as payment_id,
        {('o.' + contract_fk) if contract_fk else 'null'} as contract_id,
        a.INS_NUM as contract_no,
        {_client_name_expr('k')} as client_name,
        o.OPL_DATA as payment_date,
        {amount_expr} as amount,
        o.OPL_TYPE as payment_type,
        {doc_expr} as document_no,
        o.STATUS as status,
        {series_expr} as policy_series,
        {number_expr} as policy_number,
        {ins_type_expr} as insurance_type_id
    from INS_OPLATA o
    left join INS_ANKETA a on {join_expr}
    left join INS_KONTRAGENT k on k.TB_ID = a.OWNER
    where (
        :search is null or :search = '' or
        upper(nvl(a.INS_NUM, '')) like '%' || upper(:search) || '%' or
        upper(nvl({doc_expr}, '')) like '%' || upper(:search) || '%' or
        upper({_client_name_expr('k')}) like '%' || upper(:search) || '%'
    )
    and (
        :date_from is null or
        (:date_field = 'payment_date' and trunc(o.OPL_DATA) >= to_date(:date_from, 'YYYY-MM-DD'))
    )
    and (
        :date_to is null or
        (:date_field = 'payment_date' and trunc(o.OPL_DATA) <= to_date(:date_to, 'YYYY-MM-DD'))
    )
    order by o.INS_ID desc
)
where rownum <= :limit_rows
"""


def documents_query() -> str:
    title_ru_col = first_existing_column("INS_PTURI", ["POLIS_NAME_RUS", "POLIS_NAME_UZ", "POLIS_NAME"])
    title_col = first_existing_column("INS_PTURI", ["POLIS_NAME", "POLIS_NAME_RUS"])
    code_col = first_existing_column("INS_PTURI", ["KOD_NUM", "KOD", "CODE"])
    page_col = first_existing_column("INS_PTURI", ["TB_PAGE", "PAGE_ID", "APEX_PAGE"])
    active_col = first_existing_column("INS_PTURI", ["ACTIVE", "STATUS"])
    created_col = first_existing_column("INS_PTURI", ["CREATED_DATE", "CREATE_DATE", "CR_DATE"])
    modified_col = first_existing_column("INS_PTURI", ["MODIFIED_DATE", "MOD_DATE", "UPDATED_DATE"])

    title_ru_expr = f"p.{title_ru_col}" if title_ru_col else "null"
    title_expr = f"p.{title_col}" if title_col else "null"
    code_expr = f"p.{code_col}" if code_col else "null"

    selects = [
        'p.INS_ID as product_id',
        f"{code_expr} as code",
        f"{title_ru_expr} as title_ru",
        f"{title_expr} as title",
        f"p.{page_col} as apex_page" if page_col else 'null as apex_page',
        'p.MIN_DAY',
        'p.MAX_DAY',
        f"p.{active_col} as active" if active_col else 'null as active',
        f"p.{created_col} as created_date" if created_col else 'null as created_date',
        f"p.{modified_col} as modified_date" if modified_col else 'null as modified_date',
    ]

    return f"""
select * from (
    select
        {', '.join(selects)}
    from INS_PTURI p
    where (
        :search is null or :search = '' or
        upper(nvl({code_expr}, '')) like '%' || upper(:search) || '%' or
        upper(nvl({title_ru_expr}, '')) like '%' || upper(:search) || '%' or
        upper(nvl({title_expr}, '')) like '%' || upper(:search) || '%'
    )
    order by p.INS_ID
)
where rownum <= :limit_rows
"""



def contract_detail_query() -> str:
    object_col = first_existing_column("INS_ANKETA", ["INS_OBJECT", "OBJECT_NAME", "OBEKT_NAME", "OBEKT", "OBJECT_INS", "PRODUCT_NAME"])
    class_col = first_existing_column("INS_ANKETA", ["CLASS", "CLASS_ID", "RISK_CLASS", "INS_CLASS"])
    division_id_col = first_existing_column("INS_ANKETA", ["INS_DIV", "DIVISION_ID", "DIV", "TB_DIV", "DIVISION"])
    created_by_col = first_existing_column("INS_ANKETA", ["CREATED_BY", "USER_ID", "TB_USER", "CREATE_USER"])
    val_type_col = first_existing_column("INS_ANKETA", ["VAL_TYPE", "CURRENCY_ID", "CURR_ID"])
    pturi_name_col = first_existing_column("INS_PTURI", ["POLIS_NAME_RUS", "POLIS_NAME", "TITLE_RU", "TITLE"])
    pturi_code_col = first_existing_column("INS_PTURI", ["KOD_NUM", "CODE", "PRODUCT_CODE"])
    curr_id_col = first_existing_column("P_SP_CURRENCY", ["SP_ID", "ID"])
    curr_name_col = first_existing_column("P_SP_CURRENCY", ["SP_NAME1", "NAME", "SP_NAME"])
    div_id_col = first_existing_column("SP_DIVISION", ["SP_ID", "ID"])
    div_name_col = first_existing_column("SP_DIVISION", ["SP_NAME1", "NAME", "SP_NAME"])
    pay_fk_col = first_existing_column("INS_OPLATA", ["ANKETA_ID", "TB_ANKETA"])
    pay_amount_col = first_existing_column("INS_OPLATA", ["OPL_SUMMA", "OPLATA"])

    object_expr = f"a.{object_col}" if object_col else "null"
    class_expr = f"a.{class_col}" if class_col else "null"
    type_name_expr = f"p.{pturi_name_col}" if pturi_name_col else "null"
    product_code_expr = f"p.{pturi_code_col}" if pturi_code_col else "null"
    division_name_expr = (
        f"(select max(d.{div_name_col}) from SP_DIVISION d where d.{div_id_col} = a.{division_id_col})"
        if (division_id_col and div_id_col and div_name_col) else "null"
    )
    currency_name_expr = f"c.{curr_name_col}" if (val_type_col and curr_id_col and curr_name_col) else "null"
    amount_paid_expr = (
        f"(select sum(o.{pay_amount_col}) from INS_OPLATA o where o.{pay_fk_col} = a.INS_ID)"
        if (pay_fk_col and pay_amount_col) else "null"
    )
    created_by_expr = f"a.{created_by_col}" if created_by_col else "null"
    return f"""
select
    a.INS_ID as contract_id,
    a.INS_NUM as contract_no,
    a.OWNER as client_id,
    a.INS_TYPE as insurance_type_id,
    {type_name_expr} as insurance_type_name,
    {object_expr} as insurance_object,
    {class_expr} as insurance_class,
    {product_code_expr} as product_code,
    a.INS_DATE as issue_date,
    a.INS_DATEF as start_date,
    a.INS_DATET as end_date,
    a.INS_PREM as premium,
    a.INS_OTV as liability,
    {division_name_expr} as division_name,
    {created_by_expr} as created_by,
    {currency_name_expr} as currency_name,
    {amount_paid_expr} as amount_paid,
    a.*,
    """ + _client_name_expr('k') + f""" as client_name,
    k.TB_ID as kontragent_id
from INS_ANKETA a
left join INS_KONTRAGENT k on k.TB_ID = a.OWNER
left join INS_PTURI p on p.INS_ID = a.INS_TYPE
left join P_SP_CURRENCY c on {('c.' + curr_id_col + ' = a.' + val_type_col) if (val_type_col and curr_id_col and curr_name_col) else '1=0'}
where a.INS_ID = :contract_id
"""


def contract_policies_query() -> str:
    anketa_col = first_existing_column("INS_POLIS", ["TB_ANKETA", "ANKETA_ID"])
    series_col = first_existing_column("INS_POLIS", ["POLIS_SERY", "TB_SERY", "SERY", "SERIES"])
    number_col = first_existing_column("INS_POLIS", ["POLIS_NUMBER", "TB_NUMBER", "NUMBER1", "NUM"])
    issue_col = first_existing_column("INS_POLIS", ["DATA_VIDACHI", "TB_DATECONTROL", "DATE_VIDACHI", "TB_DATE_BEGIN"])
    status_col = first_existing_column("INS_POLIS", ["TB_STATUS", "STATUS"])
    if not anketa_col:
        return "select cast(null as number) as policy_id, cast(null as varchar2(100)) as policy_series, cast(null as varchar2(100)) as policy_number, cast(null as date) as issue_date, cast(null as varchar2(100)) as status from dual where 1=0"
    series_expr = f"p.{series_col}" if series_col else "null"
    num_expr = f"p.{number_col}" if number_col else "null"
    issue_expr = f"p.{issue_col}" if issue_col else "null"
    status_expr = f"p.{status_col}" if status_col else "null"
    return f"""
select
    p.TB_ID as policy_id,
    {series_expr} as policy_series,
    {num_expr} as policy_number,
    {issue_expr} as issue_date,
    {status_expr} as status
from INS_POLIS p
where p.{anketa_col} = :contract_id
order by p.TB_ID desc
"""


def contract_payments_query() -> str:
    contract_fk = first_existing_column("INS_OPLATA", ["ANKETA_ID", "TB_ANKETA"])
    payment_id_col = first_existing_column("INS_OPLATA", ["TB_ID", "INS_ID", "ID"])
    amount_col = first_existing_column("INS_OPLATA", ["OPL_SUMMA", "OPLATA"])
    pay_date_col = first_existing_column("INS_OPLATA", ["OPL_DATE", "PAY_DATE", "DATE_OPLATI", "OPL_DATA"])
    doc_col = first_existing_column("INS_OPLATA", ["DOC_NUM", "DOCUMENT_NO"])
    if not contract_fk:
        return "select cast(null as number) as payment_id, cast(null as date) as payment_date, cast(null as number) as amount, cast(null as varchar2(100)) as document_no from dual where 1=0"
    payment_id_expr = f"o.{payment_id_col}" if payment_id_col else "null"
    amount_expr = f"o.{amount_col}" if amount_col else "null"
    date_expr = f"o.{pay_date_col}" if pay_date_col else "null"
    doc_expr = f"o.{doc_col}" if doc_col else "null"
    order_expr = payment_id_expr if payment_id_col else (date_expr if pay_date_col else amount_expr)
    return f"""
select
    {payment_id_expr} as payment_id,
    {date_expr} as payment_date,
    {amount_expr} as amount,
    {doc_expr} as document_no
from INS_OPLATA o
where o.{contract_fk} = :contract_id
order by {order_expr} desc
"""


def contract_api_logs_query() -> str:
    anketa_col = first_existing_column("FOND_API_LOG2", ["ANKETA_ID", "TB_ANKETA", "CONTRACT_ID"])
    polis_col = first_existing_column("FOND_API_LOG2", ["POLIS_ID", "TB_POLIS"])
    status_code_col = first_existing_column("FOND_API_LOG2", ["STATUS_CODE", "HTTP_STATUS", "HTTP_CODE"])
    reason_col = first_existing_column("FOND_API_LOG2", ["REASON_PHRASE", "REASON", "STATUS_TEXT"])
    timespent_col = first_existing_column("FOND_API_LOG2", ["TIMESPENT", "TIME_SPENT", "ELAPSED_MS"])
    err_code_col = first_existing_column("FOND_API_LOG2", ["ERROR_CODE", "ERR_CODE"])
    err_text_col = first_existing_column("FOND_API_LOG2", ["ERROR_TEXT", "ERR_TEXT", "ERROR_MESSAGE"])
    log_sent_col = first_existing_column("FOND_API_LOG2", ["LOG_SENT", "REQUEST_BODY", "LOG_REQUEST"])

    def expr(alias: str, col: str | None, out: str) -> str:
        return f", {alias}.{col} as {out}" if col else f", cast(null as varchar2(4000)) as {out}"

    if polis_col and log_sent_col:
        polis_expr = f"coalesce(to_char(l.{polis_col}), regexp_substr(dbms_lob.substr(l.{log_sent_col}, 32767, 1), '\"polisUuid\"\\s*:\\s*\"([^\"]+)\"', 1, 1, null, 1)) as polis_id"
    elif polis_col:
        polis_expr = f"to_char(l.{polis_col}) as polis_id"
    elif log_sent_col:
        polis_expr = f"regexp_substr(dbms_lob.substr(l.{log_sent_col}, 32767, 1), '\"polisUuid\"\\s*:\\s*\"([^\"]+)\"', 1, 1, null, 1) as polis_id"
    else:
        polis_expr = "cast(null as varchar2(4000)) as polis_id"

    return f"""
select * from (
    select
        l.LOG_ID as log_id,
        l.LOG_DATE as log_date,
        l.API_NAME as api_name
        {expr('l', anketa_col, 'anketa_id')}
        , {polis_expr}
        {expr('l', status_code_col, 'status_code')}
        {expr('l', reason_col, 'reason_phrase')}
        {expr('l', timespent_col, 'timespent')}
        {expr('l', err_code_col, 'error_code')}
        {expr('l', err_text_col, 'error_text')}
    from FOND_API_LOG2 l
    where {('l.' + anketa_col + ' = :contract_id') if anketa_col else '1=0'}
    order by l.LOG_ID desc
)
where rownum <= 100
"""


def contract_api_log_detail_query() -> str:
    log_recv_col = first_existing_column("FOND_API_LOG2", ["LOG_RECIEVED", "LOG_RECEIVED", "LOG_RESPONSE", "RESPONSE_BODY"])
    log_sent_col = first_existing_column("FOND_API_LOG2", ["LOG_SENT", "REQUEST_BODY", "LOG_REQUEST"])
    error_info_col = first_existing_column("FOND_API_LOG2", ["ERROR_INFO", "ERR_INFO"])
    http_version_col = first_existing_column("FOND_API_LOG2", ["HTTP_VERSION", "HTTP_VER"])
    usr_col = first_existing_column("FOND_API_LOG2", ["USR", "LOG_USR", "USER_ID"])
    log_div_col = first_existing_column("FOND_API_LOG2", ["LOG_DIV", "DIVISION_ID", "DIV"])
    anketa_col = first_existing_column("FOND_API_LOG2", ["ANKETA_ID", "TB_ANKETA", "CONTRACT_ID"])
    polis_col = first_existing_column("FOND_API_LOG2", ["POLIS_ID", "TB_POLIS"])
    status_code_col = first_existing_column("FOND_API_LOG2", ["STATUS_CODE", "HTTP_STATUS", "HTTP_CODE"])
    reason_col = first_existing_column("FOND_API_LOG2", ["REASON_PHRASE", "REASON", "STATUS_TEXT"])
    timespent_col = first_existing_column("FOND_API_LOG2", ["TIMESPENT", "TIME_SPENT", "ELAPSED_MS"])
    err_code_col = first_existing_column("FOND_API_LOG2", ["ERROR_CODE", "ERR_CODE"])
    err_text_col = first_existing_column("FOND_API_LOG2", ["ERROR_TEXT", "ERR_TEXT", "ERROR_MESSAGE"])

    def expr(alias: str, col: str | None, out: str) -> str:
        return f", {alias}.{col} as {out}" if col else f", cast(null as varchar2(4000)) as {out}"

    def clob_expr(alias: str, col: str | None, out: str) -> str:
        return f", dbms_lob.substr({alias}.{col}, 32767, 1) as {out}" if col else f", cast(null as varchar2(32767)) as {out}"

    if polis_col and log_sent_col:
        polis_expr = f"coalesce(to_char(l.{polis_col}), regexp_substr(dbms_lob.substr(l.{log_sent_col}, 32767, 1), '\"polisUuid\"\\s*:\\s*\"([^\"]+)\"', 1, 1, null, 1)) as polis_id"
    elif polis_col:
        polis_expr = f"to_char(l.{polis_col}) as polis_id"
    elif log_sent_col:
        polis_expr = f"regexp_substr(dbms_lob.substr(l.{log_sent_col}, 32767, 1), '\"polisUuid\"\\s*:\\s*\"([^\"]+)\"', 1, 1, null, 1) as polis_id"
    else:
        polis_expr = "cast(null as varchar2(4000)) as polis_id"

    return f"""
select
    l.LOG_ID as log_id,
    l.LOG_DATE as log_date,
    l.API_NAME as api_name
    {expr('l', usr_col, 'usr')}
    {expr('l', log_div_col, 'log_div')}
    {expr('l', anketa_col, 'anketa_id')}
    , {polis_expr}
    {expr('l', status_code_col, 'status_code')}
    {expr('l', reason_col, 'reason_phrase')}
    {expr('l', timespent_col, 'timespent')}
    {expr('l', err_code_col, 'error_code')}
    {expr('l', err_text_col, 'error_text')}
    {expr('l', error_info_col, 'error_info')}
    {expr('l', http_version_col, 'http_version')}
    {clob_expr('l', log_sent_col, 'log_sent')}
    {clob_expr('l', log_recv_col, 'log_received')}
from FOND_API_LOG2 l
where l.LOG_ID = :log_id
"""
