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
    # Professional Clean White Theme
    bg, box, txt, brd = "#ffffff", "#ffffff", "#111827", "#ced4da"

st.set_page_config(layout="wide", page_title="Shift Compliance Validator")

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

# --- 3. UI STYLING (Centered & Formal) ---
st.markdown(f"""
    <style>
    .block-container {{ max-width: 900px !important; padding-top: 2rem !important; margin: auto !important; }}
    .stApp {{ background-color: {bg}; color: {txt}; }}
    h1, h2, h3, h4, p, label {{ text-align: center !important; color: {txt} !important; }}
    
    /* Box Styling for Light Mode Fix */
    div[data-testid="stVerticalBlockBorderWrapper"], .stSelectbox div[data-baseweb="select"],
    input[type="text"], .stNumberInput input {{
        background-color: {box} !important; 
        color: {txt} !important;
        border: 1px solid {brd} !important; 
        border-radius: 8px !important;
    }}
    
    .auto-box {{
        background-color: {box};
        color: {txt};
        border: 1px solid {brd};
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin-top: 4px;
    }}

    .stButton>button {{
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #007bff !important;
        color: white !important;
        font-weight: bold;
        font-size: 16px;
    }}
    
    .results-card {{ padding: 25px; border-radius: 15px; margin-top: 20px; border: 2px solid {brd}; text-align: center; }}
    .test-btn {{ position: fixed; bottom: 20px; right: 20px; z-index: 100; }}
    </style>
    """, unsafe_allow_html=True)

# Top Actions
t1, t2 = st.columns([8, 2])
with t2: st.button("☀️ Light / 🌙 Dark", on_click=toggle_theme)
with t1: st.markdown("<h1>👤 Workforce Compliance Validator</h1>", unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h Shift)")
dur = 7 if is_ramadan else 9

# --- 4. MAIN INTERFACE ---
shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"### Employee {i}")
        st.text_input(f"Name", key=f"un{i}", placeholder=f"Full Name {i}", label_visibility="collapsed")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"**🗓️ {wk} Week**")
                
                # Shift Row
                sc1, sc2 = st.columns(2)
                with sc1:
                    s_t = st.selectbox(f"Start of Shift", hrs, index=hrs.index(st.session_state.get(f"s{i}{wk}", "09 AM")), key=f"s{i}{wk}")
                with sc2:
                    e_t = (datetime.strptime(s_t, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                    st.markdown(f"End of Shift")
                    st.markdown(f"<div class='auto-box'>{e_t}</div>", unsafe_allow_html=True)
                
                st.write("---")
                
                # FIX: Mutual Exclusion for Off Days
                o1 = st.selectbox(f"First Day Off", ["None"] + days_list, key=f"o1{i}{wk}")
                
                # The second list removes whatever was chosen in the first list
                available_for_o2 = ["None"] + [d for d in days_list if d != o1]
                o2 = st.selectbox(f"Second Day Off", available_for_o2, key=f"o2{i}{wk}")
                
                # OT Toggles
                ot1 = st.toggle(f"Work OT (6th Day)", key=f"do_ot1_{i}_{wk}", disabled=st.session_state.get(f"do_ot2_{i}_{wk}", False))
                ot2 = st.toggle(f"Work OT (7th Day)", key=f"do_ot2_{i}_{wk}", disabled=st.session_state.get(f"do_ot1_{i}_{wk}", False))
                
                # Overtime
                with st.expander("Overtime (Max 2h Total)"):
                    cur_ota = st.session_state.get(f"ota_{i}_{wk}", 0)
                    otb = st.number_input(f"Before Shift OT", 0, 2 - cur_ota, key=f"otb_{i}_{wk}")
                    cur_otb = st.session_state.get(f"otb_{i}_{wk}", 0)
                    ota = st.number_input(f"After Shift OT", 0, 2 - cur_otb, key=f"ota_{i}_{wk}")

            # Capture Logic
            real_offs = []
            if o1 in days_list and not ot1: real_offs.append(days_list.index(o1)+1)
            if o2 in days_list and not ot2: real_offs.append(days_list.index(o2)+1)
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": real_offs, "otb": otb, "ota": ota, "name": st.session_state[f"un{i}"] or f"Emp {i}"}

# --- 5. COMPLIANCE ENGINE ---
st.write("")
if st.button("🚀 RUN COMPLIANCE CHECK"):
    results = []
    checks = [{"id": 1, "cur": "e1_Current", "nxt": "e2_Next"}, {"id": 2, "cur": "e2_Current", "nxt": "e1_Next"}]

    for c in checks:
        name = shift_data[c['cur']]['name']
        cur_dat, nxt_dat = shift_data[c['cur']], shift_data[c['nxt']]
        msgs, fail = [], False
        
        # 12h Rest Rule
        is_exempt = (7 in cur_dat['off']) or (1 in nxt_dat['off'])
        if is_exempt:
            msgs.append(f"✅ Rest Rule: Passed (Weekend Rest)")
        else:
            dt_e = get_dt(7, cur_dat['e'], True, cur_dat['s']) + timedelta(hours=cur_dat['ota'])
            dt_s = get_dt(8, nxt_dat['s']) - timedelta(hours=nxt_dat['otb'])
            gap = (dt_s - dt_e).total_seconds() / 3600
            if gap >= 12:
                msgs.append(f"✅ Rest Rule: Passed ({gap:.1f}h Gap)")
            else:
                msgs.append(f"❌ Rest Rule: REJECTED! ({gap:.1f}h is less than 12h)")
                fail = True

        # 6-Day Consecutive Rule
        w1_work = [d for d in range(1, 8) if d not in cur_dat['off']]
        w2_work = [d for d in range(8, 15) if (d-7) not in nxt_dat['off']]
        timeline = sorted(w1_work + w2_work)
        streak, max_s = 0, 0
        for d in range(1, 15):
            if d in timeline:
                streak += 1
                max_s = max(max_s, streak)
            else: streak = 0
            
        if max_s <= 6:
            msgs.append(f"✅ Consecutive Rule: Passed ({max_s} days)")
        else:
            msgs.append(f"❌ Consecutive Rule: REJECTED! ({max_s}-day work streak)")
            fail = True
            
        results.append({"name": name, "msgs": msgs, "fail": fail})

    overall_fail = any(r['fail'] for r in results)
    card_color = "#d32f2f" if overall_fail else "#2e7d32"
    
    st.markdown(f"<div class='results-card' style='background-color:{card_color}; color:white;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:white;'>{'❌ SWAP REJECTED' if overall_fail else '✅ SWAP APPROVED'}</h2>", unsafe_allow_html=True)
    for r in results:
        st.markdown(f"**Compliance for {r['name']}:**")
        for m in r['msgs']: st.markdown(f"<p style='margin:0;'>{m}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Random Button
st.markdown('<div class="test-btn">', unsafe_allow_html=True)
st.button("🎲 Random Data", on_click=on_load_random)
st.markdown('</div>', unsafe_allow_html=True)
