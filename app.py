import streamlit as st
from datetime import datetime, timedelta
import random

# --- 1. THEME & INITIALIZATION ---
if 'theme' not in st.session_state: st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Professional Theme Palettes
if st.session_state.theme == 'dark':
    bg, box, txt, brd, accent = "#0e1117", "#1e2129", "#ffffff", "#3e4451", "#4f46e5"
else:
    bg, box, txt, brd, accent = "#f9fafb", "#ffffff", "#111827", "#d1d5db", "#3b82f6"

st.set_page_config(layout="wide", page_title="Professional Swap Validator")

# --- 2. DYNAMIC HELPERS ---
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

def on_load_random():
    for i in [1, 2]:
        st.session_state[f"un{i}"] = random.choice(["Abdelrahman", "Sarah", "Ahmed", "Mariam"])
        for wk in ["Current", "Next"]:
            st.session_state[f"s{i}{wk}"] = random.choice(hrs)
            st.session_state[f"o1{i}{wk}"] = random.choice(days)
            st.session_state[f"o2{i}{wk}"] = random.choice([d for d in days if d != st.session_state.get(f"o1{i}{wk}", "")])
            st.session_state[f"do_ot1_{i}_{wk}"] = False 
            st.session_state[f"do_ot2_{i}_{wk}"] = False
            st.session_state[f"otb_{i}_{wk}"] = 0
            st.session_state[f"ota_{i}_{wk}"] = 0

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

