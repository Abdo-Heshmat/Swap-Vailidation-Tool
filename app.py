import streamlit as st
from datetime import datetime, timedelta
import random

# --- 1. THEME & INITIALIZATION ---
if 'theme' not in st.session_state: st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

if st.session_state.theme == 'dark':
    bg, box, txt, brd = "#0e1117", "#1e2129", "#ffffff", "#3e4451"
else:
    # Forced White Theme - Fixes "Black Boxes" in Light Mode
    bg, box, txt, brd = "#ffffff", "#ffffff", "#111827", "#ced4da"

st.set_page_config(layout="wide", page_title="Workforce Swap Validator")

# --- 2. THE ORIGINAL HELPERS YOU REQUESTED ---
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

def on_load_random():
    for i in [1, 2]:
        st.session_state[f"un{i}"] = random.choice(["Abdelrahman", "Sarah", "Ahmed", "Mariam"])
        for wk in ["Current", "Next"]:
            st.session_state[f"s{i}{wk}"] = random.choice(hrs)
            st.session_state[f"o1{i}{wk}"] = random.choice(days)
            st.session_state[f"o2{i}{wk}"] = random.choice([d for d in days if d != st.session_state.get(f"o1{i}{wk}", "")])
            st.session_state[f"otb_{i}_{wk}"] = 0
            st.session_state[f"ota_{i}_{wk}"] = 0

# --- 3. UI STYLING (The Original Structure) ---
st.markdown(f"""
    <style>
    .block-container {{ max-width: 900px !important; padding-top: 2rem !important; margin: auto !important; }}
    .stApp {{ background-color: {bg}; color: {txt}; }}
    h1, h2, h3, h4, p, label {{ text-align: center !important; color: {txt} !important; }}
    div[data-testid="stVerticalBlockBorderWrapper"], .stSelectbox div[data-baseweb="select"],
    input[type="text"], .stNumberInput input {{
        background-color: {box} !important; color: {txt} !important;
        border: 1px solid {brd} !important; border-radius: 8px !important;
    }}
    .results-card {{ padding: 25px; border-radius: 15px; margin-top: 20px; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

# Top Nav
t1, t2 = st.columns([9, 1])
with t2: st.button("🌓", on_click=toggle_theme)
with t1: st.markdown("<h1>👤 Workforce Swap Validator</h1>", unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h Shift)")
dur = 7 if is_ramadan else 9

# --- 4. MAIN INTERFACE ---
shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"### Employee {i}")
        st.text_input(f"Name", key=f"un{i}", label_visibility="collapsed", placeholder=f"Employee {i} Name")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"**🗓️ {wk} Week**")
                s_t = st.selectbox(f"Start {i}{wk}", hrs, index=hrs.index(st.session_state.get(f"s{i}{wk}", "09 AM")), key=f"s{i}{wk}")
                e_t = (datetime.strptime(s_t, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                st.info(f"Shift: {s_t} to {e_t}")
                
                o1 = st.selectbox(f"Off 1 {i}{wk}", ["None"] + days, key=f"o1{i}{wk}")
                ot1 = st.toggle(f"Work 6th Day", key=f"do_ot1_{i}_{wk}")
                
                # Mutual Exclusion Fix
                o2_opts = ["None"] + [d for d in days if d != o1]
                o2 = st.selectbox(f"Off 2 {i}{wk}", o2_opts, key=f"o2{i}{wk}")
                ot2 = st.toggle(f"Work 7th Day", key=f"do_ot2_{i}_{wk}")
                
                with st.expander("OT Settings"):
                    otb = st.number_input(f"Before {i}{wk}", 0, 2, key=f"otb_{i}_{wk}")
                    ota = st.number_input(f"After {i}{wk}", 0, 2, key=f"ota_{i}_{wk}")

            real_offs = []
            if o1 in days and not ot1: real_offs.append(days.index(o1)+1)
            if o2 in days and not ot2: real_offs.append(days.index(o2)+1)
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": real_offs, "otb": otb, "ota": ota}

# --- 5. THE ORIGINAL VALIDATION LOGIC (DETAILED RESULTS) ---
if st.button("🚀 Run Swap Check", use_container_width=True):
    results = []
    has_conflict = False
    conflict_day = ""
    wk_key_conflict = ""
    
    # 1. Check for Timing Conflicts (Both working same time)
    for d_idx in range(1, 15):
        wk_key = "Current" if d_idx <= 7 else "Next"
        adj_idx = d_idx if d_idx <= 7 else d_idx - 7
        
        e1 = shift_data[f"e1_{wk_key}"]
        e2 = shift_data[f"e2_{wk_key}"]
        
        if adj_idx not in e1["off"] and adj_idx not in e2["off"]:
            start1 = get_dt(d_idx, e1["s"])
            end1 = get_dt(d_idx, e1["e"], True, e1["s"])
            start2 = get_dt(d_idx, e2["s"])
            end2 = get_dt(d_idx, e2["e"], True, e2["s"])
            
            if (start1 < end2) and (end1 > start2):
                has_conflict = True
                conflict_day = days[adj_idx-1]
                wk_key_conflict = wk_key
                break

    # 2. Check Rest Rules (SWAP LOGIC: Emp 1 Cur -> Emp 2 Nxt | Emp 2 Cur -> Emp 1 Nxt)
    swap_configs = {
        1: {"c": "e1_Current", "n": "e2_Next", "idx": 1}, 
        2: {"c": "e2_Current", "n": "e1_Next", "idx": 2}
    }
    
    for en, cfg in swap_configs.items():
        name = st.session_state[f"un{en}"] or f"Employee {en}"
        msgs = []
        
        cur_week = shift_data[cfg['c']]
        nxt_week = shift_data[cfg['n']]
        
        # Rest Rule Check
        is_exempt = (7 in cur_week["off"]) or (1 in nxt_week["off"])
        if is_exempt:
            msgs.append("✅ **Rest Rule:** Waived (Has Sat/Sun off).")
        else:
            dt_e = get_dt(7, cur_week["e"], True, cur_week["s"]) + timedelta(hours=cur_week['ota'])
            dt_s = get_dt(8, nxt_week["s"]) - timedelta(hours=nxt_week['otb'])
            gap = (dt_s - dt_e).total_seconds() / 3600
            
            if gap >= 12:
                msgs.append(f"✅ **Rest Rule:** Sufficient {gap:.1f}h gap between Weeks.")
            else:
                msgs.append(f"❌ **Rest Rule Rejected:** Only {gap:.1f}h gap between Saturday and Sunday.")

        if has_conflict:
            msgs.append(f"❌ **Conflict Alert:** Overlap on {conflict_day} ({wk_key_conflict} Week).")
            
        results.append({"name": name, "msgs": msgs})

    # UI Display
    success = all("❌" not in "".join(r["msgs"]) for r in results)
    card_bg = '#1b5e20' if success else '#b71c1c'
    st.markdown(f"<div class='results-card' style='background-color:{card_bg}; color:white;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:white;'>{'✅ Approved' if success else '❌ Rejected'}</h2>", unsafe_allow_html=True)
    for r in results:
        st.markdown(f"<b>{r['name']}</b>", unsafe_allow_html=True)
        for m in r['msgs']: st.markdown(f"<p style='margin:0;'>{m}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("---")
st.button("🎲 Randomize Data", on_click=on_load_random)
