import streamlit as st
import pandas as pd
import time
import sys
import os
import datetime

# Add parent dir to path to import db_manager
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from email_shield.db_manager import DBManager
from streamlit_autorefresh import st_autorefresh

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

# --- AUTO-REFRESH ---
# refresh options in milliseconds
refresh_intervals = {
    "1 Minute": 60 * 1000,
    "5 Minutes": 5 * 60 * 1000,
    "10 Minutes": 10 * 60 * 1000,
    "30 Minutes": 30 * 60 * 1000,
    "1 Hour": 60 * 60 * 1000,
    "Off": 0
}

r_col1, r_col2 = st.columns([1, 3])

with r_col1:
    if st.button('🔄 Refresh Data'):
        st.rerun()

with r_col2:
    selected_interval = st.selectbox(
        "Auto-Refresh",
        options=list(refresh_intervals.keys()),
        index=0,  # Default to 1 Minute
        help="Select auto-refresh interval"
    )

interval_ms = refresh_intervals[selected_interval]

if interval_ms > 0:
    st_autorefresh(interval=interval_ms, key="dashboard_refresh")

# --- LOAD DATA ---
df = db.get_all_logs()

if df.empty:
    st.warning("No data found. Please run the Gateway and Traffic Generator to populate logs.")
    st.stop()

# Convert timestamp to datetime immediately for calculations
df['timestamp'] = pd.to_datetime(df['timestamp'])

# --- HELPER: TREND CALCULATION ---
def calculate_trend(df, verdict=None):
    """Calculates % change compared to the previous hour."""
    now = datetime.datetime.now()
    one_hour = datetime.timedelta(hours=1)
    
    # Time Windows
    curr_start = now - one_hour
    prev_start = now - (one_hour * 2)
    
    # Slices
    curr_df = df[df['timestamp'] >= curr_start]
    prev_df = df[(df['timestamp'] >= prev_start) & (df['timestamp'] < curr_start)]
    
    # Verdict Filtering
    if verdict:
        curr_count = len(curr_df[curr_df['verdict'] == verdict])
        prev_count = len(prev_df[prev_df['verdict'] == verdict])
    else:
        curr_count = len(curr_df)
        prev_count = len(prev_df)
        
    if prev_count == 0:
        return 0.0 # No history to compare
        
    delta = ((curr_count - prev_count) / prev_count) * 100
    return delta

# --- METRICS ROW ---
col1, col2, col3, col4, col5 = st.columns(5)

# Calculate Counts (Totals)
total_emails = len(df)
total_phishing = len(df[df['verdict'] == 'PHISHING'])
total_malware = len(df[df['verdict'] == 'MALWARE'])
total_safe = len(df[df['verdict'] == 'SAFE'])

# Calculate Trends (vs Last Hour)
trend_traffic = calculate_trend(df)
trend_phishing = calculate_trend(df, 'PHISHING')
trend_malware = calculate_trend(df, 'MALWARE')
trend_safe = calculate_trend(df, 'SAFE')

col1.metric("Total Traffic", f"{total_emails}", f"{trend_traffic:.1f}% (1h)")
col2.metric("Phishing", f"{total_phishing}", f"{trend_phishing:.1f}% (1h)", delta_color="inverse")
col3.metric("Malware Blocked", f"{total_malware}", f"{trend_malware:.1f}% (1h)", delta_color="inverse")
col4.metric("Safe Emails", f"{total_safe}", f"{trend_safe:.1f}% (1h)")
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
        # Default Logic: Try 'debug@test.com', else first user
        default_index = 0
        if "debug@test.com" in user_list:
            default_index = list(user_list).index("debug@test.com")

        # Selectbox (matches Forensics filter style)
        # st.selectbox supports typing to search, covering the scalability requirement.
        target_user = st.selectbox("Select User", user_list, index=default_index)
                
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

# Convert timestamp to datetime if not already (Moved to top)
# df['timestamp'] = pd.to_datetime(df['timestamp'])

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
