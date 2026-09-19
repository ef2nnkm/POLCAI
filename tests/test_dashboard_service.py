from datetime import date
import pandas as pd
from dashboard.services.dashboard_service import prepare_data, filter_data, build_dashboard_metrics, build_dc_table

def sample():
    return pd.DataFrame({"DC":["8155"],"DC_NAME":["8155 - TEST"],"DATE_PST":["2026-09-19"],"NATIONAL_CHAIN":["A"],"NATIONAL_CHAIN_DESC":["Alpha"],"SAP_ORDER":[10],"SAP_RECEIVED_LINES":[20],"SAP_CONFIRMED_LINES":[18],"SAP_REJECTED_LINE":[2],"SAP_DELIVERIES_PGI_COMPLETE":[8],"INVOICES_CREATED_IN_SAP":[8],"ZERO_DOLLAR_INVOICES":[1],"SAP_DELIVERY_COUNT":[10],"ACUMAX_DELIVERY_COUNT":[9],"RELEASED_COUNT":[8],"PICK_COUNT":[8],"PGI_COUNT":[7],"TRUCK_CLOSURE_COUNT":[6],"DIFFERENCE":[3]})

def test_pipeline():
    df=prepare_data(sample()); out=filter_data(df,[date(2026,9,19)],[],[]); m=build_dashboard_metrics(out)
    assert m["sap"]==10 and m["pgi_rate"]==70 and m["difference"]==3
    assert build_dc_table(out).iloc[0]["DC"]=="8155"