# --- 3. UI STYLING ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; max-width: 1100px; margin: 0 auto; }}
    h1, h2, h3, p, span, label {{ color: {txt} !important; }}
    div[data-testid="stVerticalBlockBorderWrapper"], .stSelectbox div[data-baseweb="select"],
    input[type="text"], .unified-box, .stNumberInput input {{
        background-color: {box} !important; color: {txt} !important;
        border: 1px solid {brd} !important; border-radius: 8px !important;
    }}
    .unified-box {{ height: 40px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 1px solid {brd}; border-radius: 8px; background-color: {box}; }}
    .results-card {{ padding: 25px; border-radius: 12px; margin-top: 20px; }}
    .test-btn-container {{ position: fixed; bottom: 20px; left: 20px; z-index: 99; }}
    </style>
    """, unsafe_allow_html=True)

# Header Row
l_col, r_col = st.columns([10, 1])
with r_col: st.button("☀️" if st.session_state.theme == 'dark' else "🌙", on_click=toggle_theme)
with l_col: st.title("👤🔁👤 Smart Swap Validator Pro")

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h Shift)")
dur = 7 if is_ramadan else 9

# --- 4. MAIN INTERFACE ---
shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.subheader(f"Employee {i}")
        st.text_input(f"Name", key=f"un{i}", placeholder="Enter Employee Name")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"**{wk} Week Schedule**")
                
                # Shift Logic
                t_cols = st.columns([5, 5])
                with t_cols[0]:
                    s_t = st.selectbox(f"Start Time", hrs, index=hrs.index(st.session_state.get(f"s{i}{wk}", "09 AM")), key=f"s{i}{wk}")
                with t_cols[1]:
                    e_t = (datetime.strptime(s_t, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                    st.markdown(f"<small>Ends At</small><div class='unified-box'>{e_t}</div>", unsafe_allow_html=True)
                
                # Mutual Exclusion for Off Days
                st.markdown("---")
                o1 = st.selectbox(f"Day Off 1", ["None"] + days, key=f"o1{i}{wk}")
                ot1 = st.toggle("Work 6th Day OT", key=f"do_ot1_{i}_{wk}", disabled=st.session_state.get(f"do_ot2_{i}_{wk}", False))
                
                o2 = st.selectbox(f"Day Off 2", ["None"] + [d for d in days if d != o1], key=f"o2{i}{wk}")
                ot2 = st.toggle("Work 7th Day OT", key=f"do_ot2_{i}_{wk}", disabled=st.session_state.get(f"do_ot1_{i}_{wk}", False))
                
                # Strict 2h OT Cap
                st.markdown("**Daily Overtime (Max 2h Total)**")
                ot_cols = st.columns(2)
                with ot_cols[0]:
                    cur_ota = st.session_state.get(f"ota_{i}_{wk}", 0)
                    otb = st.number_input(f"Before (h)", 0, 2 - cur_ota, key=f"otb_{i}_{wk}")
                with ot_cols[1]:
                    cur_otb = st.session_state.get(f"otb_{i}_{wk}", 0)
                    ota = st.number_input(f"After (h)", 0, 2 - cur_otb, key=f"ota_{i}_{wk}")

            # Capture for logic
            real_offs = []
            if o1 in days and not ot1: real_offs.append(days.index(o1)+1)
            if o2 in days and not ot2: real_offs.append(days.index(o2)+1)
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": real_offs, "otb": otb, "ota": ota, "name": st.session_state[f"un{i}"] or f"Emp {i}"}

# --- 5. VALIDATION ENGINE ---
if st.button("🚀 RUN COMPLIANCE CHECK", use_container_width=True):
    results = []
    checks = [{"id": 1, "cur": "e1_Current", "nxt": "e2_Next", "opp_id": 2},
              {"id": 2, "cur": "e2_Current", "nxt": "e1_Next", "opp_id": 1}]

    for c in checks:
        name = shift_data[c['cur']]['name']
        msgs = []
        fail = False
        
        # RULE A: 12h REST RULE
        is_exempt = (7 in shift_data[c['cur']]['off']) or (1 in shift_data[c['nxt']]['off'])
        if is_exempt:
            msgs.append("✅ Rest Rule: Waived (Weekend Day Off)")
        else:
            dt_e = get_dt(7, shift_data[c['cur']]['e'], True, shift_data[c['cur']]['s']) + timedelta(hours=shift_data[c['cur']]['ota'])
            dt_s = get_dt(8, shift_data[c['nxt']]['s']) - timedelta(hours=shift_data[c['nxt']]['otb'])
            gap = (dt_s - dt_e).total_seconds() / 3600
            
            if gap >= 12:
                msgs.append(f"✅ Rest Rule: {gap:.1f}h gap (Pass)")
            else:
                msgs.append(f"❌ Rest Rule: REJECTED! Only {gap:.1f}h gap between weeks.")
                fail = True

        # RULE B: 6-DAY CONSECUTIVE
        w1_work = [d for d in range(1, 8) if d not in shift_data[c['cur']]['off']]
        w2_work = [d for d in range(8, 15) if (d-7) not in shift_data[c['nxt']]['off']]
        full_timeline = sorted(w1_work + w2_work)
        streak, max_s = 0, 0
        for d in range(1, 15):
            if d in full_timeline:
                streak += 1
                max_s = max(max_s, streak)
            else: streak = 0
            
        if max_s <= 6:
            msgs.append(f"✅ Consecutive Rule: {max_s} days (Pass)")
        else:
            msgs.append(f"❌ Consecutive Rule: REJECTED! creates a {max_s}-day work streak.")
            fail = True
            
        results.append({"name": name, "msgs": msgs, "fail": fail})

    # Display Output
    overall_fail = any(r['fail'] for r in results)
    status_color = "#dc2626" if overall_fail else "#16a34a" # Hard Red / Hard Green
    
    st.markdown(f"<div class='results-card' style='background-color:{status_color}; color:white;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; color:white;'>{'❌ SWAP REJECTED' if overall_fail else '✅ SWAP APPROVED'}</h2>", unsafe_allow_html=True)
    for r in results:
        st.markdown(f"**{r['name']}**")
        for m in r['msgs']: st.markdown(f"<div style='font-size:14px; margin-left:10px;'>{m}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Random Button
st.markdown('<div class="test-btn-container">', unsafe_allow_html=True)
st.button("🎲 Randomize All Data", on_click=on_load_random)
st.markdown('</div>', unsafe_allow_html=True)
