import streamlit as st
from datetime import datetime, timedelta

# --- Helper Functions ---
def calculate_end_time(start_time_str, duration):
    """Calculates the end time based on start time and shift duration."""
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=duration)
    return end_dt.strftime("%I %p")

def get_dt(day_idx, time_str):
    """Converts a day index and time string into a datetime object for comparison."""
    base_date = datetime(2026, 3, 22) # Reference Sunday
    target_date = base_date + timedelta(days=day_idx)
    time_obj = datetime.strptime(time_str, "%I %p").time()
    return datetime.combine(target_date, time_obj)

# --- UI Styling (Dark Monochrome) ---
st.set_page_config(layout="wide", page_title="Swap Validator Pro")

st.markdown("""
    <style>
    .stApp { max-width: 1100px; margin: 0 auto; }
    
    /* Dark Dropdown Styling */
    div[data-baseweb="select"] > div {
        background-color: #1e2129 !important;
        color: white !important;
        border: 1px solid #3e4451 !important;
        border-radius: 8px !important;
    }

    /* Shift End Box (Dark Grey to match Start) */
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
    .week-label { text-align: center; font-weight: bold; margin-bottom: 10px; display: block; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🛡️ Swap Validation Tool</h1>", unsafe_allow_html=True)

# 1. RAMADAN TOGGLE: This changes 'duration' globally
is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9

day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)

# Data storage for validation
shift_data = {}

# --- Employee Columns ---
for i, col in enumerate([col1, col2], 1):
    with col:
        st.markdown(f"<h3 style='text-align: center;'>👤 Employee {i}</h3>", unsafe_allow_html=True)
        emp_name = st.text_input(f"E{i} Name", ["John", "Mike"][i-1], key=f"name_{i}", label_visibility="collapsed")
        
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
                    # 2. AUTOMATIC CALCULATION: Re-calculates every time 'duration' or 's_time' changes
                    e_time = calculate_end_time(s_time, duration)
                    st.markdown(f"<div class='dark-match-box'>{e_time}</div>", unsafe_allow_html=True)
                    
                    # Store data for the validation button
                    shift_data[f"e{i}_{week}_start"] = s_time
                    shift_data[f"e{i}_{week}_end"] = e_time
                
                st.write("Days Off:")
                d_col1, d_col2 = st.columns(2)
                d_col1.selectbox("Off 1", ["First Day off"] + day_list, key=f"d{i}a_{week}", label_visibility="collapsed")
                d_col2.selectbox("Off 2", ["Second Day off"] + day_list, key=f"d{i}b_{week}", label_visibility="collapsed")

st.divider()

# --- Validation Logic ---
if st.button("✅ Check the Validation", use_container_width=True):
    # Example: Check rest between Employee 1's end of Current Week and Start of Next Week
    # This logic can be expanded based on your specific company rules
    dt_end = get_dt(1, shift_data["e1_Current Week_end"])
    dt_start = get_dt(2, shift_data["e1_Next Week_start"])
    
    rest_hours = (dt_start - dt_end).total_seconds() / 3600
    
    if rest_hours >= 21:
        st.markdown(f"""
            <div class='status-container approved'>
                <h2 style='text-align: center;'>✅ Swap Approved</h2>
                <p style='text-align: center;'>Rest Period: {rest_hours:.1f} hours (Passes 21h rule)</p>
            </div>
        """, unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown(f"""
            <div class='status-container rejected'>
                <h2 style='text-align: center;'>❌ Swap Rejected</h2>
                <p style='text-align: center;'>Rest Period: {rest_hours:.1f} hours (Minimum 21h required)</p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br><center><b>Created by Abdelrahman heshmat @abheshma</b></center>", unsafe_allow_html=True)
