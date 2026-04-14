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
    # Forced White Theme - This fixes the "Black Boxes" from your screenshot
    bg, box, txt, brd = "#ffffff", "#ffffff", "#111827", "#ced4da"

st.set_page_config(layout="wide", page_title="Workforce Compliance")

# --- 2. DYNAMIC HELPERS ---
days_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

def on_load_random():
    for i in [1, 2]:
        st.session_state[f"un{i}"] = random.choice(["Abdelrahman", "Sarah", "Ahmed", "Mariam"])
        for wk in ["Current", "Next"]:
            st.session_state[f"s{i}{wk}"] = random.choice(hrs)
            st.session_state[f"o1{i}{wk}"] = random.choice(days_list)
            st.session_state[f"o2{i}{wk}"] = random.choice([d for d in days_list if d != st.session_state.get(f"o1{i}{wk}", "")])
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

# --- 3. UI STYLING (Centered & Formal) ---
st.markdown(f"""
    <style>
    .block-container {{ max-width: 900px !important; padding-top: 2rem !important; margin: auto !important; }}
    .stApp {{ background-color: {bg}; color: {txt}; }}
    h1, h2, h3, h4, p, label {{ text-align: center !important; color: {txt} !important; }}
    
    /* Global box override to ensure no black boxes appear in Light Mode */
    div[data-testid="stVerticalBlockBorderWrapper"], 
    .stSelectbox div[data-baseweb="select"],
    input[type="text"], .stNumberInput input {{
        background-color: {box} !important; 
        color: {txt} !important;
        border: 1px solid {brd} !important; 
        border-radius: 8px !important;
    }}
    
    /* The Long Centered Run Button */
    div.stButton > button:first-child {{
        display: block;
        margin: 30px auto;
        width: 100% !important;
        max-width: 500px;
        height: 50px;
        background-color: #007bff !important;
        color: white !important;
        font-weight: bold;
        border-radius: 10px;
    }}
    
    .results-card {{ padding: 25px; border-radius: 15px; margin-top: 20px; border: 2px solid {brd}; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# Header
t1, t2 = st.columns([9, 1])
with t2: st.button("🌓", on_click=toggle_theme)
with t1: st.markdown("<h1>👤 Workforce Compliance Validator</h1>", unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h Shift)")
dur = 7 if is_ramadan else 9

# --- 4. MAIN INTERFACE ---
shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"### Employee {i}")
        st.text_input(f"Name {i}", key=f"un{i}", label_visibility="collapsed", placeholder="Enter Name")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"**🗓️ {wk} Week Schedule**")
                
                # Start Time
                s_t = st.selectbox(f"Start {i}{wk}", hrs, index=hrs.index(st.session_state.get(f"s{i}{wk}", "09 AM")), key=f"s{i}{wk}")
                
                # Auto Shift Display
                e_t = (datetime.strptime(s_t, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                st.info(f"Shift: {s_t} to {e_t}")
                
                # Off Days (With Mutual Exclusion Fix)
                o1 = st.selectbox(f"Off 1 {i}{wk}", ["None"] + days_list, key=f"o1{i}{wk}")
                ot1 = st.toggle(f"Work 6th Day", key=f"do_ot1_{i}_{wk}")
                
                # Second off day cannot be the same as the first
                o2_opts = ["None"] + [d for d in days_list if d != o1]
                o2 = st.selectbox(f"Off 2 {i}{wk}", o2_opts, key=f"o2{i}{wk}")
                ot2 = st.toggle(f"Work 7th Day", key=f"do_ot2_{i}_{wk}")
                
                # Overtime
                with st.expander("OT (Max 2h Total)"):
                    ota_val = st.session_state.get(f"ota_{i}_{wk}", 0)
                    otb = st.number_input(f"Before {i}{wk}", 0, 2 - ota_val, key=f"otb_{i}_{wk}")
                    otb_val = st.session_state.get(f"otb_{i}_{wk}", 0)
                    ota = st.number_input(f"After {i}{wk}", 0, 2 - otb_val, key=f"ota_{i}_{wk}")

            # Capture Logic
            real_offs = []
            if o1 in days_list and not ot1: real_offs.append(days_list.index(o1)+1)
            if o2 in days_list and not ot2: real_offs.append(days_list.index(o2)+1)
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": real_offs, "otb": otb, "ota": ota, "name": st.session_state[f"un{i}"] or f"Emp {i}"}

# --- 5. COMPLIANCE ENGINE & RUN BUTTON ---
if st.button("🚀 RUN COMPLIANCE CHECK"):
    results = []
    checks = [{"id": 1, "cur": "e1_Current", "nxt": "e2_Next"}, {"id": 2, "cur": "e2_Current", "nxt": "e1_Next"}]

    for c in checks:
        name = shift_data[c['cur']]['name']
        cur, nxt = shift_data[c['cur']], shift_data[c['nxt']]
        msgs, fail = [], False
        
        # 12h Rest Rule
        is_exempt = (7 in cur['off']) or (1 in nxt['off'])
        if is_exempt:
            msgs.append("✅ **Rest Rule:** Waived (Weekend Day Off).")
        else:
            dt_e = get_dt(7, cur['e'], True, cur['s']) + timedelta(hours=cur['ota'])
            dt_s = get_dt(8, nxt['s']) - timedelta(hours=nxt['otb'])
            gap = (dt_s - dt_e).total_seconds() / 3600
            if gap >= 12:
                msgs.append(f"✅ **Rest Rule:** Passed ({gap:.1f}h gap).")
            else:
                msgs.append(f"❌ **Rest Rule:** REJECTED! Only {gap:.1f}h gap found.")
                fail = True

        # 6-Day Consecutive Rule
        w1_work = [d for d in range(1, 8) if d not in cur['off']]
        w2_work = [d for d in range(8, 15) if (d-7) not in nxt['off']]
        timeline = sorted(w1_work + w2_work)
        streak, max_s = 0, 0
        for d in range(1, 15):
            if d in timeline:
                streak += 1
                max_s = max(max_s, streak)
            else: streak = 0
            
        if max_s <= 6:
            msgs.append(f"✅ **Consecutive Rule:** Passed ({max_s} days streak).")
        else:
            msgs.append(f"❌ **Consecutive Rule:** REJECTED! Found a {max_s}-day streak.")
            fail = True
            
        results.append({"name": name, "msgs": msgs, "fail": fail})

    overall_fail = any(r['fail'] for r in results)
    card_color = "#dc3545" if overall_fail else "#28a745"
    
    st.markdown(f"<div class='results-card' style='background-color:{card_color}; color:white;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:white;'>{'❌ SWAP DENIED' if overall_fail else '✅ SWAP APPROVED'}</h2>", unsafe_allow_html=True)
    for r in results:
        st.markdown(f"**{r['name']} Results:**")
        for m in r['msgs']: st.markdown(f"<p style='margin:0;'>{m}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("---")
st.button("🎲 Randomize All Data", on_click=on_load_random)
