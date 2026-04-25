DASHBOARD_METRICS = {
    "clients": "select count(*) from INS_KONTRAGENT where TB_OLD = 0",
    "contracts": "select count(*) from INS_ANKETA",
    "policies": "select count(*) from INS_POLIS",
    "payments_total": "select nvl(sum(OPL_SUMMA),0) from INS_OPLATA",
}

DASHBOARD_PLAN_FACT = """
select 
 f.*,
 f.opl - f.yopl as oneday,
 (f_osago + f_osgor + f_osgop) as obv,
 case 
   when f.opl / decode(f.mnplan, 0, 1, nvl(f.mnplan, 1)) * 100 > 1000 then null
   else round(f.opl / decode(f.mnplan, 0, 1, nvl(f.mnplan, 1)) * 100, 2)
 end as mperc,
 case 
   when f.opl / decode(f.allplan, 0, 1, nvl(f.allplan, 1)) * 100 > 1000 then null
   else round(f.opl / decode(f.allplan, 0, 1, nvl(f.allplan, 1)) * 100, 2)
 end as yperc
from (
    select 
        case
            when substr(d.sp_id, -3) = '000' then d.sp_name1
            else ' - ' || d.sp_name1
        end as division_name,
        d.sp_id as division_id,
        a.ins_prem as allplan,
        g.ins_prem as mnplan,
        y.opl as yopl,
        m.opl as mopl,
        v.allp as opl,
        v.osgo as f_osago,
        v.osgor as f_osgor,
        v.osgop as f_osgop,
        v.oila as f_oila,
        v.allp + v.oila as oplplus,
        v.other as f_other,
        hb.opl as hbopl
    from sp_division d
    left join (
        select division_id, sum(ins_prem) ins_prem
        from ins_forecast
        where date_from <= last_day(trunc(sysdate,'MM'))
          and date_to   >= trunc(sysdate,'Y')
        group by division_id
    ) g on g.division_id = d.sp_id
    left join (
        select division_id, sum(ins_prem) ins_prem
        from ins_forecast
        where date_from <= last_day(add_months(trunc(sysdate,'Y'),12))
          and date_to   >= trunc(sysdate,'Y')
        group by division_id
    ) a on a.division_id = d.sp_id
    left join (
        select
            div,
            nvl(p448_opl,0) + nvl(p2_opl,0) + nvl(p3_opl,0) + nvl(p4_opl,0) as allp,
            nvl(p448_opl,0) as osgo,
            nvl(p2_opl,0) as osgor,
            nvl(p3_opl,0) as osgop,
            nvl(p162_opl,0) as oila,
            nvl(p4_opl,0) as other
        from (
            select
                div,
                decode(pturi,3,1,4002,2,4003,3,162,162,4) as pr,
                opl_sum as opl
            from vw_factopl_
            where opl_date between trunc(sysdate,'Y') and trunc(sysdate)
        )
        pivot (
            sum(opl) as opl for pr in (1 p448, 2 p2, 3 p3, 4 p4, 162 p162)
        )
    ) v on v.div = d.sp_id
    left join (
        select div, sum(opl_sum) as opl
        from vw_factopl_
        where opl_date between trunc(sysdate,'Y') and trunc(sysdate - 1)
          and pturi <> 162
        group by div
    ) y on y.div = d.sp_id
    left join (
        select div, sum(opl_sum) as opl
        from vw_factopl_
        where opl_date between trunc(sysdate,'MM') and trunc(sysdate)
          and pturi <> 162
        group by div
    ) m on m.div = d.sp_id
    left join (
        select div, sum(opl_sum) as opl
        from vw_factopl_
        where opl_date between trunc(sysdate,'Y') and trunc(sysdate)
          and hb = 2
        group by div
    ) hb on hb.div = d.sp_id
    where d.sp_active = 1
    order by d.sp_sort
) f
"""

