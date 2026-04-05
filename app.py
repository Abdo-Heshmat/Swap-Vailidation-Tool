import streamlit as st
from datetime import datetime, timedelta

# --- Helper Functions ---
def calculate_end_time(start_time_str, duration):
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=duration)
    return end_dt.strftime("%I %p")

def get_dt(day_idx, time_str, is_end_time=False, start_time_str=None):
    base_date = datetime(2026, 3, 22) 
    target_date = base_date + timedelta(days=day_idx-1)
    if is_end_time and start_time_str:
        s_hour = datetime.strptime(start_time_str, "%I %p").hour
        e_hour = datetime.strptime(time_str, "%I %p").hour
        if e_hour < s_hour:
            target_date += timedelta(days=1)
    time_obj = datetime.strptime(time_str, "%I %p").time()
    return datetime.combine(target_date, time_obj)

# --- Theme State Management ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Define Unified Colors
if st.session_state.theme == 'dark':
    bg_color, box_bg, text_color, border_color, btn_face = "#0e1117", "#1e2129", "#ffffff", "#3e4451", "☀️"
else:
    bg_color, box_bg, text_color, border_color, btn_face = "#ffffff", "#f0f2f6", "#31333F", "#d3d3d3", "🌙"

st.set_page_config(layout="wide", page_title="Swap Validator Pro")

# --- Global CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; max-width: 1100px; margin: 0 auto; }}
    div[data-testid="stVerticalBlockBorderWrapper"], .stSelectbox div[data-baseweb="select"],
    input[type="text"], .unified-box {{
        background-color: {box_bg} !important; color: {text_color} !important;
        border: 1px solid {border_color} !important; border-radius: 8px !important;
    }}
    .unified-box {{ height: 42px; display: flex; align-items: center; justify-content: center; text-align: center; }}
    .rules-box {{ background-color: {box_bg}; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# --- Header & Toggle ---
h_col, t_col = st.columns([9, 1])
with h_col: st.markdown("<h1>🔄 Smart Swap Validator</h1>", unsafe_allow_html=True)
with t_col: st.button(btn_face, on_click=toggle_theme)

# --- Rules Section ---
with st.expander("📋 View Validation Rules & Exemptions"):
    st.markdown(f"<div class='rules-box'><b>✅ Rules Applied:</b><br>"
                f"* Min 12h rest between shifts.<br>"
                f"* Max 6 consecutive working days (Cross-week check enabled).<br>"
                f"* Ramadan shifts: 7h | Normal: 9h.</div>", unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9

day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)
shift_starts, shift_ends, off_days_indices = {}, {}, {}

for i, col in enumerate([col1, col2], 1):
    with col:
        st.markdown(f"<h3 style='text-align: center;'>👤 Employee {i}</h3>", unsafe_allow_html=True)
        st.text_input(f"Name {i}", placeholder="Enter Name", key=f"user_name_{i}", label_visibility="collapsed")
        
        for week in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"<center><b>🗓️ {week} Week</b></center>", unsafe_allow_html=True)
                t1, t2, t3 = st.columns([3, 1, 3])
                with t1: s_time = st.selectbox(f"S{i}{week}", hours, index=9, key=f"s{i}_{week}", label_visibility="collapsed")
                with t2: st.write("<br><center>to</center>", unsafe_allow_html=True)
                with t3:
                    e_time = calculate_end_time(s_time, duration)
                    st.markdown(f"<div class='unified-box'>{e_time}</div>", unsafe_allow_html=True)
                    shift_starts[f"e{i}_{week}"], shift_ends[f"e{i}_{week}"] = s_time, e_time

                st.write("Days Off:")
                d1, d2 = st.columns(2)
                o1 = d1.selectbox(f"O1{i}{week}", ["First Day off"] + day_list, key=f"d1{i}{week}", label_visibility="collapsed")
                o2 = d2.selectbox(f"O2{i}{week}", ["Second Day off"] + [d for d in day_list if d != o1], key=f"d2{i}{week}", label_visibility="collapsed")
                
                indices = []
                if o1 in day_list: indices.append(day_list.index(o1) + 1)
                if o2 in day_list: indices.append(day_list.index(o2) + 1)
                off_days_indices[f"e{i}_{week}"] = sorted(indices)

st.divider()

if st.button("🚀 Run Swap Check", use_container_width=True):
    validation_results = []
    configs = {1: {"c": "e1_Current", "n": "e2_Next", "u": "user_name_1"},
               2: {"c": "e2_Current", "n": "e1_Next", "u": "user_name_2"}}

    for emp_num, cfg in configs.items():
        reasons = []
        name = st.session_state[cfg['u']] or f"Employee {emp_num}"
        
        # 1. 12H Rest Rule
        if not (7 in off_days_indices[cfg['c']] or 1 in off_days_indices[cfg['n']]):
            dt_e = get_dt(7, shift_ends[cfg['c']], True, shift_starts[cfg['c']])
            dt_s = get_dt(8, shift_starts[cfg['n']])
            rest = (dt_s - dt_e).total_seconds() / 3600
            if rest < 12: reasons.append(f"Insufficient Rest: **{rest:.1f}h**.")

        # 2. 6-Consecutive Day Rule (Cross-Week Logic)
        last_off_cur = off_days_indices[cfg['c']][-1] if off_days_indices[cfg['c']] else 0
        first_off_next = off_days_indices[cfg['n']][0] if off_days_indices[cfg['n']] else 8
        # Days worked at end of week + days worked at start of next
        consecutive_work = (7 - last_off_cur) + (first_off_next - 1)
        
        if consecutive_work > 6:
            reasons.append(f"Consecutive Work: **{consecutive_work} days** (Limit 6).")

        validation_results.append({"name": name, "reasons": reasons})

    is_success = all(len(r["reasons"]) == 0 for r in validation_results)
    bg = "#1b5e20" if is_success else "#b71c1c"
    st.markdown(f"<div style='padding:20px; border-radius:12px; background-color:{bg}; color:white;'>"
                f"<h2 style='text-align: center;'>{'✅ Swap Approved' if is_success else '❌ Swap Rejected'}</h2>", unsafe_allow_html=True)
    for res in validation_results:
        st.write(f"**{res['name']}**")
        if not res["reasons"]: st.write(" - Schedule Valid.")
        for r in res["reasons"]: st.write(f" - {r}")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><center><b>Created by Abdelrahman heshmat @abheshma</b></center>", unsafe_allow_html=True)
