import streamlit as st
from datetime import datetime, timedelta
import random

# --- 1. INITIALIZATION ---
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

if 'theme' not in st.session_state: st.session_state.theme = 'light'
if 'initialized' not in st.session_state:
    for i in [1, 2]:
        st.session_state[f"un{i}"] = ""
        for wk in ["Current", "Next"]:
            st.session_state[f"s{i}{wk}"] = "11 PM"
            st.session_state[f"o1{i}{wk}"] = "1st Day Off"
            st.session_state[f"o2{i}{wk}"] = "2nd Day Off"
            st.session_state[f"otb_{i}_{wk}"] = 0
            st.session_state[f"ota_{i}_{wk}"] = 0
    st.session_state.initialized = True

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

def on_load_random():
    for i in [1, 2]:
        st.session_state[f"un{i}"] = random.choice(["Abdelrahman", "Sarah", "Ahmed", "Mariam"])
        for wk in ["Current", "Next"]:
            st.session_state[f"s{i}{wk}"] = random.choice(hrs)
            st.session_state[f"o1{i}{wk}"] = random.choice(days)
            st.session_state[f"o2{i}{wk}"] = random.choice([d for d in days if d != st.session_state[f"o1{i}{wk}"]])

# --- 2. STYLING ---
bg, box, txt, brd = ("#0e1117", "#1e2129", "#ffffff", "#3e4451") if st.session_state.theme == 'dark' else ("#f8f9fa", "#ffffff", "#1f2937", "#d1d5db")

