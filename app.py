import streamlit as st
from datetime import datetime, timedelta

# --- Core Logic Functions ---
def calculate_end_time(start_time_str, duration):
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=duration)
    return end_dt.strftime("%I %p")

def get_dt(day_idx, time_str, is_end_time=False, start_time_str=None):
    # Reference: Day 7 is Saturday, Day 8 is Sunday
    base_date = datetime(2026, 3, 22) 
    target_date = base_date + timedelta(days=day_idx-1)
    
    # MIDNIGHT CROSSING LOGIC:
    # If a shift starts at 5 PM and ends at 2 AM, it technically ends the NEXT day.
    if is_end_time and start_time_str:
        s_hour = datetime.strptime(start_time_str, "%I %p").hour
        e_hour = datetime.strptime(time_str, "%I %p").hour
        if e_hour < s_hour:
            target_date += timedelta(days=1)
            
    time_obj = datetime.strptime(time_str, "%I %p").time()
    return datetime.combine(target_date, time_obj)

# --- UI Styling ---
st.set_page_config(layout="wide", page_title="Swap Validator Pro")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; max-width: 1100px; margin: 0 auto; }
    .rules-box { background-color: #1e2129; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; }
    .exemption-box { background-color: #332b00; padding: 10px; border-radius: 5px; border: 1px solid #ffcc00; margin-top: 10px; font-size: 0.95rem; }
    .dark-match-box { background-color: #1e2129; color: #00ff00; padding: 10px; border-radius: 8px; border: 1px solid #3e4451; text-align: center; font-weight: bold; }
    .status-container { padding: 20px; border-radius: 12px; margin-top: 15px; text-align: center; }
    .approved { background-color: #1b5e20; border: 2px solid #ffffff; }
    .rejected { background-color: #b71c1c; border: 2px solid #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🔄 Professional Swap Validator</h1>", unsafe_allow_html=True)

# --- Enhanced Rules Section ---
with st.expander("📋 View Validation Rules & Detailed Logic", expanded=False):
    st.markdown("""
    <div class='rules-box'>
        <b>🛠️ How Validation Works:</b><br>
        1. <b>The 12h Rest Rule:</b> We calculate the gap between the <i>Last Shift</i> of the current week and the <i>First Shift</i> of the new week.<br>
        2. <b>The Midnight Crossing:</b> If a shift starts in the PM and ends in the AM (e.g., 5 PM - 2 AM), the tool automatically adds +1 day to the end time to ensure rest is calculated correctly.<br>
        3. <b>The 6-Day Rule:</b> No employee can work more than 6 days in a single week.<br>
        <div class='exemption-box'>
            <b>⚠️ Special Exemptions:</b><br>
            • If you are <b>Off on Saturday</b> (Current Week), the 12h rest rule is ignored.<br>
            • If you are <b>Off on Sunday</b> (Next Week), the 12h rest rule is ignored.<br>
            <i>Note: Even if one rule is waived, the 6-day work rule must still be passed!</i>
        </div>
    </div>
    """, unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9
day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)
shift_starts, shift_ends, off_days = {}, {}, {}

for i, col in enumerate([col1, col2], 1):
    with col:
        st.markdown(f"### 👤 Employee {i}")
        # Fixed the TypeError here by adding an empty label ""
        st.text_input("", placeholder=f"Enter Name for Employee {i}", key=f"user_name_{i}", label_visibility="collapsed")
        
        for week in ["Current", "Next"]:
            with st.container(border=True):
                st.write(f"**{week} Week**")
                s_time = st.selectbox(f"Start {i}{week}", hours, index=9, key=f"s{i}_{week}")
                e_time = calculate_end_time(s_time, duration)
                st.markdown(f"<div class='dark-match-box'>Ends: {e_time}</div>", unsafe_allow_html=True)
                
                shift_starts[f"e{i}_{week}"] = s_time
                shift_ends[f"e{i}_{week}"] = e_time
                
                # Dynamic filtering to prevent same day selection
                o1 = st.selectbox(f"Off1 {i}{week}", ["First Day off"] + day_list, key=f"d{i}a_{week}")
                o2 = st.selectbox(f"Off2 {i}{week}", ["Second Day off"] + [d for d in day_list if d != o1], key=f"d{i}b_{week}")
                off_days[f"e{i}_{week}"] = [o1, o2]

if st.button("🚀 Validate Swap", use_container_width=True):
    config = {
        1: {"cur": "e1_Current", "next": "e2_Next", "name": st.session_state.user_name_1},
        2: {"cur": "e2_Current", "next": "e1_Next", "name": st.session_state.user_name_2}
    }
    
    results_html = ""
    all_pass = True
    
    for emp_num, data in config.items():
        errs = []
        name = data['name'] if data['name'] else f"Employee {emp_num}"
        
        # Exemption Logic Check
        is_exempt = "Saturday" in off_days[data["cur"]] or "Sunday" in off_days[data["next"]]
        
        # 1. 12H Rest Check
        dt_end = get_dt(7, shift_ends[data["cur"]], True, shift_starts[data["cur"]])
        dt_start = get_dt(8, shift_starts[data["next"]])
        rest = (dt_start - dt_end).total_seconds() / 3600
        
        if rest < 12 and not is_exempt:
            errs.append(f"❌ Insufficient rest: **{rest:.1f} hours** (Ends {dt_end.strftime('%I %p')}, Starts {dt_start.strftime('%I %p')})")
        elif is_exempt:
            errs.append(f"✅ Exempt from 12h rule (Day off coverage)")

        # 2. 6-Day Work Rule
        work_c = 7 - sum(1 for d in off_days[data["cur"]] if d != "First Day off")
        work_n = 7 - sum(1 for d in off_days[data["next"]] if d != "Second Day off")
        if work_c > 6 or work_n > 6:
            errs.append(f"❌ Exceeds 6 working days (Current: {work_c}, Next: {work_n})")

        if any("❌" in e for e in errs): all_pass = False
        
        results_html += f"<div style='text-align: left;'><b>{name}:</b><br>"
        results_html += "".join([f"&nbsp;&nbsp;{e}<br>" for e in errs]) + "</div><br>"

    if all_pass:
        st.markdown(f"<div class='status-container approved'><h2>✅ Swap Approved</h2>{results_html}</div>", unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown(f"<div class='status-container rejected'><h2>❌ Swap Rejected</h2>{results_html}</div>", unsafe_allow_html=True)

st.markdown("<br><center><b>Created by Abdelrahman heshmat @abheshma</b></center>", unsafe_allow_html=True)
