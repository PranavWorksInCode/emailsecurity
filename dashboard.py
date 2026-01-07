import streamlit as st
import pandas as pd
import time
import sys
import os
import datetime

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

# Display System Time for debugging/verification
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.caption(f"🕒 System Time: **{current_time}** (Local Machine Time)")

# --- AUTO-REFRESH BUTTON ---
if st.button('🔄 Refresh Data'):
    st.rerun()

# --- LOAD DATA ---
df = db.get_all_logs()

if df.empty:
    st.warning("No data found. Please run the Gateway and Traffic Generator to populate logs.")
    st.stop()

# --- METRICS ROW ---
col1, col2, col3, col4, col5 = st.columns(5)
total_emails = len(df)
total_phishing = len(df[df['verdict'] == 'PHISHING'])
total_malware = len(df[df['verdict'] == 'MALWARE'])
total_safe = len(df[df['verdict'] == 'SAFE'])
phishing_rate = ((total_phishing + total_malware) / total_emails) * 100 if total_emails > 0 else 0

col1.metric("Total Traffic", f"{total_emails}", "+12%")
col2.metric("Phishing", f"{total_phishing}", delta_color="inverse")
col3.metric("Malware Blocked", f"{total_malware}", delta_color="inverse")
col4.metric("Safe Emails", f"{total_safe}")
col5.metric("Active Users", f"{df['user_email'].nunique()}")

st.divider()

import altair as alt

# --- CHARTS ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("Traffic Composition")
    verdict_counts = df['verdict'].value_counts().reset_index()
    verdict_counts.columns = ['Verdict', 'Count']
    
    chart = alt.Chart(verdict_counts).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color('Verdict', scale=alt.Scale(domain=['SAFE', 'PHISHING', 'MALWARE'], range=['#00CC96', '#FF4B4B', '#8000FF'])),
        tooltip=['Verdict', 'Count']
    )
    st.altair_chart(chart, use_container_width=True)

with c2:
    st.subheader("User Specific Analysis")
    
    # Get list of users
    user_list = df['user_email'].unique()
    
    if len(user_list) > 0:
        # Search Input
        search_query = st.text_input("Search User by Email", placeholder="e.g. alice@company.com")
        
        # Default Logic: Try 'debug@test.com', else first user
        target_user = "debug@test.com"
        if target_user not in user_list:
            target_user = user_list[0]

        # Search Logic (Overrides Default)
        if search_query:
            # Case-insensitive partial match
            matches = [u for u in user_list if search_query.lower() in u.lower()]
            
            if len(matches) == 1:
                target_user = matches[0]
            elif len(matches) > 1:
                st.warning(f"Multiple users found: {', '.join(matches[:3])}... Showing match: {matches[0]}")
                target_user = matches[0]
            else:
                st.warning("No matching user found. Showing default.")
                
        if target_user:
            st.success(f"Showing analysis for: **{target_user}**")
            # Filter data for this user
            user_subset = df[df['user_email'] == target_user]
            user_counts = user_subset['verdict'].value_counts().reset_index()
            user_counts.columns = ['Verdict', 'Count']
            
            # Dynamic Pie Chart
            user_chart = alt.Chart(user_counts).mark_arc(innerRadius=40).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color('Verdict', scale=alt.Scale(domain=['SAFE', 'PHISHING', 'MALWARE'], range=['#00CC96', '#FF4B4B', '#8000FF'])),
                tooltip=['Verdict', 'Count']
            )
            st.altair_chart(user_chart, use_container_width=True)
            
            # Show mini stat
            phish_count = len(user_subset[user_subset['verdict'] == 'PHISHING'])
            st.caption(f"{target_user} has encountered {phish_count} phishing attempts.")
    else:
        st.info("No user data available yet.")

# --- TIME FILTER ---
st.divider()
st.subheader("🔍 Forensics Filters")

# Convert timestamp to datetime if not already
df['timestamp'] = pd.to_datetime(df['timestamp'])

c_time, c_user = st.columns([2, 1])

with c_time:
    time_option = st.radio(
        "Time Range", 
        ["All Time", "Last Hour", "Last 24 Hours", "Last 7 Days", "Custom Range"], 
        horizontal=True
    )

    if time_option == "Custom Range":
        # Default to today
        today = datetime.datetime.now()
        start_date = st.date_input("Start Date", today)
        end_date = st.date_input("End Date", today)
        
        # Filter (Whole days)
        # Combine date with min/max time for inclusive filtering
        start_dt = datetime.datetime.combine(start_date, datetime.time.min)
        end_dt = datetime.datetime.combine(end_date, datetime.time.max)
        
        filtered_df = df[(df['timestamp'] >= start_dt) & (df['timestamp'] <= end_dt)]
        
    elif time_option == "Last Hour":
        cutoff = datetime.datetime.now() - datetime.timedelta(hours=1)
        filtered_df = df[df['timestamp'] >= cutoff]
        
    elif time_option == "Last 24 Hours":
        cutoff = datetime.datetime.now() - datetime.timedelta(hours=24)
        filtered_df = df[df['timestamp'] >= cutoff]
        
    elif time_option == "Last 7 Days":
        cutoff = datetime.datetime.now() - datetime.timedelta(days=7)
        filtered_df = df[df['timestamp'] >= cutoff]
        
    else: # All Time
        filtered_df = df

with c_user:
    users = ["All"] + list(df['user_email'].unique())
    selected_user = st.selectbox("Filter by User", users)

if selected_user != "All":
    filtered_df = filtered_df[filtered_df['user_email'] == selected_user]

# Filter by Search Term
search_term = st.text_input("🔍 Search Logs", placeholder="Type to search by email, verdict, or URL...")

if search_term:
    # Filter if any string column contains the search term (case-insensitive)
    filtered_df = filtered_df[
        filtered_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
    ]

# styling the table
# styling the table
# Format timestamp as string to ensure it matches System Time exactly
filtered_df['timestamp_str'] = filtered_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Reorder mechanism
cols = ['id', 'timestamp_str', 'sender_email', 'user_email', 'verdict', 'url_detected']
st.dataframe(
    filtered_df[cols],
    use_container_width=True,
    hide_index=True,
    column_config={
        "id": st.column_config.NumberColumn(
            "Scan ID",
            help="Unique Database ID",
            format="%d"
        ),
        "timestamp_str": st.column_config.TextColumn(
            "Time (Local)",
            help="Time of scan"
        ),
        "sender_email": "Source",
        "user_email": "Target",
        "verdict": st.column_config.TextColumn(
            "Verdict",
            help="AI Decision",
        ),
        "url_detected": "Threat Artifact"
    }
)