st.set_page_config(layout="wide", page_title="Smart Swap Validator Pro")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; max-width: 1100px; margin: 0 auto; }}
    h1 {{ color: {txt}; text-align: center; margin-bottom: 5px; }}
    .results-card {{ padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-top: 20px; }}
    .status-line {{ padding: 8px; margin: 5px 0; border-radius: 8px; background: rgba(0,0,0,0.05); display: flex; justify-content: space-between; color: inherit; }}
    .test-btn-container {{ position: fixed; bottom: 20px; left: 20px; z-index: 1000; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER & RULES ---
l_space, h_col, t_col = st.columns([1, 10, 1])
with t_col: st.button("☀️" if st.session_state.theme == 'dark' else "🌙", on_click=toggle_theme)
with h_col: 
    st.markdown('<h1>👤🔁👤 Smart Swap Validator Pro</h1>', unsafe_allow_html=True)
    
    with st.expander("📋 View Validation Rules"):
        st.markdown("""
        * **Rest Rule:** Minimum 12 hours between shifts.
        * **Streak Rule:** Maximum 6 consecutive working days across weeks.
        * **Shift Duration:** 9 hours (Normal) / 7 hours (Ramadan).
        * **Exemption:** 12h rule is **WAIVED** if off on Saturday (Week 1) or Sunday (Week 2).
        * **OT Limit:** Max 2 hours total per day (Before + After).
        """)

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h Shifts)", help="Changes shift length and validation math")
dur = 7 if is_ramadan else 9

# --- 4. FORM ---
shift_data = {}
all_days_selected = True 

c1, c2 = st.columns(2)
for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"### Employee {i}")
        st.text_input(f"Name {i}", key=f"un{i}", placeholder="Enter Name")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"**{wk} Week**")
                
                # Times
                t_cols = st.columns([4, 1, 4])
                with t_cols[0]:
                    s_t = st.selectbox(f"Start {i}{wk}", hrs, key=f"s{i}{wk}")
                t_cols[1].markdown("<p style='padding-top:35px;'>to</p>", unsafe_allow_html=True)
                with t_cols[2]:
                    e_t = (datetime.strptime(s_t, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                    st.info(f"End: {e_t}")
                
                # Off Days
                o1 = st.selectbox(f"1st Off {i}{wk}", ["1st Day Off"] + days, key=f"o1{i}{wk}")
                st.toggle("Work 6th Day OT", key=f"do_ot1_{i}_{wk}", disabled=st.session_state.get(f"do_ot2_{i}_{wk}", False))
                
                o2 = st.selectbox(f"2nd Off {i}{wk}", ["2nd Day Off"] + [d for d in days if d != o1], key=f"o2{i}{wk}")
                st.toggle("Work 7th Day OT", key=f"do_ot2_{i}_{wk}", disabled=st.session_state.get(f"do_ot1_{i}_{wk}", False))
                
                if o1 == "1st Day Off" or o2 == "2nd Day Off": all_days_selected = False

                with st.expander("➕ Daily OT (Max 2h)"):
                    b_val = st.session_state[f"otb_{i}_{wk}"]
                    a_val = st.session_state[f"ota_{i}_{wk}"]
                    st.number_input("Before", 0, 2 - a_val, key=f"otb_{i}_{wk}")
                    st.number_input("After", 0, 2 - b_val, key=f"ota_{i}_{wk}")

            real_offs = []
            if o1 in days and not st.session_state[f"do_ot1_{i}_{wk}"]: real_offs.append(days.index(o1)+1)
            if o2 in days and not st.session_state[f"do_ot2_{i}_{wk}"]: real_offs.append(days.index(o2)+1)
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": sorted(real_offs)}

# --- 5. LOGIC & RESULTS ---
if st.button("🚀 Run Swap Check", use_container_width=True):
    if not all_days_selected:
        st.error("⚠️ No Days off selected. Please choose your days off for both weeks.")
    else:
        results = []
        for en in [1, 2]:
            c_key, n_key = f"e{en}_Current", f"e{en}_Next"
            # 12h Rest Math
            is_exempt = (7 in shift_data[c_key]["off"]) or (1 in shift_data[n_key]["off"])
            
            # Times
            dt_e = datetime(2026, 3, 28, datetime.strptime(shift_data[c_key]["e"], "%I %p").hour)
            if datetime.strptime(shift_data[c_key]["e"], "%I %p").hour < datetime.strptime(shift_data[c_key]["s"], "%I %p").hour:
                dt_e += timedelta(days=1)
            dt_e += timedelta(hours=st.session_state[f"ota_{en}_Current"])
            
            dt_s = datetime(2026, 3, 29, datetime.strptime(shift_data[n_key]["s"], "%I %p").hour)
            dt_s -= timedelta(hours=st.session_state[f"otb_{en}_Next"])
            
            gap = (dt_s - dt_e).total_seconds() / 3600
            
            # Streak Math
            l_off = shift_data[c_key]["off"][-1] if shift_data[c_key]["off"] else 0
            f_off = shift_data[n_key]["off"][0] if shift_data[n_key]["off"] else 8
            streak = (7 - l_off) + (f_off - 1)

            results.append({
                "name": st.session_state[f"un{en}"] or f"Employee {en}",
                "rest_pass": gap >= 12 or is_exempt,
                "rest_msg": "Exempted" if is_exempt else f"{gap:.1f}h gap",
                "streak_pass": streak <= 6,
                "streak_val": streak
            })

        all_pass = all(r["rest_pass"] and r["streak_pass"] for r in results)
        st.markdown(f"<div class='results-card' style='background-color:{'#1b5e20' if all_pass else '#b71c1c'}; color:white;'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center; color:white;'>{'✅ Swap Approved' if all_pass else '❌ Swap Rejected'}</h2>", unsafe_allow_html=True)
        for r in results:
            st.markdown(f"#### 👤 {r['name']}")
            st.markdown(f"<div class='status-line'><span>{'🟢' if r['rest_pass'] else '🔴'} Rest Rule</span> <span>{r['rest_msg']}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='status-line'><span>{'🟢' if r['streak_pass'] else '🔴'} Streak</span> <span>{r['streak_val']} Days Work</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="test-btn-container">', unsafe_allow_html=True)
st.button("🎲 Test Data", on_click=on_load_random)
st.markdown('</div>', unsafe_allow_html=True)
