import streamlit as st
from datetime import datetime, timedelta

# --- Helper Functions ---
def calculate_end_time(start_time_str, duration):
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=duration)
    return end_dt.strftime("%I %p")

def get_dt(week_type, day_idx, time_str):
    base_date = datetime(2026, 3, 22) 
    offset = 0 if week_type == "Next Week" else 0
    target_date = base_date + timedelta(days=day_idx + offset)
    time_obj = datetime.strptime(time_str, "%I %p").time()
    return datetime.combine(target_date, time_obj)

# --- UI Styling ---
st.set_page_config(layout="wide", page_title="Swap Validator Pro")

st.markdown("""
    <style>
    .stApp { max-width: 1100px; margin: 0 auto; }
    div[data-baseweb="select"] > div {
        background-color: #1e2129 !important;
        color: white !important;
        border: 1px solid #3e4451 !important;
        border-radius: 8px !important;
    }
    .dark-match-box {
        background-color: #1e2129; 
        color: white;
        padding: 10px; 
        border-radius: 8px; 
        border: 1px solid #3e4451;
        text-align: center; 
        font-weight: bold; 
        font-size: 1.1rem;
        min-height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .status-container { padding: 25px; border-radius: 15px; margin-top: 20px; }
    .approved { background-color: #1b5e20; color: white; border: 2px solid #ffffff; }
    .rejected { background-color: #b71c1c; color: white; border: 2px solid #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🛡️ Swap Validation Tool</h1>", unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9

day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)

# --- Employee Columns ---
with col1:
    st.markdown("<h3 style='text-align: center;'>👤 Employee 1</h3>", unsafe_allow_html=True)
    name1 = st.text_input("E1 Name", "John", key="emp1_name", label_visibility="collapsed")
    
    # Week 1
    with st.container(border=True):
        st.markdown("<center><b>🗓️ Current Week</b></center>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,1,3])
        with c1:
            s1_curr = st.selectbox("Start", hours, index=9, key="s1_curr", label_visibility="collapsed")
        with c2: st.write("<br><center>to</center>", unsafe_allow_html=True)
        with c3:
            e1_curr = calculate_end_time(s1_curr, duration)
            st.markdown(f"<div class='dark-match-box'>{e1_curr}</div>", unsafe_allow_html=True)
    
    # Week 2
    with st.container(border=True):
        st.markdown("<center><b>🗓️ Next Week</b></center>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,1,3])
        with c1:
            s1_next = st.selectbox("Start", hours, index=9, key="s1_next", label_visibility="collapsed")
        with c2: st.write("<br><center>to</center>", unsafe_allow_html=True)
        with c3:
            e1_next = calculate_end_time(s1_next, duration)
            st.markdown(f"<div class='dark-match-box'>{e1_next}</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<h3 style='text-align: center;'>👤 Employee 2</h3>", unsafe_allow_html=True)
    name2 = st.text_input("E2 Name", "Mike", key="emp2_name", label_visibility="collapsed")
    
    # Week 1
    with st.container(border=True):
        st.markdown("<center><b>🗓️ Current Week</b></center>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,1,3])
        with c1:
            s2_curr = st.selectbox("Start", hours, index=14, key="s2_curr", label_visibility="collapsed")
        with c2: st.write("<br><center>to</center>", unsafe_allow_html=True)
        with c3:
            e2_curr = calculate_end_time(s2_curr, duration)
            st.markdown(f"<div class='dark-match-box'>{e2_curr}</div>", unsafe_allow_html=True)
    
    # Week 2
    with st.container(border=True):
        st.markdown("<center><b>🗓️ Next Week</b></center>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,1,3])
        with c1:
            s2_next = st.selectbox("Start", hours, index=14, key="s2_next", label_visibility="collapsed")
        with c2: st.write("<br><center>to</center>", unsafe_allow_html=True)
        with c3:
            e2_next = calculate_end_time(s2_next, duration)
            st.markdown(f"<div class='dark-match-box'>{e2_next}</div>", unsafe_allow_html=True)

st.divider()

# --- The Fix: Using the variables directly ---
if st.button("✅ Check the Validation", use_container_width=True):
    # Calculate rest between Employee 1's end and Employee 2's start
    dt1_end = get_dt("Current Week", 1, e1_curr)
    dt2_start = get_dt("Current Week", 2, s2_curr)
    rest_hours = (dt2_start - dt1_end).total_seconds() / 3600
    
    if rest_hours >= 21:
        st.markdown(f"<div class='status-container approved'><h2 style='text-align: center;'>✅ Swap Approved</h2><p style='text-align: center;'>Rest: {rest_hours:.1f} hours</p></div>", unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown(f"<div class='status-container rejected'><h2 style='text-align: center;'>❌ Swap Rejected</h2><p style='text-align: center;'>Rest: {rest_hours:.1f} hours (Required: 21h)</p></div>", unsafe_allow_html=True)

st.markdown("<br><center><b>Created by Abdelrahman heshmat @abheshma</b></center>", unsafe_allow_html=True)
