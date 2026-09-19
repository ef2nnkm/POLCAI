import streamlit as st
from dashboard.components.renderers import load_css, render_header, render_filters, render_kpi, render_flow_panel, render_connector, render_dc_table
from dashboard.repositories.dashboard_repository import load_dashboard_data
from dashboard.services.dashboard_service import prepare_data, filter_data, build_dashboard_metrics, build_trends, build_dc_table
from dashboard.utils.formatters import format_number

st.set_page_config(page_title="End-to-End Order Processing Dashboard",page_icon="📊",layout="wide",initial_sidebar_state="collapsed")
load_css()
try: df=prepare_data(load_dashboard_data())
except Exception as exc: st.error("Unable to read PostgreSQL data."); st.code(str(exc)); st.stop()
if df.empty: st.warning("No valid dashboard data is available."); st.stop()
dates=sorted(df["date_pst"].unique().tolist(),reverse=True)
for key,value in [("date_filter",[dates[0]]),("dc_filter",[]),("chain_filter",[])]:
    if key not in st.session_state: st.session_state[key]=value
render_header(); render_filters(df,dates)
selected_dates=st.session_state.date_filter or [dates[0]]
filtered=filter_data(df,selected_dates,st.session_state.dc_filter,st.session_state.chain_filter)
if filtered.empty: st.warning("No data is available for the selected filters."); st.stop()
m=build_dashboard_metrics(filtered); trends=build_trends(df,max(selected_dates),st.session_state.dc_filter,st.session_state.chain_filter)
cols=st.columns(4,gap="medium")
with cols[0]: render_kpi("▤","TOTAL SAP ORDERS",format_number(m["sap"]),f"{len(selected_dates)} date(s) selected",trends["sap"])
with cols[1]: render_kpi("▱","TOTAL DELIVERIES",format_number(m["sap_del"]),f"{format_number(m['acx'])} Acumax deliveries",trends["deliveries"])
with cols[2]: render_kpi("✓","PGI COMPLETE (%)",f"{m['pgi_rate']:.1f}%","Recent completion trend",trends["pgi"],"success")
with cols[3]: render_kpi("⌁","TRUCK CLOSURE (%)",f"{m['truck_rate']:.1f}%","Recent closure trend",trends["truck"],"success")
render_flow_panel("ORDER-TO-CASH PROCESS FLOW",[("☷","SAP Orders",m["sap"],"",""),("☷","Received Lines",m["received"],"",""),("✓","Confirmed Lines",m["confirmed"],"","green"),("×","Rejected Lines",m["rejected"],f"{m['reject_rate']:.1f}% of Received","danger"),("🚚","Deliveries",m["sap_del"],"",""),("☷","Delivery Lines",m["dlines"],"",""),("✓","PGI Complete",m["pgi"],f"{m['pgi_rate']:.1f}%","green"),("🚛","Truck Closure Complete",m["truck"],f"{m['truck_rate']:.1f}%","green"),("$","Invoice Created",m["invoices"],"",""),("$","Zero $ Invoices",m["zero"],f"{m['zero_rate']:.1f}% of Invoices","warning")])
render_connector()
render_flow_panel("ACUMAX DISTRIBUTION",[("🚚","Deliveries",m["acx"],"",""),("🧾","Released",m["released"],"",""),("📦","Pick Pack",m["picked"],"",""),("✓","PGI Complete",m["pgi"],"","green"),("🚛","Truck Close",m["truck"],"","green"),("!","Deliveries To Truck Close",m["difference"],"Requires follow-up","warning")])
render_dc_table(build_dc_table(filtered))
