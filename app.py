import streamlit as st
from datetime import datetime, timedelta

# --- Helper Functions ---
def calculate_end_time(start_time_str, duration):
    """Calculates end time based on start and duration."""
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=duration)
    return end_dt.strftime("%I %p")

def get_dt(day_idx, time_str):
    """Reference date for shift validation logic."""
    base_date = datetime(2026, 3, 22) 
    target_date = base_date + timedelta(days=day_idx)
    time_obj = datetime.strptime(time_str, "%I %p").time()
    return datetime.combine(target_date, time_obj)

# --- UI Styling & Dark Mode Force ---
# Setting layout to wide and providing a page title
st.set_page_config(
    layout="wide", 
    page_title="Swap Validator Pro",
    initial_sidebar_state="collapsed"
)

# Custom CSS to force dark theme colors and center-aligned inputs
st.markdown("""
    <style>
    /* Force dark background for the whole app */
    .stApp { 
        background-color: #0e1117; 
        color: #ffffff;
        max-width: 1100px; 
        margin: 0 auto; 
    }
    
    /* Centered Name Input with dark background */
    input[type="text"] {
        text-align: center !important;
        background-color: #1e2129 !important;
        color: white !important;
        border: 1px solid #3e4451 !important;
        border-radius: 8px !important;
    }

    /* Styling Selectboxes to match the dark theme */
    div[data-baseweb="select"] > div {
        background-color: #1e2129 !important;
        color: white !important;
        border: 1px solid #3e4451 !important;
        border-radius: 8px !important;
    }

    /* Shift End Box styling */
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

    /* Status containers for validation results */
    .status-container { padding: 25px; border-radius: 15px; margin-top: 20px; text-align: center; }
    .approved { background-color: #1b5e20; color: white; border: 2px solid #ffffff; }
    .rejected { background-color: #b71c1c; color: white; border: 2px solid #ffffff; }
    .reason-text { font-size: 1.1rem; margin-top: 10px; font-weight: normal; opacity: 0.9; }
    .week-label { text-align: center; font-weight: bold; margin-bottom: 10px; display: block; }
    
    /* Ensuring checkbox text is visible in dark mode */
    .stCheckbox { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Swap Validation Tool</h1>", unsafe_allow_html=True)

# Ramadan Shift Toggle
is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9

day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)
shift_data = {}

# --- Employee Sections ---
for i, col in enumerate([col1, col2], 1):
    with col:
        st.markdown(f"<h3 style='text-align: center;'>👤 Employee {i}</h3>", unsafe_allow_html=True)
        st.text_input(
            label=f"E{i} Name", 
            placeholder="Enter your Name here", 
            key=f"name_input_{i}", 
            label_visibility="collapsed"
        )
        
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
                    st.markdown(f"<div class='dark-match-box'>{e_time}</div>", unsafe_allow_html=True)
                    shift_data[f"e{i}_{week}_end"] = e_time
                    shift_data[f"
