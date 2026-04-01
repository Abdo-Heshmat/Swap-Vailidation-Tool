import streamlit as st
from datetime import datetime, timedelta

# --- Helper Functions ---
def calculate_end_time(start_time_str, duration):
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=duration)
    return end_dt.strftime("%I %p")

def get_dt(week_type, day_idx, time_str):
    # Reference Sunday for calculation
    base_date = datetime(2026, 3, 22) 
    offset = 0 if week_type == "Current Week" else 7
    target_date = base_date + timedelta(days=day_idx + offset)
    time_obj = datetime.strptime(time_str, "%I %p").time()
    return datetime.combine(target_date, time_obj)

# --- UI Styling (Dark Monochrome Theme) ---
st.set_page_config(layout="wide", page_title="Swap Validator Pro")

st.markdown("""
    <style>
    /* Centering the main app container */
    .stApp { max-width: 1100px; margin: 0 auto; }
    
    /* Styling for the Start Dropdown (Dark Grey) */
    div[data-baseweb="select"] > div {
        background-color: #1e2129 !important;
        color: white !important;
        border: 1px solid #3e4451 !important;
        border-radius: 8px !important;
        height: 45px !important;
    }

    /* Styling for the Shift End Box (Matching the Start box) */
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

    /* Validation Results Styling */
    .status-container { padding: 25px; border-radius: 15px; margin-top: 20px; }
    .approved { background-color: #1b5e20; color: white; border: 2px solid #ffffff; }
    .rejected { background-color: #b71c1c; color: white; border: 2px solid #ffffff; }
    
    /* Center text specifically for week headers */
    .week-label { text-align: center; font-weight: bold; margin-bottom: 10px; display: block; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🛡️ Swap Validation Tool</h1>", unsafe_allow_html=True)

# Ramadan Shift Toggle
is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9

day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)

# --- Employee 1 & 2 Columns ---
for i, col in enumerate([col1, col2], 1):
    with col:
        st.markdown(f"<h3 style='text-align: center;'>👤 Employee {i}</h3>", unsafe_allow_html=True)
        name = st.text_input(f"E{i} Name", ["John", "Mike"][i-1], key=f"n{i}", label_visibility="collapsed")
        
        for week in ["Current Week", "Next Week"]:
            with st.container(border=True):
                st.markdown(f"<span class='week-label'>🗓️ {week}</span>", unsafe_allow_html=True)
                
                t_col1, t_col2, t_col3 = st.columns([3, 1, 3])
                
                with t_col1:
                    st.write("Start")
                    s_time = st.selectbox("Start", hours, index=9 if i==1 else 14, key=f"s{i}_{week}", label_visibility="collapsed")
                
                with t_col2:
                    st.write("<br><center>to</center>", unsafe_allow_html=True)
                
                with t_col3:
                    st.write("Shift End")
                    e_time = calculate_end_time(s_time, duration)
                    # Now styled as a dark box to match the start input
                    st.markdown(f"<div class='dark-match-box'>{e_time}</div>", unsafe_allow_html=True)
                
                st.write("Days Off:")
                d_col1, d_col2 = st.columns(2)
                d_col1.selectbox("Off 1", ["First Day off"] + day_list, key=f"d{i}a_{week}", label_visibility="collapsed")
                d_col2.selectbox("Off 2", ["Second Day off"] + day_list, key=f"d{i}b_{week}", label_visibility="collapsed")

st.divider()

if st.button("✅ Check the Validation", use_container_width=True):
    # Calculation Logic
    dt1_end = get_dt("Current Week", 1, calculate_end_time(st.session_state.s1_Current_Week, duration))
    dt2_start = get_dt("Current Week", 2, st.session_state.s2_Current_Week)
    rest_hours = (dt2_start - dt1_end).total_seconds() / 3600
    
    if rest_hours >= 21:
        st.markdown(f"<div class='status-container approved'><h2 style='text-align: center;'>✅ Swap Approved</h2><p style='text-align: center;'>Rest Period: {rest_hours:.1f} hours</p></div>", unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown(f"<div class='status-container rejected'><h2 style='text-align: center;'>❌ Swap Rejected</h2><p style='text-align: center;'>Rest Period: {rest_hours:.1f} hours (Minimum 21h required)</p></div>", unsafe_allow_html=True)

st.markdown("<br><center><b>Created by Abdelrahman heshmat @abheshma</b></center>", unsafe_allow_html=True)
