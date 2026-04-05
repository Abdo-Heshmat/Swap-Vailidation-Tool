import streamlit as st
from datetime import datetime, timedelta

# --- Helper Functions (The Engine) ---
def calculate_end_time(start_time_str, duration):
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=duration)
    return end_dt.strftime("%I %p")

def get_dt(day_idx, time_str, is_end_time=False, start_time_str=None):
    # Reference: Sun=1 (Mar 22), Sat=7 (Mar 28), Sun=8 (Mar 29)
    base_date = datetime(2026, 3, 22) 
    target_date = base_date + timedelta(days=day_idx-1)
    
    # Internal Logic: Fixes the approval problem by correctly identifying 
    # shifts that cross midnight (e.g., 5 PM to 2 AM) as ending the next day.
    if is_end_time and start_time_str:
        s_hour = datetime.strptime(start_time_str, "%I %p").hour
        e_hour = datetime.strptime(time_str, "%I %p").hour
        if e_hour < s_hour: # Crossed midnight
            target_date += timedelta(days=1)
            
    time_obj = datetime.strptime(time_str, "%I %p").time()
    return datetime.combine(target_date, time_obj)

# --- UI Styling (Your Exact Design) ---
st.set_page_config(layout="wide", page_title="Swap Validator Pro")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; max-width: 1100px; margin: 0 auto; }
    .rules-box { background-color: #1e2129; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 20px; }
    .exemption-box { background-color: #332b00; padding: 10px; border-radius: 5px; border: 1px solid #ffcc00; margin-top: 10px; font-size: 0.9rem; }
    input[type="text"] { text-align: center !important; background-color: #1e2129 !important; color: white !important; border: 1px solid #3e4451 !important; border-radius: 8px !important; }
    .dark-match-box { background-color: #1e2129; color: #00ff00; padding: 10px; border-radius: 8px; border: 1px solid #3e4451; text-align: center; font-weight: bold; font-size: 1.1rem; min-height: 45px; display: flex; align-items: center; justify-content: center; }
    .status-container { padding: 20px; border-radius: 12px; margin-top: 15px; }
    .approved { background-color: #1b5e20; color: white; border: 2px solid #ffffff; }
    .rejected { background-color: #b71c1c; color: white; border: 2px solid #ffffff; }
    .emp-header { font-weight: bold; font-size: 1.2rem; margin-top: 10px; text-decoration: underline; }
    .reason-item { margin-left: 20px; font-size: 1rem; list-style-type: disc; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🔄 Smart Swap Validator</h1>", unsafe_allow_html=True)

# --- Collapsible Rules Section ---
with st.expander("📋 Show/Hide Validation Rules", expanded=False):
    st.markdown("""
    <div class='rules-box'>
        <b>✅ Rules Applied:</b><br>
        * Minimum 12 hours rest between shift end and next shift start.<br>
        * Maximum 6 consecutive working days across weeks.<br>
        * <b>Important:</b> PM end → AM start = NEXT DAY calculation.<br>
        <div class='exemption-box'>
            <b>⚠️ Exemption Rules:</b><br>
            1. If employee is off on <b>Saturday (Day 7)</b>, 12-hour rule is <b>WAIVED</b>.<br>
            2. If employee is off on <b>Sunday (Day 8)</b>, 12-hour rule is <b>WAIVED</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9

day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)
shift_starts, shift_ends, off_counts, off_days = {}, {}, {}, {}

# --- Employee Data Entry ---
for i, col in enumerate([col1, col2], 1):
    with col:
        st.markdown(f"<h3 style='text-align: center;'>👤 Employee {i}</h3>", unsafe_allow_html=True)
        # Fixed: Added "" as label to resolve TypeError
        st.text_input("", placeholder=f"Employee {i} Name", key=f"user_name_{i}", label_visibility="collapsed")
        
        for week in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"<center><b>🗓️ {week} Week</b></center>", unsafe_allow_html=True)
                
                t1, t2, t3 = st.columns([3, 1, 3])
                with t1:
                    s_time = st.selectbox(f"Start {i}{week}", hours, index=17 if i==1 and week=="Current" else 9, key=f"s{i}_{week}", label_visibility="collapsed")
                with t2: st.write("<br><center>to</center>", unsafe_allow_html=True)
                with t3:
                    e_time = calculate_end_time(s_time, duration)
                    st.markdown(f"<div class='dark-match-box'>{e_time}</div>", unsafe_allow_html=True)
                    shift_starts[f"e{i}_{week}"] = s_time
                    shift_ends[f"e{i}_{week}"] = e_time

                st.write("Days Off:")
                d_col1, d_col2 = st.columns(2)
                off1 = d_col1.selectbox(f"Off1 {i}{week}", ["First Day off"] + day_list, key=f"d{i}a_{week}", label_visibility="collapsed")
                filtered_days = [d for d in day_list if d != off1] 
                off2 = d_col2.selectbox(f"Off2 {i}{week}", ["Second Day off"] + filtered_days, key=f"d{i}b_{week}", label_visibility="collapsed")
                
                count = 0
                if off1 != "First Day off": count += 1
                if off2 != "Second Day off": count += 1
                off_counts[f"e{i}_{week}"] = count
                off_days[f"e{i}_{week}"] = [off1, off2]

st.divider()

if st.button("🚀 Run Swap Check", use_container_width=True):
    validation_results = []
    swap_config = {
        1: {"cur_id": "e1_Current", "next_id": "e2_Next", "name_key": "user_name_1"},
        2: {"cur_id": "e2_Current", "next_id": "e1_Next", "name_key": "user_name_2"}
    }

    for emp_num, config in swap_config.items():
        reasons = []
        name = st.session_state[config['name_key']] if st.session_state[config['name_key']] else f"Employee {emp_num}"
        
        # Applying Exemption Rules
        is_off_sat = "Saturday" in off_days[config['cur_id']]
        is_off_sun = "Sunday" in off_days[config['next_id']]

        # 1. 12H Rest Rule Check (The corrected version)
        if not (is_off_sat or is_off_sun):
            dt_end = get_dt(7, shift_ends[config['cur_id']], is_end_time=True, start_time_str=shift_starts[config['cur_id']])
            dt_start = get_dt(8, shift_starts[config['next_id']])
            rest = (dt_start - dt_end).total_seconds() / 3600
            
            if rest < 12:
                reasons.append(f"Insufficient Rest: Only **{rest:.1f}h** (Min 12h).")
        
        # 2. 6-Day Work Rule Check (Fixed SyntaxError)
        work_cur = 7 - off_counts[config['cur_id']]
        work_next = 7 - off_counts[config['next_id']]
        if work_cur > 6: 
            reasons.append(f"Current Week: Working **{work_cur} days** (Limit 6).")
        if work_next > 6: 
            reasons.append(f"Next Week: Working **{work_next} days** (Limit 6).")
            
        validation_results.append({"name": name, "reasons": reasons})

    is_success = all(len(r["reasons"]) == 0 for r in validation_results)
    if is_success:
        st.markdown("<div class='status-container approved'><h2 style='text-align: center;'>✅ Swap Approved</h2></div>", unsafe_allow_html=True)
        st.balloons()
    else:
        html = "<div class='status-container rejected'><h2 style='text-align: center;'>❌ Swap Rejected</h2>"
        for res in validation_results:
            html += f"<div class='emp-header'>{res['name']}</div>"
            if res["reasons"]:
                for r in res["reasons"]: html += f"<div class='reason-item'>{r}</div>"
            else:
                html += "<div class='reason-item' style='color: #a5d6a7;'>✅ Schedule is safe.</div>"
        st.markdown(html + "</div>", unsafe_allow_html=True)

st.markdown("<br><center><b>Created by Abdelrahman heshmat @abheshma</b></center>", unsafe_allow_html=True)
