-- Representative SQL fragments extracted from the APEX app.
-- They are kept as reference only and may require adaptation for Python services.

-- Page 2: Contracts
select A."INS_ID",
       A."INS_ID" dog_id,
       KONTRAGENT_NAME(A."OWNER") as OWN_NAME
from "#OWNER#"."INS_ANKETA" A;

-- Page 11: Policy stock
select "INS_ID", STORE_DATE, DEC_DIVISION("DIVISION_ID",1) div,
       DEC_USER2("USER_ID") usr, "POL_SERY", "POL_NUMF", "POL_NUMT"
from "#OWNER#"."INS_POLIS_STORE";

-- Page 12: Client search
SELECT TB_ID as SEL, TB_ID, TB_MASTERID, TB_SURNAME, TB_NAME, TB_PATRONYM
from "#OWNER#"."TB_KONTRAGENT";

-- Page 29: Payment
select "INS_ID","ANKETA_ID","POLIS_SERY","POLIS_NUMBER","DIVISION_ID","USER_ID",
       "OPL_DATA","OPL_SUMMA","INS_TYPE","OPL_TYPE"
from "#OWNER#"."INS_OPLATA";

-- Page 850: API modules
select m.API_ID, m.API_NAME, m.API_DESC, m.ACTIVE, m.CREATED_DATE
from API_MODULES m;
