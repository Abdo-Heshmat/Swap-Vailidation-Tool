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
    bg, box, txt, brd = "#ffffff", "#f9fafb", "#111827", "#d1d5db"

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
    h1, h2, h3, h4, p, span, label, .stMarkdown {{ color: {txt} !important; }}
    div[data-testid="stVerticalBlockBorderWrapper"], .stSelectbox div[data-baseweb="select"],
    input[type="text"], .unified-box, .stNumberInput input {{
        background-color: {box} !important; color: {txt} !important;
        border: 1px solid {brd} !important; border-radius: 8px !important;
    }}
    .unified-box {{ height: 40px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 1px solid {brd}; border-radius: 8px; background-color: {box}; }}
    .results-card {{ padding: 25px; border-radius: 12px; margin-top: 20px; border: 1px solid {brd}; }}
    .status-msg {{ font-size: 14px; margin-bottom: 5px; }}
    .test-btn-container {{ position: fixed; bottom: 20px; left: 20px; z-index: 99; }}
    </style>
    """, unsafe_allow_html=True)

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
        name_input = st.text_input(f"Name", key=f"un{i}", placeholder=f"Emp {i}")
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"**{wk} Week Schedule**")
                s_t = st.selectbox(f"Start {i}{wk}", hrs, index=hrs.index(st.session_state.get(f"s{i}{wk}", "09 AM")), key=f"s{i}{wk}")
                e_t = (datetime.strptime(s_t, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                st.info(f"Shift: {s_t} to {e_t}")
                
                o1 = st.selectbox(f"Off 1 {i}{wk}", ["None"] + days, key=f"o1{i}{wk}")
                ot1 = st.toggle("Work 6th Day", key=f"do_ot1_{i}_{wk}", disabled=st.session_state.get(f"do_ot2_{i}_{wk}", False))
                o2 = st.selectbox(f"Off 2 {i}{wk}", ["None"] + [d for d in days if d != o1], key=f"o2{i}{wk}")
                ot2 = st.toggle("Work 7th Day", key=f"do_ot2_{i}_{wk}", disabled=st.session_state.get(f"do_ot1_{i}_{wk}", False))
                
                with st.expander("OT (Max 2h Total)"):
                    ota_val = st.session_state.get(f"ota_{i}_{wk}", 0)
                    otb = st.number_input(f"Before {i}{wk}", 0, 2 - ota_val, key=f"otb_{i}_{wk}")
                    otb_val = st.session_state.get(f"otb_{i}_{wk}", 0)
                    ota = st.number_input(f"After {i}{wk}", 0, 2 - otb_val, key=f"ota_{i}_{wk}")

            real_offs = []
            if o1 in days and not ot1: real_offs.append(days.index(o1)+1)
            if o2 in days and not ot2: real_offs.append(days.index(o2)+1)
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": real_offs, "otb": otb, "ota": ota, "name": st.session_state[f"un{i}"] or f"Emp {i}"}

# --- 5. VALIDATION ENGINE ---
if st.button("🚀 RUN DETAILED COMPLIANCE CHECK", use_container_width=True):
    results = []
    checks = [{"id": 1, "cur": "e1_Current", "nxt": "e2_Next"}, {"id": 2, "cur": "e2_Current", "nxt": "e1_Next"}]

    for c in checks:
        cur_dat = shift_data[c['cur']]
        nxt_dat = shift_data[c['nxt']]
        msgs, fail = [], False
        
        # 1. REST RULE LOGIC
        is_exempt = (7 in cur_dat['off']) or (1 in nxt_dat['off'])
        if is_exempt:
            msgs.append("✅ **Rest Rule:** Waived (Weekend Day Off).")
        else:
            dt_e = get_dt(7, cur_dat['e'], True, cur_dat['s']) + timedelta(hours=cur_dat['ota'])
            dt_s = get_dt(8, nxt_dat['s']) - timedelta(hours=nxt_dat['otb'])
            gap = (dt_s - dt_e).total_seconds() / 3600
            
            if gap >= 12:
                msgs.append(f"✅ **Rest Rule:** Sufficient {gap:.1f}h gap between Sat & Sun.")
            else:
                msgs.append(f"❌ **Rest Rule REJECTED:** Only {gap:.1f}h gap found between Saturday and Sunday.")
                fail = True

        # 2. 6-DAY CONSECUTIVE LOGIC (With Detailed Day Listing)
        w1_work = [d for d in range(1, 8) if d not in cur_dat['off']]
        w2_work = [d for d in range(8, 15) if (d-7) not in nxt_dat['off']]
        timeline = sorted(w1_work + w2_work)
        
        streak_groups = []
        temp_streak = []
        for i, d in enumerate(timeline):
            if not temp_streak or d == temp_streak[-1] + 1:
                temp_streak.append(d)
            else:
                streak_groups.append(temp_streak)
                temp_streak = [d]
        if temp_streak: streak_groups.append(temp_streak)
        
        max_streak_group = max(streak_groups, key=len) if streak_groups else []
        max_s = len(max_streak_group)
        
        # Format the day names for the UI
        streak_day_names = [days[(d-1)%7] for d in max_streak_group]
        day_string = ", ".join(streak_day_names)

        if max_s <= 6:
            msgs.append(f"✅ **Consecutive Rule:** Passed ({max_s} days streak).")
        else:
            msgs.append(f"❌ **Consecutive Rule REJECTED:** {max_s}-day streak detected!")
            msgs.append(f"&nbsp;&nbsp;&nbsp;&nbsp;⚠️ *Problem Days:* {day_string}")
            fail = True
            
        results.append({"name": cur_dat['name'], "msgs": msgs, "fail": fail})

    # Display Results Card
    overall_fail = any(r['fail'] for r in results)
    card_bg = "#dc2626" if overall_fail else "#16a34a"
    
    st.markdown(f"<div class='results-card' style='background-color:{card_bg}; color:white;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; color:white;'>{'❌ SWAP DENIED' if overall_fail else '✅ SWAP APPROVED'}</h2>", unsafe_allow_html=True)
    for r in results:
        st.markdown(f"**{r['name']} Timeline:**")
        for m in r['msgs']:
            st.markdown(f"<div class='status-msg'>{m}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Randomize Button
st.markdown('<div class="test-btn-container">', unsafe_allow_html=True)
st.button("🎲 Randomize All Data", on_click=on_load_random)
st.markdown('</div>', unsafe_allow_html=True)
