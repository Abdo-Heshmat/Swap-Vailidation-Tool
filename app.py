import streamlit as st
from datetime import datetime, timedelta

# --- Helper Functions ---
def calculate_end_time(start_time_str, duration):
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=duration)
    return end_dt.strftime("%I %p")

def get_dt(day_idx, time_str):
    # Reference Sunday: March 22, 2026
    base_date = datetime(2026, 3, 22) 
    target_date = base_date + timedelta(days=day_idx)
    time_obj = datetime.strptime(time_str, "%I %p").time()
    return datetime.combine(target_date, time_obj)

# --- UI Styling & Forced Dark Mode ---
st.set_page_config(layout="wide", page_title="Swap Validator Pro")

st.markdown("""
    <style>
    .stApp { 
        background-color: #0e1117; 
        color: #ffffff;
        max-width: 1100px; 
        margin: 0 auto; 
    }
    input[type="text"] {
        text-align: center !important;
        background-color: #1e2129 !important;
        color: white !important;
        border: 1px solid #3e4451 !important;
        border-radius: 8px !important;
    }
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
    .status-container { padding: 20px; border-radius: 12px; margin-top: 15px; }
    .approved { background-color: #1b5e20; color: white; border: 2px solid #ffffff; }
    .rejected { background-color: #b71c1c; color: white; border: 2px solid #ffffff; }
    .emp-header { font-weight: bold; font-size: 1.2rem; margin-top: 10px; text-decoration: underline; }
    .reason-item { margin-left: 20px; font-size: 1rem; list-style-type: disc; }
    .week-label { text-align: center; font-weight: bold; margin-bottom: 10px; display: block; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Swap Validation Tool</h1>", unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9

day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)
shift_data = {}
days_off_data = {}

# --- Employee Sections ---
for i, col in enumerate([col1, col2], 1):
    with col:
        st.markdown(f"<h3 style='text-align: center;'>👤 Employee {i}</h3>", unsafe_allow_html=True)
        st.text_input(placeholder="Enter your Name here", key=f"name_{i}", label="Name", label_visibility="collapsed")
        
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
                    shift_data[f"e{i}_{week}_start"] = s_time

                st.write("Days Off:")
                d_col1, d_col2 = st.columns(2)
                off1 = d_col1.selectbox("Off 1", ["First Day off"] + day_list, key=f"d{i}a_{week}", label_visibility="collapsed")
                off2 = d_col2.selectbox("Off 2", ["Second Day off"] + day_list, key=f"d{i}b_{week}", label_visibility="collapsed")
                
                off_count = 0
                if off1 != "First Day off": off_count += 1
                if off2 != "Second Day off": off_count += 1
                days_off_data[f"e{i}_{week}_offcount"] = off_count

st.divider()

if st.button("✅ Check the Validation", use_container_width=True):
    results = []
    
    for i in [1, 2]:
        name = st.session_state[f"name_{i}"] if st.session_state[f"name_{i}"] else f"Employee {i}"
        reasons = []
        
        # --- THE 12H REST RULE ---
        # Comparing the end of the last day of 'Current Week' (Day 0) 
        # to the start of the first day of 'Next Week' (Day 1)
        dt_old_end = get_dt(0, shift_data[f"e{i}_Current Week_end"])
        dt_new_start = get_dt(1, shift_data[f"e{i}_Next Week_start"])
        rest = (dt_new_start - dt_old_end).total_seconds() / 3600
        
        if rest < 12:
            reasons.append(f"Gap between old and new shift is only **{rest:.1f}h** (Must be 12h+).")
            
        # --- THE 6-DAY RULE ---
        curr_work = 7 - days_off_data[f"e{i}_Current Week_offcount"]
        next_work = 7 - days_off_data[f"e{i}_Next Week_offcount"]
        
        if curr_work > 6:
            reasons.append(f"Current Week: Working **{curr_work} days** (Max 6).")
        if next_work > 6:
            reasons.append(f"Next Week: Working **{next_work} days** (Max 6).")
            
        results.append({"name": name, "reasons": reasons})

    all_clear = all(len(r["reasons"]) == 0 for r in results)
    
    if all_clear:
        st.markdown("<div class='status-container approved'><h2>✅ Swap Approved</h2><p>All rest periods are 12 hours or more.</p></div>", unsafe_allow_html=True)
        st.balloons()
    else:
        html_output = "<div class='status-container rejected'><h2>❌ Swap Rejected</h2>"
        for res in results:
            if res["reasons"]:
                html_output += f"<div class='emp-header'>{res['name']}</div>"
                for reason in res["reasons"]:
                    html_output += f"<div class='reason-item'>{reason}</div>"
            else:
                html_output += f"<div class='emp-header' style='color: #a5d6a7;'>{res['name']}: No issues</div>"
        html_output += "</div>"
        st.markdown(html_output, unsafe_allow_html=True)

st.markdown("<br><center><b>Created by Abdelrahman heshmat @abheshma</b></center>", unsafe_allow_html=True)
