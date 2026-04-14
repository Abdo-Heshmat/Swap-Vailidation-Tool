import streamlit as st
from datetime import datetime, timedelta
import random

# --- 1. THEME & INITIALIZATION ---
if 'theme' not in st.session_state: st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Define strict reactive variables
if st.session_state.theme == 'dark':
    bg, box, txt, brd, accent = "#0e1117", "#1e2129", "#ffffff", "#3e4451", "#4f46e5"
    input_txt = "#ffffff"
else:
    # High-contrast Light Mode (Pure White & Slate)
    bg, box, txt, brd, accent = "#f8fafc", "#ffffff", "#0f172a", "#cbd5e1", "#6366f1"
    input_txt = "#0f172a"

st.set_page_config(layout="wide", page_title="Smart Swap Validator Pro")

# --- 2. DYNAMIC HELPERS ---
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

def on_load_random():
    for i in [1, 2]:
        st.session_state[f"un{i}"] = random.choice(["Abdelrahman", "Sarah", "Ahmed", "Mariam"])
        for wk in ["Current", "Next"]:
            st.session_state[f"s{i}{wk}"] = random.choice(hrs)
            st.session_state[f"o1{i}{wk}"] = random.choice(days)
            st.session_state[f"o2{i}{wk}"] = random.choice([d for d in days if d != st.session_state.get(f"o1{i}{wk}")])

def get_dt(day_idx, time_str, is_end=False, s_time_str=None):
    # Anchor to a fixed Sunday
    base_sunday = datetime(2026, 1, 4, 0, 0) 
    dt = base_sunday + timedelta(days=day_idx-1)
    t_obj = datetime.strptime(time_str, "%I %p")
    final_dt = datetime.combine(dt.date(), t_obj.time())
    
    # Correct Midnight Crossover Logic
    if is_end and s_time_str:
        s_hour = datetime.strptime(s_time_str, "%I %p").hour
        e_hour = t_obj.hour
        # If end hour is numerically less than or equal to start hour, it's next day
        if e_hour <= s_hour: 
            final_dt += timedelta(days=1)
    return final_dt

