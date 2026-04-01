import streamlit as st
from datetime import datetime, timedelta

# Helper function to calculate the 9-hour (or 7-hour) shift end
def calculate_end_time(start_time_str, duration):
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=duration)
    return end_dt.strftime("%I %p")

# Page Config
st.set_page_config(layout="wide", page_title="Shift Swap Validator")

# Custom CSS to center the app and style the green boxes
st.markdown("""
    <style>
    .stApp {
        max-width: 1100px;
        margin: 0 auto;
    }
    .green-box {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-top: 5px;
    }
    .week-header {
        text-align: center;
        background-color: #f8f9fa;
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔄 Shift Swap Validation Tool")
st.markdown("---")

# Ramadan Toggle (7 hours)
is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
shift_duration = 7 if is_ramadan else 9

# Data lists
days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

# Create two main columns for the employees
col1, col2 = st.columns(2)

# --- EMPLOYEE 1 COLUMN ---
with col1:
    emp1_name = st.text_input("Employee 1 Name", value="John", key="name1")
    
    for week in ["Current Week", "Next Week"]:
        with st.container(border=True):
            st.markdown(f"<div class='week-header'>📅 <b>{week}</b></div>", unsafe_allow_html=True)
            
            # Shift Timing Row
            t_col1, t_col2, t_col3 = st.columns([3, 1, 3])
            with t_col1:
                s1 = st.selectbox("Shift Start", hours, index=9, key=f"s1_{week}")
            with t_col2:
                st.write("<br><center>to</center>", unsafe_allow_html=True)
            with t_col3:
                e1 = calculate_end_time(s1, shift_duration)
                st.write("Shift End")
                st.markdown(f"<div class='green-box'>{e1}</div>", unsafe_allow_html=True)
            
            # Days Off Row
            st.write("**Days Off:**")
            do_col1, do_col2 = st.columns(2)
            with do_col1:
                st.selectbox("Day 1", days_of_week, index=0, key=f"d1a_{week}", label_visibility="collapsed")
            with do_col2:
                st.selectbox("Day 2", days_of_week, index=1, key=f"d1b_{week}", label_visibility="collapsed")

# --- EMPLOYEE 2 COLUMN ---
with col2:
    emp2_name = st.text_input("Employee 2 Name", value="Mike", key="name2")
    
    for week in ["Current Week", "Next Week"]:
        with st.container(border=True):
            st.markdown(f"<div class='week-header'>📅 <b>{week}</b></div>", unsafe_allow_html=True)
            
            # Shift Timing Row
            t_col1, t_col2, t_col3 = st.columns([3, 1, 3])
            with t_col1:
                s2 = st.selectbox("Shift Start", hours, index=14, key=f"s2_{week}")
            with t_col2:
                st.write("<br><center>to</center>", unsafe_allow_html=True)
            with t_col3:
                e2 = calculate_end_time(s2, shift_duration)
                st.write("Shift End")
                st.markdown(f"<div class='green-box'>{e2}</div>", unsafe_allow_html=True)
            
            # Days Off Row
            st.write("**Days Off:**")
            do_col1, do_col2 = st.columns(2)
            with do_col1:
                st.selectbox("Day 1", days_of_week, index=4, key=f"d2a_{week}", label_visibility="collapsed")
            with do_col2:
                st.selectbox("Day 2", days_of_week, index=6, key=f"d2b_{week}", label_visibility="collapsed")

st.markdown("---")
st.caption("Created by Abdelrahman heshmat @abheshma")
