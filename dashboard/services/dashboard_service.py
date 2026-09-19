import pandas as pd
from dashboard.utils.formatters import percentage, total

TEXT_COLUMNS = {"dc", "dc_name", "date_pst", "national_chain", "national_chain_desc"}

def prepare_data(raw: pd.DataFrame) -> pd.DataFrame:
    data = raw.copy()
    data.columns = [str(c).lower() for c in data.columns]
    required = {"date_pst", "dc_name"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    data["date_pst"] = pd.to_datetime(data["date_pst"], errors="coerce").dt.date
    data = data.dropna(subset=["date_pst"])
    for column in data.columns:
        if column not in TEXT_COLUMNS:
            data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)
    return data

def filter_data(data, dates, dc_names, chains):
    filtered = data[data["date_pst"].isin(dates)].copy()
    if dc_names:
        filtered = filtered[filtered["dc_name"].isin(dc_names)]
    if chains:
        filtered = filtered[filtered["national_chain"].astype(str).isin(chains)]
    return filtered

def build_dashboard_metrics(filtered):
    m = {name: total(filtered, column) for name, column in {
        "sap":"sap_order", "received":"sap_received_lines", "confirmed":"sap_confirmed_lines",
        "rejected":"sap_rejected_line", "sap_del":"sap_delivery_count",
        "dlines":"sap_deliveries_pgi_complete", "invoices":"invoices_created_in_sap",
        "zero":"zero_dollar_invoices", "acx":"acumax_delivery_count", "released":"released_count",
        "picked":"pick_count", "pgi":"pgi_count", "truck":"truck_closure_count",
        "difference":"difference"}.items()}
    m["difference"] = abs(m["difference"])
    m.update(pgi_rate=percentage(m["pgi"],m["sap_del"]), truck_rate=percentage(m["truck"],m["sap_del"]),
             reject_rate=percentage(m["rejected"],m["received"]), zero_rate=percentage(m["zero"],m["invoices"]))
    return m

def build_trends(data, selected_date, dc_names, chains):
    trend = data.copy()
    if dc_names: trend = trend[trend["dc_name"].isin(dc_names)]
    if chains: trend = trend[trend["national_chain"].astype(str).isin(chains)]
    trend = trend[trend["date_pst"] <= selected_date].groupby("date_pst",as_index=False).sum(numeric_only=True).sort_values("date_pst").tail(14)
    deliveries = trend.get("sap_delivery_count", pd.Series(dtype=float))
    return {"sap":trend.get("sap_order",pd.Series(dtype=float)).tolist(),
            "deliveries":deliveries.tolist(),
            "pgi":[percentage(a,b) for a,b in zip(trend.get("pgi_count",[]),deliveries)],
            "truck":[percentage(a,b) for a,b in zip(trend.get("truck_closure_count",[]),deliveries)]}

def build_dc_table(filtered):
    dc=filtered.groupby(["dc","dc_name"],as_index=False).agg(SAP_Orders=("sap_order","sum"),SAP_Deliveries=("sap_delivery_count","sum"),Acumax_Deliveries=("acumax_delivery_count","sum"),Released=("released_count","sum"),Pick_Pack=("pick_count","sum"),PGI_Complete=("pgi_count","sum"),Truck_Closed=("truck_closure_count","sum"),Invoices=("invoices_created_in_sap","sum"),Difference=("difference","sum"))
    dc["PGI_Percent"]=dc.apply(lambda r:percentage(r["PGI_Complete"],r["SAP_Deliveries"]),axis=1)
    dc["Truck_Close_Percent"]=dc.apply(lambda r:percentage(r["Truck_Closed"],r["SAP_Deliveries"]),axis=1)
    dc["_abs"]=dc["Difference"].abs()
    return dc.sort_values(["_abs","SAP_Deliveries"],ascending=[False,False]).drop(columns="_abs").rename(columns={"dc":"DC","dc_name":"DC Name","SAP_Orders":"SAP Orders","SAP_Deliveries":"SAP Deliveries","Acumax_Deliveries":"Acumax Deliveries","Pick_Pack":"Pick Pack","PGI_Complete":"PGI Complete","Truck_Closed":"Truck Closed","PGI_Percent":"PGI %","Truck_Close_Percent":"Truck Close %"})