# --- 3. THE "NO MORE BLACK" CSS FIX ---
st.markdown(f"""
    <style>
    /* Force Background and Text */
    .stApp {{ background-color: {bg} !important; color: {txt} !important; }}
    
    /* Target EVERY input container, dropdown, and list item */
    div[data-testid="stVerticalBlockBorderWrapper"], 
    div[data-baseweb="select"], 
    div[role="listbox"], 
    ul[role="listbox"],
    li[role="option"],
    div[data-testid="stExpander"],
    div[data-testid="stNumberInput"],
    input, 
    .unified-box {{
        background-color: {box} !important; 
        color: {input_txt} !important;
        border: 1px solid {brd} !important;
    }}

    /* Fix for Dropdown Text inside the menu */
    div[data-baseweb="popover"] div {{
        background-color: {box} !important;
        color: {input_txt} !important;
    }}

    /* Fix for Toggle labels */
    .stToggle p {{ color: {txt} !important; }}
    
    /* Fix for Expanders */
    summary[data-testid="stExpanderHeader"] {{
        background-color: {box} !important;
        color: {txt} !important;
    }}

    .emp-header {{ text-align: center; font-weight: 800; font-size: 22px; color: {accent}; }}
    .unified-box {{ height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold; border-radius: 8px; }}
    
    /* Buttons */
    .stButton>button {{
        background-color: {box} !important;
        color: {txt} !important;
        border: 1px solid {brd} !important;
        width: 100%;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. UI STRUCTURE ---
l_col, h_col, r_col = st.columns([1, 8, 1])
with r_col: st.button("☀️" if st.session_state.theme == 'dark' else "🌙", on_click=toggle_theme)
with h_col: st.markdown(f'<h1 style="text-align:center;">👤🔁👤 Smart Swap Validator Pro</h1>', unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h)")
dur = 7 if is_ramadan else 9

shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"<div class='emp-header'>Employee {i}</div>", unsafe_allow_html=True)
        name_input = st.text_input(f"Name {i}", key=f"un{i}", placeholder="Enter Name", label_visibility="collapsed")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"**🗓️ {wk} Week**")
                t_cols = st.columns([4, 1, 4])
                with t_cols[0]:
                    s_t = st.selectbox(f"S{i}{wk}", hrs, index=hrs.index(st.session_state.get(f"s{i}{wk}", "09 AM")), key=f"s{i}{wk}", label_visibility="collapsed")
                t_cols[1].markdown("<p style='text-align:center; padding-top:10px;'>to</p>", unsafe_allow_html=True)
                with t_cols[2]:
                    e_t = (datetime.strptime(s_t, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                    st.markdown(f"<div class='unified-box'>{e_t}</div>", unsafe_allow_html=True)
                
                o1 = st.selectbox(f"O1{i}{wk}", ["None"] + days, key=f"o1{i}{wk}", label_visibility="collapsed")
                ot1 = st.toggle("Work 6th Day OT", key=f"do_ot1_{i}_{wk}")
                o2 = st.selectbox(f"O2{i}{wk}", ["None"] + [d for d in days if d != o1], key=f"o2{i}{wk}", label_visibility="collapsed")
                ot2 = st.toggle("Work 7th Day OT", key=f"do_ot2_{i}_{wk}")
                
                with st.expander("➕ Daily OT"):
                    otb = st.number_input(f"Before {i}{wk}", 0, 2, key=f"otb_{i}_{wk}")
                    ota = st.number_input(f"After {i}{wk}", 0, 2, key=f"ota_{i}_{wk}")

            real_offs = []
            if o1 in days and not ot1: real_offs.append(days.index(o1)+1)
            if o2 in days and not ot2: real_offs.append(days.index(o2)+1)
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": real_offs, "otb": otb, "ota": ota, "name": name_input or f"Emp {i}"}

# --- 5. CORRECTED VALIDATION LOGIC ---
if st.button("🚀 Run Swap Check", use_container_width=True):
    results = []
    checks = [{"cur": "e1_Current", "nxt": "e2_Next", "name": shift_data["e1_Current"]["name"]},
              {"cur": "e2_Current", "nxt": "e1_Next", "name": shift_data["e2_Current"]["name"]}]

    for check in checks:
        cur, nxt = shift_data[check['cur']], shift_data[check['nxt']]
        msgs, fail = [], False
        
        # Rule 1: 12h Rest (Sat End to Sun Start)
        if (7 not in cur['off']) and (1 not in nxt['off']):
            dt_e = get_dt(7, cur['e'], True, cur['s']) + timedelta(hours=cur['ota'])
            dt_s = get_dt(8, nxt['s']) - timedelta(hours=nxt['otb'])
            gap = (dt_s - dt_e).total_seconds() / 3600
            
            if gap < 12:
                msgs.append(f"❌ **Rest Rule:** REJECTED. Gap is {gap:.1f}h (Min 12h).")
                fail = True
            else:
                msgs.append(f"✅ **Rest Rule:** Valid {gap:.1f}h gap.")
        else:
            msgs.append("✅ **Rest Rule:** Waived (Day Off).")

        # Rule 2: Consecutive 6 Days
        w1_work = [d for d in range(1, 8) if d not in cur['off']]
        w2_work = [d for d in range(8, 15) if (d-7) not in nxt['off']]
        combined = sorted(w1_work + w2_work)
        streak, max_s = 0, 0
        for d in range(1, 15):
            if d in combined: streak += 1; max_s = max(max_s, streak)
            else: streak = 0
        
        if max_s > 6:
            msgs.append(f"❌ **Consecutive Rule:** REJECTED ({max_s} days).")
            fail = True
        else:
            msgs.append(f"✅ **Consecutive Rule:** Passed ({max_s} days).")
            
        results.append({"name": check['name'], "msgs": msgs, "fail": fail})

    # Results UI
    all_ok = not any(r['fail'] for r in results)
    st.markdown(f"<div style='background-color:{'#16a34a' if all_ok else '#dc2626'}; color:white; padding:20px; border-radius:15px;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; color:white;'>{'✅ Swap Approved' if all_ok else '❌ Swap Rejected'}</h2>", unsafe_allow_html=True)
    for r in results:
        st.markdown(f"**{r['name']}**")
        for m in r['msgs']: st.markdown(f"<p style='margin:0; color:white !important;'>{m}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.button("🎲 Test Random Data", on_click=on_load_random)
