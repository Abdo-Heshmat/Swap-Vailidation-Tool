import streamlit as st
from datetime import datetime, timedelta

# --- Helper Functions ---
def calculate_end_time(start_time_str, duration):
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=duration)
    return end_dt.strftime("%I %p")

def get_dt(week_type, day_idx, time_str):
    # Reference Sunday: March 22, 2026
    base_date = datetime(2026, 3, 22) 
    offset = 0 if week_type == "Current Week" else 7
    target_date = base_date + timedelta(days=day_idx + offset)
    time_obj = datetime.strptime(time_str, "%I %p").time()
    return datetime.combine(target_date, time_obj)

# --- UI Styling ---
st.set_page_config(layout="wide", page_title="Swap Validator Pro")

st.markdown("""
    <style>
    .stApp { max-width: 1200px; margin: 0 auto; }
    .shift-box {
        background-color: #e8f5e9; color: #2e7d32;
        padding: 10px; border-radius: 8px; border: 1px solid #c8e6c9;
        text-align: center; font-weight: bold; font-size: 1.1rem;
    }
    .status-container {
        padding: 25px; border-radius: 15px; margin-top: 20px;
    }
    .approved { background-color: #d4edda; border: 2px solid #c3e6cb; color: #155724; }
    .rejected { background-color: #f8d7da; border: 2px solid #f5c6cb; color: #721c24; }
    .reason-text { font-size: 0.95rem; margin-left: 20px; color: #444; }
    </style>
    """, unsafe_allow_html=True)

# --- Top Header ---
st.markdown("<h1 style='text-align: center;'>🛡️ Swap Validation Tool</h1>", unsafe_allow_html=True)

# Global Ramadan Toggle
is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9

day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)

# --- Employee 1 ---
with col1:
    st.markdown("<h3 style='text-align: center;'>👤 Employee 1</h3>", unsafe_allow_html=True)
    name1 = st.text_input("E1 Name", "John", key="n1", label_visibility="collapsed")
    
    for week in ["Current Week", "Next Week"]:
        with st.container(border=True):
            st.markdown(f"<p style='text-align: center;'>🗓️ <b>{week}</b></p>", unsafe_allow_html=True)
            t_col1, t_col2, t_col3 = st.columns([3, 1, 3])
            with t_col1:
                s1 = st.selectbox("Start", hours, index=9, key=f"s1_{week}")
            with t_col2:
                st.write("<br><center>to</center>", unsafe_allow_html=True)
            with t_col3:
                e1 = calculate_end_time(s1, duration)
                st.write("Shift End")
                st.markdown(f"<div class='shift-box'>{e1}</div>", unsafe_allow_html=True)
            
            st.write("Days Off:")
            d1_col1, d1_col2 = st.columns(2)
            d1_col1.selectbox("Off 1", ["First Day off"] + day_list, key=f"d1a_{week}", label_visibility="collapsed")
            d1_col2.selectbox("Off 2", ["Second Day off"] + day_list, key=f"d1b_{week}", label_visibility="collapsed")

# --- Employee 2 ---
with col2:
    st.markdown("<h3 style='text-align: center;'>👤 Employee 2</h3>", unsafe_allow_html=True)
    name2 = st.text_input("E2 Name", "Mike", key="n2", label_visibility="collapsed")
    
    for week in ["Current Week", "Next Week"]:
        with st.container(border=True):
            st.markdown(f"<p style='text-align: center;'>🗓️ <b>{week}</b></p>", unsafe_allow_html=True)
            t_col1, t_col2, t_col3 = st.columns([3, 1, 3])
            with t_col1:
                s2 = st.selectbox("Start", hours, index=14, key=f"s2_{week}")
            with t_col2:
                st.write("<br><center>to</center>", unsafe_allow_html=True)
            with t_col3:
                e2 = calculate_end_time(s2, duration)
                st.write("Shift End")
                st.markdown(f"<div class='shift-box'>{e2}</div>", unsafe_allow_html=True)
            
            st.write("Days Off:")
            d2_col1, d2_col2 = st.columns(2)
            d2_col1.selectbox("Off 1", ["First Day off"] + day_list, key=f"d2a_{week}", label_visibility="collapsed")
            d2_col2.selectbox("Off 2", ["Second Day off"] + day_list, key=f"d2b_{week}", label_visibility="collapsed")

st.divider()

# --- VALIDATION BUTTON ---
if st.button("✅ Check the Validation", use_container_width=True):
    # Logic: Checking rest between Employee 1's Current Week shift and Next Week shift
    dt1_end = get_dt("Current Week", 1, calculate_end_time(st.session_state.s1_Current_Week, duration))
    dt2_start = get_dt("Current Week", 2, st.session_state.s2_Current_Week)
    
    rest_hours = (dt2_start - dt1_end).total_seconds() / 3600
    
    if rest_hours >= 21:
        st.markdown(f"""
            <div class='status-container approved'>
                <h2 style='text-align: center;'>✅ Swap Approved</h2>
                <p style='text-align: center;'>Swap between <b>{name1}</b> and <b>{name2}</b></p>
                <hr>
                <p>✔️ {name1}: {rest_hours:.1f} hours rest ✅</p>
                <p class='reason-text'>{st.session_state.s1_Current_Week} to {st.session_state.s2_Current_Week} = {rest_hours:.1f} hours</p>
            </div>
        """, unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown(f"""
            <div class='status-container rejected'>
                <h2 style='text-align: center;'>❌ Swap Rejected</h2>
                <p style='text-align: center;'>Swap between <b>{name1}</b> and <b>{name2}</b></p>
                <hr>
                <p>❌ {name1}: Only {rest_hours:.1f} hours rest</p>
                <p class='reason-text'>Required: 21 Hours | Actual: {rest_hours:.1f} Hours</p>
                <p>❌ EXCEEDS REST LIMIT!</p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br><center><b>Created by Abdelrahman heshmat @abheshma</b></center>", unsafe_allow_html=True)
