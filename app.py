import streamlit as st
from datetime import datetime, timedelta
import random

# --- 1. THEME & INITIALIZATION ---
if 'theme' not in st.session_state: st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

if st.session_state.theme == 'dark':
    bg, box, txt, brd = "#0e1117", "#1e2129", "#ffffff", "#3e4451"
else:
    bg, box, txt, brd = "#ffffff", "#f0f2f6", "#111827", "#ced4da"

st.set_page_config(layout="wide", page_title="Smart Swap Validator Pro")

# --- 2. HELPERS ---
def get_dt(day_idx, time_str, is_end=False, s_time_str=None):
    today = datetime.now()
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
    dt = start_of_week + timedelta(days=day_idx-1)
    t_obj = datetime.strptime(time_str, "%I %p")
    final_dt = datetime.combine(dt, t_obj.time())
    if is_end and s_time_str:
        if t_obj.hour < datetime.strptime(s_time_str, "%I %p").hour: 
            final_dt += timedelta(days=1)
    return final_dt

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

# --- 3. UI STYLING (Original Clean Layout) ---
st.markdown(f"""
    <style>
    .block-container {{ max-width: 1000px !important; padding-top: 1rem !important; }}
    .stApp {{ background-color: {bg}; color: {txt}; }}
    h1, h2, h3 {{ text-align: center !important; color: {txt} !important; }}
    
    /* Fixing the Light Mode "Black Boxes" while keeping original look */
    div[data-testid="stVerticalBlockBorderWrapper"], .stSelectbox div[data-baseweb="select"],
    input[type="text"], .stNumberInput input, div[data-testid="stExpander"] {{
        background-color: {box} !important; color: {txt} !important;
        border: 1px solid {brd} !important;
    }}
    
    .results-card {{ padding: 20px; border-radius: 10px; margin-top: 20px; text-align: left; }}
    </style>
    """, unsafe_allow_html=True)

# Header matching your screenshot
t1, t2 = st.columns([9, 1])
with t2: st.button("☀️" if st.session_state.theme == "dark" else "🌙", on_click=toggle_theme)
with t1: st.markdown("<h1>👥🔄👥 Smart Swap Validator Pro</h1>", unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h)")
dur = 7 if is_ramadan else 9

# --- 4. MAIN INTERFACE (Split Columns) ---
shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"<h3 style='text-align:center;'>Employee {i}</h3>", unsafe_allow_html=True)
        st.text_input(f"Employee {i} Name", key=f"un{i}", label_visibility="collapsed", placeholder=f"Employee {i} Name")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"**🗓️ {wk} Week**")
                
                # Shift Row
                sc1, sc2, sc3 = st.columns([4, 1, 4])
                with sc1:
                    s_t = st.selectbox(f"Start{i}{wk}", hrs, index=hrs.index(st.session_state.get(f"s{i}{wk}", "09 AM")), key=f"s{i}{wk}", label_visibility="collapsed")
                with sc2:
                    st.markdown("<p style='text-align:center; padding-top:10px;'>to</p>", unsafe_allow_html=True)
                with sc3:
                    e_t = (datetime.strptime(s_t, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                    st.markdown(f"<div style='background:{brd}; padding:8px; border-radius:5px; text-align:center; font-weight:bold;'>{e_t}</div>", unsafe_allow_html=True)

                # Off Days (Mutual Exclusion Fix)
                o1 = st.selectbox(f"Off1 {i}{wk}", ["None"] + days, key=f"o1{i}{wk}", label_visibility="collapsed")
                st.toggle(f"Work 6th Day OT", key=f"do_ot1_{i}_{wk}")
                
                o2_opts = ["None"] + [d for d in days if d != o1]
                o2 = st.selectbox(f"Off2 {i}{wk}", o2_opts, key=f"o2{i}{wk}", label_visibility="collapsed")
                st.toggle(f"Work 7th Day OT", key=f"do_ot2_{i}_{wk}")
                
                with st.expander("➕ Daily OT (Max 2h)"):
                    otb = st.number_input(f"Before {i}{wk}", 0, 2, key=f"otb_{i}_{wk}")
                    ota = st.number_input(f"After {i}{wk}", 0, 2, key=f"ota_{i}_{wk}")

            # Capture Logic
            real_offs = []
            if o1 in days and not st.session_state[f"do_ot1_{i}_{wk}"]: real_offs.append(days.index(o1)+1)
            if o2 in days and not st.session_state[f"do_ot2_{i}_{wk}"]: real_offs.append(days.index(o2)+1)
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": real_offs, "otb": otb, "ota": ota}

# --- 5. VALIDATION LOGIC ---
st.write("")
if st.button("🚀 Run Swap Check", use_container_width=True):
    results = []
    # Logic: Cross-compare Employee 1 Current vs Employee 2 Next
    swap_configs = {1: {"c": "e1_Current", "n": "e2_Next"}, 2: {"c": "e2_Current", "n": "e1_Next"}}
    
    for en, cfg in swap_configs.items():
        name = st.session_state[f"un{en}"] or f"Employee {en}"
        msgs = []
        cur, nxt = shift_data[cfg['c']], shift_data[cfg['n']]
        
        # Rest Rule Check
        is_exempt = (7 in cur["off"]) or (1 in nxt["off"])
        if is_exempt:
            msgs.append("✅ **Rest Rule:** Waived (Weekend Day Off).")
        else:
            dt_e = get_dt(7, cur["e"], True, cur["s"]) + timedelta(hours=cur['ota'])
            dt_s = get_dt(8, nxt["s"]) - timedelta(hours=nxt['otb'])
            gap = (dt_s - dt_e).total_seconds() / 3600
            if gap >= 12:
                msgs.append(f"✅ **Rest Rule:** Sufficient {gap:.1f}h gap.")
            else:
                msgs.append(f"❌ **Rest Rule Rejected:** Only {gap:.1f}h gap.")
            
        results.append({"name": name, "msgs": msgs})

    # Display Card matching your screenshot
    success = all("❌" not in "".join(r["msgs"]) for r in results)
    card_bg = '#1b5e20' if success else '#b71c1c'
    st.markdown(f"<div class='results-card' style='background-color:{card_bg}; color:white;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:white; margin:0;'>{'✅ Approved' if success else '❌ SWAP DENIED'}</h2>", unsafe_allow_html=True)
    for r in results:
        st.markdown(f"<p style='margin-bottom:0;'><b>{r['name']} Timeline:</b></p>", unsafe_allow_html=True)
        for m in r['msgs']: st.markdown(f"<p style='margin:0;'>{m}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("---")
if st.button("🎲 Test Random Data"):
    for i in [1, 2]:
        for wk in ["Current", "Next"]:
            st.session_state[f"s{i}{wk}"] = random.choice(hrs)
            st.session_state[f"o1{i}{wk}"] = random.choice(days)
            st.rerun()
