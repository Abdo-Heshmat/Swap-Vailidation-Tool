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
    # Pure White Formal Theme (Removes Black Boxes)
    bg, box, txt, brd = "#ffffff", "#ffffff", "#111827", "#ced4da"

st.set_page_config(layout="wide", page_title="Compliance Validator Pro")

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
    .block-container {{ max-width: 950px !important; padding-top: 2rem !important; margin: auto !important; }}
    .stApp {{ background-color: {bg}; color: {txt}; }}
    h1, h2, h3, h4, p, label {{ text-align: center !important; color: {txt} !important; font-weight: 600; }}
    
    /* Strict override to fix "Black Boxes" */
    div[data-testid="stVerticalBlockBorderWrapper"], 
    .stSelectbox div[data-baseweb="select"],
    input[type="text"], .stNumberInput input, .stToggle {{
        background-color: {box} !important; 
        color: {txt} !important;
        border: 1px solid {brd} !important; 
        border-radius: 8px !important;
    }}
    
    .auto-box {{
        background-color: {box}; color: #007bff; border: 1px solid {brd};
        padding: 8px; border-radius: 8px; text-align: center; font-weight: bold; margin-top: 4px; min-height: 42px;
    }}

    /* Full-Width Centered Button at the very bottom */
    div.stButton > button:first-child {{
        display: block;
        margin: 40px auto;
        width: 100% !important;
        max-width: 700px;
        height: 60px;
        background-color: #007bff !important;
        color: white !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 15px;
        box-shadow: 0px 4px 10px rgba(0, 123, 255, 0.3);
    }}
    
    .results-card {{ padding: 25px; border-radius: 15px; margin-top: 30px; border: 2px solid {brd}; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# Header
t1, t2 = st.columns([9, 1])
with t2: st.button("🌓", on_click=toggle_theme)
with t1: st.markdown("<h1>👤 Workforce Compliance Pro</h1>", unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h Shift)")
base_dur = 7 if is_ramadan else 9

# --- 4. MAIN INTERFACE ---
shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"### Employee {i}")
        st.text_input(f"Name", key=f"un{i}", placeholder=f"Full Name", label_visibility="collapsed")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"**🗓️ {wk} Week**")
                
                # SHIFT & OT SECTION
                row1_c1, row1_c2 = st.columns(2)
                with row1_c1:
                    s_t = st.selectbox(f"Start of Shift", hrs, index=hrs.index(st.session_state.get(f"s{i}{wk}", "09 AM")), key=f"s{i}{wk}")
                with row1_c2:
                    e_t = (datetime.strptime(s_t, "%I %p") + timedelta(hours=base_dur)).strftime("%I %p")
                    st.markdown("End of Shift")
                    st.markdown(f"<div class='auto-box'>{e_t}</div>", unsafe_allow_html=True)
                
                ot_c1, ot_c2, ot_c3 = st.columns([3, 3, 4])
                with ot_c1:
                    cur_ota = st.session_state.get(f"ota_{i}_{wk}", 0)
                    otb = st.number_input(f"Before OT", 0, 2 - cur_ota, key=f"otb_{i}_{wk}")
                with ot_c2:
                    cur_otb = st.session_state.get(f"otb_{i}_{wk}", 0)
                    ota = st.number_input(f"After OT", 0, 2 - cur_otb, key=f"ota_{i}_{wk}")
                with ot_c3:
                    total_hrs = base_dur + otb + ota
                    st.markdown("Total Shift")
                    st.markdown(f"<div class='auto-box'>{total_hrs} Hours</div>", unsafe_allow_html=True)

                st.write("---")
                
                # OFF DAYS WITH TOGGLES BESIDE THEM
                off1_c1, off1_c2 = st.columns([6, 4])
                with off1_c1:
                    o1 = st.selectbox(f"First Day Off", ["None"] + days_list, key=f"o1{i}{wk}")
                with off1_c2:
                    st.write("") # Alignment
                    ot1 = st.toggle(f"Work OT", key=f"do_ot1_{i}_{wk}", disabled=(o1 == "None"))

                off2_c1, off2_c2 = st.columns([6, 4])
                with off2_c1:
                    o2_opts = ["None"] + [d for d in days_list if d != o1]
                    o2 = st.selectbox(f"Second Day Off", o2_opts, key=f"o2{i}{wk}")
                with off2_c2:
                    st.write("") # Alignment
                    ot2 = st.toggle(f"Work OT ", key=f"do_ot2_{i}_{wk}", disabled=(o2 == "None"))

            # Logic Setup
            real_offs = []
            if o1 in days_list and not ot1: real_offs.append(days_list.index(o1)+1)
            if o2 in days_list and not ot2: real_offs.append(days_list.index(o2)+1)
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": real_offs, "otb": otb, "ota": ota, "name": st.session_state[f"un{i}"] or f"Emp {i}"}

# --- 5. COMPLIANCE ENGINE & FINAL BUTTON ---
if st.button("🚀 RUN COMPLIANCE CHECK"):
    results = []
    checks = [{"id": 1, "cur": "e1_Current", "nxt": "e2_Next"}, {"id": 2, "cur": "e2_Current", "nxt": "e1_Next"}]

    for c in checks:
        name = shift_data[c['cur']]['name']
        cur, nxt = shift_data[c['cur']], shift_data[c['nxt']]
        msgs, fail = [], False
        
        # 12h Rest
        is_exempt = (7 in cur['off']) or (1 in nxt['off'])
        if is_exempt: msgs.append("✅ Rest Rule: Passed (Weekend Break)")
        else:
            dt_e = get_dt(7, cur['e'], True, cur['s']) + timedelta(hours=cur['ota'])
            dt_s = get_dt(8, nxt['s']) - timedelta(hours=nxt['otb'])
            gap = (dt_s - dt_e).total_seconds() / 3600
            if gap >= 12: msgs.append(f"✅ Rest Rule: Passed ({gap:.1f}h Rest)")
            else:
                msgs.append(f"❌ Rest Rule: REJECTED! (Gap is {gap:.1f}h)")
                fail = True

        # Consecutive Days
        w1_work = [d for d in range(1, 8) if d not in cur['off']]
        w2_work = [d for d in range(8, 15) if (d-7) not in nxt['off']]
        timeline = sorted(w1_work + w2_work)
        streak, max_s = 0, 0
        for d in range(1, 15):
            if d in timeline:
                streak += 1
                max_s = max(max_s, streak)
            else: streak = 0
        if max_s <= 6: msgs.append(f"✅ Consecutive Rule: Passed ({max_s} days)")
        else:
            msgs.append(f"❌ Consecutive Rule: REJECTED! ({max_s}-day streak)")
            fail = True
            
        results.append({"name": name, "msgs": msgs, "fail": fail})

    # Output Card
    overall_fail = any(r['fail'] for r in results)
    card_color = "#d32f2f" if overall_fail else "#2e7d32"
    
    st.markdown(f"<div class='results-card' style='background-color:{card_color}; color:white;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:white;'>{'❌ SWAP DENIED' if overall_fail else '✅ SWAP APPROVED'}</h2>", unsafe_allow_html=True)
    for r in results:
        st.markdown(f"**Compliance for {r['name']}:**")
        for m in r['msgs']: st.markdown(f"<p style='margin:0;'>{m}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("---")
st.button("🎲 Randomize Data", on_click=on_load_random)