CLIENTS = """
select * from (
    select
        k.TB_ID as client_id,
        case
            when nvl(trim(k.TB_ORGNAME), 'x') <> 'x' then k.TB_ORGNAME
            else trim(nvl(k.TB_SURNAME,'') || ' ' || nvl(k.TB_NAME,'') || ' ' || nvl(k.TB_PATRONYM,''))
        end as client_name,
        k.TB_FIZYUR as client_type,
        nvl(k.TB_PINFL, k.TB_ORGINN) as pinfl_inn,
        k.TB_PHONE as phone,
        trim(nvl(k.TB_ULICA,'') || ' ' || nvl(k.TB_DOM,'') || ' ' || nvl(k.TB_KV,'')) as address,
        k.USER_ID as user_id
    from INS_KONTRAGENT k
    where k.TB_OLD = 0
      and (
            :search is null or :search = '' or
            upper(nvl(k.TB_SURNAME,'')) like '%' || upper(:search) || '%' or
            upper(nvl(k.TB_NAME,'')) like '%' || upper(:search) || '%' or
            upper(nvl(k.TB_PATRONYM,'')) like '%' || upper(:search) || '%' or
            upper(nvl(k.TB_ORGNAME,'')) like '%' || upper(:search) || '%' or
            nvl(k.TB_PINFL, k.TB_ORGINN) like '%' || :search || '%'
          )
    order by k.TB_ID desc
)
where rownum <= :limit_rows
"""

CONTRACTS = """
select * from (
    select
        a.INS_ID as contract_id,
        a.INS_NUM as contract_no,
        case
            when nvl(trim(k.TB_ORGNAME), 'x') <> 'x' then k.TB_ORGNAME
            else trim(nvl(k.TB_SURNAME,'') || ' ' || nvl(k.TB_NAME,'') || ' ' || nvl(k.TB_PATRONYM,''))
        end as client_name,
        a.OWNER as client_id,
        a.INS_TYPE as insurance_type_id,
        a.INS_DATE as issue_date,
        a.INS_DATEF as start_date,
        a.INS_DATET as end_date,
        a.INS_PREM as premium,
        a.INS_OTV as liability,
        a.STATUS as status
    from INS_ANKETA a
    left join INS_KONTRAGENT k on k.TB_ID = a.OWNER
    order by a.INS_ID desc
)
where rownum <= :limit_rows
"""

POLICIES = """
select * from (
    select
        p.TB_ID as policy_id,
        p.POLIS_SERY as policy_series,
        p.POLIS_NUMBER as policy_number,
        a.INS_NUM as contract_no,
        a.INS_ID as contract_id,
        case
            when nvl(trim(k.TB_ORGNAME), 'x') <> 'x' then k.TB_ORGNAME
            else trim(nvl(k.TB_SURNAME,'') || ' ' || nvl(k.TB_NAME,'') || ' ' || nvl(k.TB_PATRONYM,''))
        end as client_name,
        p.DATA_VIDACHI as issue_date,
        p.TB_STATUS as policy_status,
        p.FOND_STATUS as fund_status,
        p.POLISUUID as policy_uuid,
        p.TB_DIVISION as division_id,
        p.TB_USER as user_id
    from INS_POLIS p
    left join INS_ANKETA a on a.INS_ID = p.TB_ANKETA
    left join INS_KONTRAGENT k on k.TB_ID = a.OWNER
    order by p.TB_ID desc
)
where rownum <= :limit_rows
"""

PAYMENTS = """
select * from (
    select
        o.INS_ID as payment_id,
        o.ANKETA_ID as contract_id,
        a.INS_NUM as contract_no,
        case
            when nvl(trim(k.TB_ORGNAME), 'x') <> 'x' then k.TB_ORGNAME
            else trim(nvl(k.TB_SURNAME,'') || ' ' || nvl(k.TB_NAME,'') || ' ' || nvl(k.TB_PATRONYM,''))
        end as client_name,
        o.OPL_DATA as payment_date,
        o.OPL_SUMMA as amount,
        o.OPL_TYPE as payment_type,
        o.DOC_NUM as document_no,
        o.STATUS as status,
        o.POLIS_SERY as policy_series,
        o.POLIS_NUMBER as policy_number,
        o.INS_TYPE as insurance_type_id
    from INS_OPLATA o
    left join INS_ANKETA a on a.INS_ID = o.ANKETA_ID
    left join INS_KONTRAGENT k on k.TB_ID = a.OWNER
    order by o.INS_ID desc
)
where rownum <= :limit_rows
"""

