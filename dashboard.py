import streamlit as st
import pandas as pd
import time
import sys
import os

# Add parent dir to path to import db_manager
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from email_shield.db_manager import DBManager

st.set_page_config(
    page_title="🛡️ Shield Analytics",
    page_icon="🛡️",
    layout="wide"
)

# Initialize DB
db = DBManager()

# --- HEADER ---
st.title("🛡️ Enterprise Security Dashboard")
st.markdown("Real-time monitoring of Email Phishing Threats.")

# --- AUTO-REFRESH BUTTON ---
if st.button('🔄 Refresh Data'):
    st.rerun()

# --- LOAD DATA ---
df = db.get_all_logs()

if df.empty:
    st.warning("No data found. Please run the Gateway and Traffic Generator to populate logs.")
    st.stop()

# --- METRICS ROW ---
col1, col2, col3, col4 = st.columns(4)
total_emails = len(df)
total_phishing = len(df[df['verdict'] == 'PHISHING'])
total_safe = len(df[df['verdict'] == 'SAFE'])
phishing_rate = (total_phishing / total_emails) * 100 if total_emails > 0 else 0

col1.metric("Total Traffic", f"{total_emails}", "+12%")
col2.metric("Phishing Attacks", f"{total_phishing}", f"{phishing_rate:.1f}% Rate", delta_color="inverse")
col3.metric("Safe Emails", f"{total_safe}")
col4.metric("Active Users", f"{df['user_email'].nunique()}")

st.divider()

import altair as alt

# --- CHARTS ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("Traffic Composition")
    verdict_counts = df['verdict'].value_counts().reset_index()
    verdict_counts.columns = ['Verdict', 'Count']
    
    chart = alt.Chart(verdict_counts).mark_bar().encode(
        x='Verdict',
        y='Count',
        color=alt.Color('Verdict', scale=alt.Scale(domain=['SAFE', 'PHISHING'], range=['#00CC96', '#FF4B4B']))
    )
    st.altair_chart(chart, use_container_width=True)

with c2:
    st.subheader("Top Targeted Users")
    user_counts = df[df['verdict'] == 'PHISHING']['user_email'].value_counts().head(5)
    st.bar_chart(user_counts)

# --- USER FORENSICS ---
st.divider()
st.subheader("🕵️ User Forensics")

users = ["All"] + list(df['user_email'].unique())
selected_user = st.selectbox("Select User to Audit:", users)

if selected_user != "All":
    filtered_df = df[df['user_email'] == selected_user]
else:
    filtered_df = df

# styling the table
st.dataframe(
    filtered_df[['timestamp', 'user_email', 'verdict', 'url_detected']],
    use_container_width=True,
    hide_index=True,
    column_config={
        "verdict": st.column_config.TextColumn(
            "Verdict",
            help="AI Decision",
        ),
        "url_detected": "Malicious Link (If Any)"
    }
)
