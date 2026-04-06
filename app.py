import streamlit as st
from datetime import datetime, timedelta

# --- Helper Functions ---
def calculate_end_time(start_time_str, duration):
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=duration)
    return end_dt.strftime("%I %p")

def get_dt(day_idx, time_str, is_end_time=False, start_time_str=None):
    """
    Ensures 'PM end -> PM start = NEXT DAY' rule.
    Explicitly handles 6 AM end times to prevent negative rest.
    """
    base_date = datetime(2026, 3, 22) # Start of Day 1
    target_date = base_date + timedelta(days=day_idx-1)
    
    current_time_obj = datetime.strptime(time_str, "%I %p")
    
    if is_end_time and start_time_str:
        start_time_obj = datetime.strptime(start_time_str, "%I %p")
        # If shift ends in AM but started in PM (e.g. 9PM -> 6AM)
        if current_time_obj.hour < start_time_obj.hour:
            target_date += timedelta(days=1)
            
    return datetime.combine(target_date, current_time_obj.time())

# --- Theme State ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

if st.session_state.theme == 'dark':
    bg_color, box_bg, text_color, border_color, btn_face = "#0e1117", "#1e2129", "#ffffff", "#3e4451", "☀️"
else:
    bg_color, box_bg, text_color, border_color, btn_face = "#ffffff", "#f0f2f6", "#31333F", "#d3d3d3", "🌙"

st.set_page_config(layout="wide", page_title="Smart Swap Validator")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; max-width: 1100px; margin: 0 auto; }}
    div[data-testid="stVerticalBlockBorderWrapper"], .stSelectbox div[data-baseweb="select"],
    input[type="text"], .unified-box {{
        background-color: {box_bg} !important; color: {text_color} !important;
        border: 1px solid {border_color} !important; border-radius: 8px !important;
    }}
    .unified-box {{ height: 42px; display: flex; align-items: center; justify-content: center; text-align: center; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# Top Bar
h_col, t_col = st.columns([9, 1])
with h_col: st.markdown("<h1>🔄 Smart Swap Validator</h1>", unsafe_allow_html=True)
with t_col: st.button(btn_face, on_click=toggle_theme)

is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9

day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)
shift_data = {}

for i, col in enumerate([col1, col2], 1):
    with col:
        st.markdown(f"<h3 style='text-align: center;'>👤 Employee {i}</h3>", unsafe_allow_html=True)
        st.text_input(f"Name {i}", placeholder="Enter Name", key=f"n{i}", label_visibility="collapsed")
        
        for week in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"<center><b>🗓️ {week} Week</b></center>", unsafe_allow_html=True)
                t1, t2, t3 = st.columns([3, 1, 3])
                # Default indices to match your screenshot example
                def_idx = 14 if (i==1 and week=="Current") else (9 if (i==1 and week=="Next") else 21)
                with t1: s_t = st.selectbox(f"S{i}{week}", hours, index=def_idx, key=f"s{i}{week}", label_visibility="collapsed")
                with t2: st.write("<br><center>to</center>", unsafe_allow_html=True)
                with t3:
                    e_t = calculate_end_time(s_t, duration)
                    st.markdown(f"<div class='unified-box'>{e_t}</div>", unsafe_allow_html=True)
                
                st.write("Days Off:")
                d1, d2 = st.columns(2)
                # FIX: Remove selected Day Off 1 from Day Off 2 list
                off1 = d1.selectbox(f"O1{i}{week}", ["Day off 1"] + day_list, key=f"o1{i}{week}", label_visibility="collapsed")
                
                remaining = [d for d in day_list if d != off1]
                off2 = d2.selectbox(f"O2{i}{week}", ["Day off 2"] + remaining, key=f"o2{i}{week}", label_visibility="collapsed")
                
                indices = [day_list.index(o)+1 for o in [off1, off2] if o in day_list]
                shift_data[f"e{i}_{week}"] = {"start": s_t, "end": e_t, "off": sorted(indices)}

st.divider()

if st.button("🚀 Run Swap Check", use_container_width=True):
    validation_results = []
    configs = {1: {"c": "e1_Current", "n": "e2_Next", "u": "n1"},
               2: {"c": "e2_Current", "n": "e1_Next", "u": "n2"}}

    for emp_num, cfg in configs.items():
        reasons = []
        name = st.session_state[cfg['u']] or f"Employee {emp_num}"
        
        # Rule: Exemption for Sat (Day 7) or Sun (Day 8)
        is_exempt = (7 in shift_data[cfg['c']]["off"]) or (1 in shift_data[cfg['n']]["off"])
        
        if is_exempt:
            reasons.append("✅ Exempt from 12-hour rule (Off Sat/Sun)")
        else:
            # Shift end of Week 1 (Day 7) vs Shift start of Week 2 (Day 8)
            dt_end = get_dt(7, shift_data[cfg['c']]["end"], True, shift_data[cfg['c']]["start"])
            dt_start = get_dt(8, shift_data[cfg['n']]["start"])
            rest = (dt_start - dt_end).total_seconds() / 3600
            
            if rest < 12:
                reasons.append(f"❌ Insufficient Rest: **{rest:.1f}h** (Min 12h)")
            else:
                reasons.append(f"✅ Sufficient Rest: **{rest:.1f}h**")

        # Rule: Max 6 Consecutive Working Days
        last_off = shift_data[cfg['c']]["off"][-1] if shift_data[cfg['c']]["off"] else 0
        first_off_next = shift_data[cfg['n']]["off"][0] if shift_data[cfg['n']]["off"] else 8
        consecutive = (7 - last_off) + (first_off_next - 1)
        
        if consecutive > 6:
            reasons.append(f"❌ Consecutive Work: **{consecutive} days** (Limit 6)")
        else:
            reasons.append(f"✅ Consecutive Work: **{consecutive} days**")

        validation_results.append({"name": name, "reasons": reasons})

    # Results Display
    is_ok = all("❌" not in " ".join(r["reasons"]) for r in validation_results)
    st.markdown(f"<div style='padding:20px; border-radius:12px; background-color:{'#1b5e20' if is_ok else '#b71c1c'}; color:white;'>"
                f"<h2 style='text-align: center;'>{'✅ Swap Approved' if is_ok else '❌ Swap Rejected'}</h2>", unsafe_allow_html=True)
    for res in validation_results:
        st.write(f"**{res['name']}**")
        for r in res["reasons"]: st.write(f" {r}")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><center><b>Created by Abdelrahman heshmat @abheshma</b></center>", unsafe_allow_html=True)