DOCUMENT_TEMPLATES = """
select * from (
    select
        p.INS_ID as product_id,
        p.KOD_NUM as code,
        p.POLIS_NAME_RUS as title_ru,
        p.POLIS_NAME as title,
        p.SERIES,
        p.TB_PAGE as apex_page,
        p.MIN_DAY,
        p.MAX_DAY,
        p.ACTIVE,
        p.CREATED_DATE,
        p.MODIFIED_DATE
    from INS_PTURI p
    order by p.INS_ID
)
where rownum <= :limit_rows
"""

API_MODULES = """
select * from (
    select
        m.API_ID,
        m.API_NAME,
        m.API_DESC,
        m.ACTIVE,
        m.CREATED_DATE,
        m.MODIFIED_DATE,
        (select count(1) from API_PROGRAMMS p where p.MODULE_ID = m.API_ID) as prg_cnt,
        (select count(1) from API_UNV_LOG l where l.MODULE_ID = m.API_ID) as log_cnt,
        (select count(1) from API_UNV_TRANSACTION t where t.MODULE_ID = m.API_ID) as tr_cnt,
        (select count(1) from API_UNV_TRANSACTION t where t.MODULE_ID = m.API_ID and t.ANKETA_ID is not null) as ank_cnt,
        (select count(1) from API_UNV_TRANSACTION t where t.MODULE_ID = m.API_ID and t.POLIS_ID is not null) as pol_cnt
    from API_MODULES m
    order by m.API_ID desc
)
where rownum <= :limit_rows
"""

ORACLE_INFO = {
    "current_schema": "select sys_context('USERENV','CURRENT_SCHEMA') from dual",
    "db_name": "select sys_context('USERENV','DB_NAME') from dual",
    "service_name": "select sys_context('USERENV','SERVICE_NAME') from dual",
    "con_name": "select sys_context('USERENV','CON_NAME') from dual",
    "instance_name": "select instance_name from v$instance",
    "version": "select banner_full from v$version where rownum = 1",
}


DASHBOARD_MONTHLY = """
with months as (
    select add_months(trunc(sysdate, 'Y'), level - 1) as month_date
    from dual
    connect by level <= extract(month from sysdate)
),
actuals as (
    select
        trunc(opl_date, 'MM') as month_date,
        sum(opl_sum) as fact_amount,
        sum(case when pturi = 3 then opl_sum else 0 end) as f_osago,
        sum(case when pturi = 4002 then opl_sum else 0 end) as f_osgor,
        sum(case when pturi = 4003 then opl_sum else 0 end) as f_osgop,
        sum(case when pturi = 162 then opl_sum else 0 end) as f_oila,
        sum(case when hb = 2 then opl_sum else 0 end) as f_halkbank,
        sum(case when pturi not in (3, 4002, 4003, 162) and nvl(hb,0) <> 2 then opl_sum else 0 end) as f_other
    from vw_factopl_
    where opl_date between trunc(sysdate, 'Y') and trunc(sysdate)
    group by trunc(opl_date, 'MM')
),
plans as (
    select
        m.month_date,
        nvl(sum(f.ins_prem), 0) as plan_amount
    from months m
    left join ins_forecast f
      on f.date_from <= last_day(m.month_date)
     and f.date_to >= m.month_date
    group by m.month_date
)
select
    m.month_date,
    to_char(m.month_date, 'YYYY-MM') as month_label,
    nvl(a.fact_amount, 0) as fact_amount,
    nvl(p.plan_amount, 0) as plan_amount,
    case
        when nvl(p.plan_amount, 0) = 0 then 0
        else round(nvl(a.fact_amount, 0) / p.plan_amount * 100, 2)
    end as month_percent,
    nvl(a.f_osago, 0) as f_osago,
    nvl(a.f_osgor, 0) as f_osgor,
    nvl(a.f_osgop, 0) as f_osgop,
    nvl(a.f_oila, 0) as f_oila,
    nvl(a.f_halkbank, 0) as f_halkbank,
    nvl(a.f_other, 0) as f_other
from months m
left join actuals a on a.month_date = m.month_date
left join plans p on p.month_date = m.month_date
order by m.month_date
"""
