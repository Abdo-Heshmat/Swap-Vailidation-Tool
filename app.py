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
    bg_color = "#0e1117"
    box_bg = "#1e2129"
    text_color = "#ffffff"
    border_color = "#3e4451"
    btn_face = "☀️" 
else:
    bg_color = "#ffffff"
    box_bg = "#f0f2f6"
    text_color = "#31333F"
    border_color = "#d3d3d3"
    btn_face = "🌙"

st.set_page_config(layout="wide", page_title="Swap Validator Pro")

# --- Global CSS for Unified Design ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; max-width: 1100px; margin: 0 auto; }}
    
    /* Force all containers, inputs, and selectboxes to look identical */
    div[data-testid="stVerticalBlockBorderWrapper"], 
    .stSelectbox div[data-baseweb="select"],
    input[type="text"],
    .unified-box {{
        background-color: {box_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
    }}

    /* Specific fix for the 2nd End Time box to match the first */
    .unified-box {{
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-size: 1rem;
    }}

    .rules-box {{ 
        background-color: {box_bg}; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #007bff; 
        margin-bottom: 20px; 
    }}

    /* Button Positioning */
    .stButton>button {{
        border-radius: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- Header with Top-Right Toggle ---
header_col, toggle_col = st.columns([9, 1])
with header_col:
    st.markdown("<h1>🔄 Smart Swap Validator</h1>", unsafe_allow_html=True)
with toggle_col:
    # Use the symbols requested: Moon for Dark pref, Sun for Light pref
    st.button(btn_face, on_click=toggle_theme, help="Toggle Light/Dark Mode")

# --- Rules Section ---
with st.expander("📋 View Validation Rules & Exemptions"):
    st.markdown(f"""
    <div class='rules-box'>
        <b>✅ Rules Applied:</b><br>
        * Minimum 12 hours rest between shift end and next shift start.<br>
        * Maximum 6 consecutive working days across weeks.<br>
        * <b>Important:</b> Midnight crossing shifts (e.g., 5 PM - 2 AM) are correctly calculated.
    </div>
    """, unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9

day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)
shift_starts, shift_ends, off_counts, off_days = {}, {}, {}, {}

for i, col in enumerate([col1, col2], 1):
    with col:
        st.markdown(f"<h3 style='text-align: center;'>👤 Employee {i}</h3>", unsafe_allow_html=True)
        # Fixed TypeError by providing label
        st.text_input(f"Name Label {i}", placeholder=f"Enter Name", key=f"user_name_{i}", label_visibility="collapsed")
        
        for week in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"<center><b>🗓️ {week} Week</b></center>", unsafe_allow_html=True)
                t1, t2, t3 = st.columns([3, 1, 3])
                with t1:
                    s_time = st.selectbox(f"S{i}{week}", hours, index=17 if i==1 and week=="Current" else 9, key=f"s{i}_{week}", label_visibility="collapsed")
                with t2: st.write("<br><center>to</center>", unsafe_allow_html=True)
                with t3:
                    # Unified Box: No arrow, same background as start time
                    e_time = calculate_end_time(s_time, duration)
                    st.markdown(f"<div class='unified-box'>{e_time}</div>", unsafe_allow_html=True)
                    shift_starts[f"e{i}_{week}"] = s_time
                    shift_ends[f"e{i}_{week}"] = e_time

                st.write("Days Off:")
                d_col1, d_col2 = st.columns(2)
                off1 = d_col1.selectbox(f"O1{i}{week}", ["First Day off"] + day_list, key=f"d{i}a_{week}", label_visibility="collapsed")
                off2 = d_col2.selectbox(f"O2{i}{week}", ["Second Day off"] + [d for d in day_list if d != off1], key=f"d{i}b_{week}", label_visibility="collapsed")
                
                off_counts[f"e{i}_{week}"] = sum(1 for x in [off1, off2] if "Day off" not in x)
                off_days[f"e{i}_{week}"] = [off1, off2]

st.divider()

if st.button("🚀 Run Swap Check", use_container_width=True):
    validation_results = []
    configs = {1: {"cur": "e1_Current", "next": "e2_Next", "n": "user_name_1"}, 
               2: {"cur": "e2_Current", "next": "e1_Next", "n": "user_name_2"}}

    for emp_num, cfg in configs.items():
        reasons = []
        name = st.session_state[cfg['n']] if st.session_state[cfg['n']] else f"Employee {emp_num}"
        
        if not ("Saturday" in off_days[cfg['cur']] or "Sunday" in off_days[cfg['next']]):
            dt_end = get_dt(7, shift_ends[cfg['cur']], True, shift_starts[cfg['cur']])
            dt_start = get_dt(8, shift_starts[cfg['next']])
            rest = (dt_start - dt_end).total_seconds() / 3600
            if rest < 12: reasons.append(f"Insufficient Rest: **{rest:.1f}h** (Min 12h).")
        
        if (7 - off_counts[cfg['cur']]) > 6: reasons.append("Current Week: Working > 6 days.")
        if (7 - off_counts[cfg['next']]) > 6: reasons.append("Next Week: Working > 6 days.")
        validation_results.append({"name": name, "reasons": reasons})

    is_success = all(len(r["reasons"]) == 0 for r in validation_results)
    title = "✅ Swap Approved" if is_success else "❌ Swap Rejected"
    st.markdown(f"<div style='padding:20px; border-radius:12px; border: 2px solid white; background-color:{'#1b5e20' if is_success else '#b71c1c'}; color:white;'><h2 style='text-align: center;'>{title}</h2>", unsafe_allow_html=True)
    for res in validation_results:
        st.write(f"**{res['name']}**")
        for r in res["reasons"]: st.write(f" - {r}")
        if not res["reasons"]: st.write(" - Safe schedule.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><center><b>Created by Abdelrahman heshmat @abheshma</b></center>", unsafe_allow_html=True)
