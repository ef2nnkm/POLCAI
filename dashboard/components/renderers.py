from datetime import datetime
import html
import pandas as pd
import streamlit as st
from dashboard.utils.formatters import format_number

def load_css(path="assets/styles/dashboard.css"):
    with open(path,encoding="utf-8") as f: st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)

def sparkline(values):
    values=[float(v) for v in values if not pd.isna(v)] or [0.0]
    if len(values)==1: values*=2
    w,h,p=92,28,2; lo,hi=min(values),max(values); span=hi-lo or 1.0
    pts=[f"{p+i*(w-2*p)/(len(values)-1):.1f},{h-p-((v-lo)/span)*(h-2*p):.1f}" for i,v in enumerate(values)]
    line=" ".join(pts); area=f"{p},{h-p} {line} {w-p},{h-p}"
    return f"<svg class='sparkline' viewBox='0 0 {w} {h}'><polygon class='area' points='{area}'/><polyline class='line' points='{line}'/></svg>"

def render_header():
    stamp=datetime.now().astimezone().strftime("%m-%d-%Y %H:%M:%S %Z")
    st.markdown(f"<div class='topbar'><div class='brand'>McKESSON</div><div class='title'><span class='title-icon'>▱</span><span>End-to-End Order Processing Dashboard</span></div><div class='header-meta'><div class='refresh'>REPORT REFRESHED<br>{stamp}</div><div class='filter-hint'>FILTERS ▾</div></div></div>",unsafe_allow_html=True)

def render_filters(data, dates):
    _,fc=st.columns([8.5,1.5])
    with fc:
        with st.popover("▽ Filters",use_container_width=True):
            st.multiselect("SAP Order Date",dates,key="date_filter",format_func=lambda d:d.strftime("%Y-%m-%d"))
            st.multiselect("DC Name",sorted(data["dc_name"].dropna().astype(str).unique()),key="dc_filter",placeholder="All")
            st.multiselect("National Chain",sorted(data["national_chain"].dropna().astype(str).unique()),key="chain_filter",placeholder="All")
            if st.button("Refresh Data",use_container_width=True): st.cache_data.clear(); st.rerun()

def render_kpi(icon,label,value,note,trend_values,status="info"):
    st.markdown(f"<div class='kpi-card {status}'><div class='kpi-head'><div class='kpi-icon'>{html.escape(str(icon))}</div><div class='kpi-content'><div class='kpi-label'>{html.escape(str(label))}</div><div class='kpi-value'>{html.escape(str(value))}</div></div></div><div class='kpi-footer'><span>{html.escape(str(note))}</span>{sparkline(trend_values)}</div></div>",unsafe_allow_html=True)

def render_flow_panel(title,steps):
    out=f"<div class='panel'><div class='section-title'>{html.escape(title)}</div><div class='flow-wrap'>"
    for icon,label,value,note,colour in steps:
        out+=f"<div class='step {colour}'><div class='step-icon'>{html.escape(str(icon))}</div><div class='step-label'>{html.escape(str(label))}</div><div class='step-value'>{format_number(value)}</div><div class='step-note'>{html.escape(str(note))}</div></div>"
    st.markdown(out+"</div></div>",unsafe_allow_html=True)

def render_connector():
    st.markdown("<div class='sap-acumax-connector'><div class='sap-acumax-line'></div><div class='sap-acumax-label'>SAP → ACUMAX FEED</div><div class='sap-acumax-arrow'>▼</div></div>",unsafe_allow_html=True)

def render_dc_table(dc):
    st.markdown("<div class='panel'><div class='mck-table-title'><div class='section-title'>DISTRIBUTION CENTRE PERFORMANCE - DETAIL</div><div class='mck-table-note'>Sorted by largest absolute difference</div></div>",unsafe_allow_html=True)
    numeric={c:st.column_config.NumberColumn(format="%,.0f") for c in ["SAP Orders","SAP Deliveries","Acumax Deliveries","Released","Pick Pack","PGI Complete","Truck Closed","Invoices","Difference"]}
    numeric.update({"PGI %":st.column_config.ProgressColumn(min_value=0,max_value=100,format="%.1f%%"),"Truck Close %":st.column_config.ProgressColumn(min_value=0,max_value=100,format="%.1f%%")})
    st.dataframe(dc,use_container_width=True,hide_index=True,height=410,row_height=44,column_config=numeric)
    st.markdown("</div><div class='note'>ⓘ Dashboard data is sourced only from the configured PostgreSQL reporting tables.</div>",unsafe_allow_html=True)
