import streamlit as st
from datetime import datetime, timedelta

# --- Theme Management ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

if st.session_state.theme == 'dark':
    bg, box, txt, brd, btn = "#0e1117", "#1e2129", "#ffffff", "#3e4451", "☀️"
else:
    bg, box, txt, brd, btn = "#ffffff", "#f0f2f6", "#31333F", "#d3d3d3", "🌙"

st.set_page_config(layout="wide", page_title="Smart Swap Validator")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; max-width: 1100px; margin: 0 auto; }}
    div[data-testid="stVerticalBlockBorderWrapper"], .stSelectbox div[data-baseweb="select"],
    input[type="text"], .unified-box {{
        background-color: {box} !important; color: {txt} !important;
        border: 1px solid {brd} !important; border-radius: 8px !important;
    }}
    .unified-box {{ height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# --- Logic Functions ---
def get_dt(day_idx, time_str, is_end=False, s_time_str=None):
    # Week 1 = Days 1-7 | Week 2 = Days 8-14
    base = datetime(2026, 3, 22) 
    dt = base + timedelta(days=day_idx-1)
    t_obj = datetime.strptime(time_str, "%I %p")
    final_dt = datetime.combine(dt, t_obj.time())
    
    # PM end -> PM start = NEXT DAY calculation
    if is_end and s_time_str:
        s_obj = datetime.strptime(s_time_str, "%I %p")
        if t_obj.hour < s_obj.hour:
            final_dt += timedelta(days=1)
    return final_dt

# --- UI Setup ---
h_col, t_col = st.columns([9, 1])
with h_col: st.markdown("<h1>🔄 Smart Swap Validator</h1>", unsafe_allow_html=True)
with t_col: st.button(btn, on_click=toggle_theme)

is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
dur = 7 if is_ramadan else 9

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"### 👤 Employee {i}")
        st.text_input(f"Name {i}", key=f"un{i}", placeholder="Enter Name", label_visibility="collapsed")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"<center><b>🗓️ {wk} Week</b></center>", unsafe_allow_html=True)
                t1, t2, t3 = st.columns([3, 1, 3])
                with t1: st_t = st.selectbox(f"S{i}{wk}", hrs, index=9, key=f"s{i}{wk}", label_visibility="collapsed")
                with t2: st.write("<br><center>to</center>", unsafe_allow_html=True)
                
                en_t = (datetime.strptime(st_t, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                with t3: st.markdown(f"<div class='unified-box'>{en_t}</div>", unsafe_allow_html=True)
                
                st.write("Days Off:")
                d1, d2 = st.columns(2)
                off1 = d1.selectbox(f"O1{i}{wk}", ["Day off 1"] + days, key=f"o1{i}{wk}", label_visibility="collapsed")
                # Filter to prevent duplicate selection
                remain = [d for d in days if d != off1]
                off2 = d2.selectbox(f"O2{i}{wk}", ["Day off 2"] + remain, key=f"o2{i}{wk}", label_visibility="collapsed")
                
                indices = [days.index(o)+1 for o in [off1, off2] if o in days]
                shift_data[f"e{i}_{wk}"] = {"s": st_t, "e": en_t, "off": sorted(indices)}

st.divider()

if st.button("🚀 Run Swap Check", use_container_width=True):
    results = []
    configs = {1: {"c": "e1_Current", "n": "e2_Next", "u": "un1"},
               2: {"c": "e2_Current", "n": "e1_Next", "u": "un2"}}

    for en, cfg in configs.items():
        reasons = []
        name = st.session_state[cfg['u']] or f"Employee {en}"
        
        # Rule 1: 12H Rest & Exemption
        # Sat = Day 7, Sun = Day 8
        is_exempt = (7 in shift_data[cfg['c']]["off"]) or (1 in shift_data[cfg['n']]["off"])
        
        if is_exempt:
            reasons.append("✅ Exempt from 12-hour rule (Off Sat/Sun)")
        else:
            dt_end = get_dt(7, shift_data[cfg['c']]["e"], True, shift_data[cfg['c']]["s"])
            dt_start = get_dt(8, shift_data[cfg['n']]["s"])
            rest = (dt_start - dt_end).total_seconds() / 3600
            
            if rest < 12:
                reasons.append(f"❌ Insufficient Rest: **{rest:.1f}h** (Min 12h)")
            else:
                reasons.append(f"✅ Sufficient Rest: **{rest:.1f}h**")

        # Rule 2: 6 Consecutive Days
        # Fixed logic to avoid IndexErrors and incorrect counts
        last_off = shift_data[cfg['c']]["off"][-1] if shift_data[cfg['c']]["off"] else 0
        next_off = shift_data[cfg['n']]["off"][0] if shift_data[cfg['n']]["off"] else 8
        work_days = (7 - last_off) + (next_off - 1)
        
        if work_days > 6:
            reasons.append(f"❌ Consecutive Work: **{work_days} days** (Limit 6)")
        else:
            reasons.append(f"✅ Consecutive Work: **{work_days} days**")
            
        results.append({"name": name, "msgs": reasons})

    success = all("❌" not in " ".join(r["msgs"]) for r in results)
    color = "#1b5e20" if success else "#b71c1c"
    st.markdown(f"""
        <div style='padding:20px; border-radius:12px; background-color:{color}; color:white;'>
        <h2 style='text-align: center;'>{'✅ Swap Approved' if success else '❌ Swap Rejected'}</h2>
    """, unsafe_allow_html=True)
    for r in results:
        st.write(f"**{r['name']}**")
        for m in r['msgs']: st.write(m)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><center>Created by Abdelrahman heshmat @abheshma</center>", unsafe_allow_html=True)

