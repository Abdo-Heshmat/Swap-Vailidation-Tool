import streamlit as st
from datetime import datetime, timedelta
import random

# --- 1. THEME & INITIALIZATION ---
if 'theme' not in st.session_state: st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Define Professional Reactive Palettes
if st.session_state.theme == 'dark':
    bg, box, txt, brd, accent = "#0e1117", "#1e2129", "#ffffff", "#3e4451", "#4f46e5"
    input_txt = "#ffffff"
else:
    # Clean, High-Contrast Light Mode
    bg, box, txt, brd, accent = "#f8fafc", "#ffffff", "#0f172a", "#cbd5e1", "#4f46e5"
    input_txt = "#0f172a" # Dark text inside white boxes

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
            st.session_state[f"do_ot1_{i}_{wk}"] = False 
            st.session_state[f"do_ot2_{i}_{wk}"] = False
            st.session_state[f"otb_{i}_{wk}"] = 0
            st.session_state[f"ota_{i}_{wk}"] = 0

def get_dt(day_idx, time_str, is_end=False, s_time_str=None):
    base_sunday = datetime(2026, 1, 4, 0, 0) 
    dt = base_sunday + timedelta(days=day_idx-1)
    t_obj = datetime.strptime(time_str, "%I %p")
    final_dt = datetime.combine(dt.date(), t_obj.time())
    if is_end and s_time_str:
        s_hour = datetime.strptime(s_time_str, "%I %p").hour
        e_hour = t_obj.hour
        if e_hour <= s_hour: final_dt += timedelta(days=1)
    return final_dt

# --- 3. UI STYLING (FULL RESET FOR LIGHT MODE) ---
st.markdown(f"""
    <style>
    /* Main App Background */
    .stApp {{ background-color: {bg}; color: {txt}; }}
    
    /* Text Readability */
    h1, h2, h3, p, span, label, div {{ color: {txt} !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}

    /* Fix Input Boxes & Buttons for Light Mode */
    div[data-testid="stVerticalBlockBorderWrapper"], 
    .stSelectbox div[data-baseweb="select"],
    input[type="text"], 
    .unified-box, 
    .stNumberInput input,
    div[data-testid="stExpander"] {{
        background-color: {box} !important; 
        color: {input_txt} !important;
        border: 1px solid {brd} !important; 
        border-radius: 12px !important;
    }}

    /* Ensure dropdown text is visible */
    div[data-baseweb="select"] span {{ color: {input_txt} !important; }}
    
    /* Center text in inputs */
    input {{ text-align: center !important; }}

    .emp-header {{ text-align: center; font-weight: 800; font-size: 22px; margin-bottom: 15px; color: {accent} !important; }}
    
    .unified-box {{ 
        height: 42px; display: flex; align-items: center; justify-content: center; 
        font-weight: bold; border: 1px solid {brd}; 
    }}

    /* Main Button Styling */
    .stButton>button {{
        background-color: {accent} !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100%;
        padding: 10px;
        font-weight: bold;
    }}

    /* Result Card Styling */
    .results-card {{ padding: 25px; border-radius: 20px; margin-top: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
    </style>
    """, unsafe_allow_html=True)

# Layout
l_col, h_col, r_col = st.columns([1, 8, 1])
with r_col: st.button("☀️" if st.session_state.theme == 'dark' else "🌙", on_click=toggle_theme)
with h_col: st.markdown(f'<h1 style="text-align:center;">👤🔁👤 Smart Swap Validator Pro</h1>', unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h)")
dur = 7 if is_ramadan else 9

# --- 4. MAIN INTERFACE ---
shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"<div class='emp-header'>Employee {i}</div>", unsafe_allow_html=True)
        name_input = st.text_input(f"Name {i}", key=f"un{i}", placeholder=f"Enter Name", label_visibility="collapsed")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"<p style='text-align:center; font-weight:bold; margin-bottom:5px;'>🗓️ {wk} Week</p>", unsafe_allow_html=True)
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
                
                with st.expander("➕ Daily OT (Max 2h)"):
                    otb = st.number_input(f"Before {i}{wk}", 0, 2, key=f"otb_{i}_{wk}")
                    ota = st.number_input(f"After {i}{wk}", 0, 2, key=f"ota_{i}_{wk}")

            real_offs = []
            if o1 in days and not ot1: real_offs.append(days.index(o1)+1)
            if o2 in days and not ot2: real_offs.append(days.index(o2)+1)
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": real_offs, "otb": otb, "ota": ota, "name": name_input or f"Emp {i}"}

st.divider()

# --- 5. VALIDATOR ---
if st.button("🚀 Run Swap
