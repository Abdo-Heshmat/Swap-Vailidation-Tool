import streamlit as st
from datetime import datetime, timedelta

# Helper to turn selections into real timestamps
def get_dt(week_type, day_idx, time_str):
    # Reference: Sunday of Current Week = March 22, 2026
    # Reference: Sunday of Next Week = March 29, 2026
    base_date = datetime(2026, 3, 22)
    week_offset = 0 if week_type == "Current Week" else 7
    target_date = base_date + timedelta(days=day_idx + week_offset)
    time_obj = datetime.strptime(time_str, "%I %p").time()
    return datetime.combine(target_date, time_obj)

st.set_page_config(layout="wide", page_title="Swap Validator Pro")

# Header & Branding
st.title("🛡️ Smart Shift Swap Validator")
st.markdown("---")

# Global Shift Settings
is_ramadan = st.checkbox("🌙 Ramadan Mode (7-hour shifts)")
duration = 7 if is_ramadan else 9
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)

# Employee 1 Input
with col1:
    st.subheader("👤 Employee 1")
    name1 = st.text_input("Name", "Ahmed", key="n1")
    w1 = st.radio("Week Selection", ["Current Week", "Next Week"], key="w1", horizontal=True)
    d1 = st.selectbox("Day of Shift", days, index=1, key="d1")
    s1 = st.selectbox("Start Time", hours, index=9, key="s1")
    
    dt1_start = get_dt(w1, days.index(d1), s1)
    dt1_end = dt1_start + timedelta(hours=duration)
    st.info(f"📍 Shift: {dt1_end.strftime('%A (%b %d)')} | Ends: {dt1_end.strftime('%I %p')}")

# Employee 2 Input
with col2:
    st.subheader("👤 Employee 2")
    name2 = st.text_input("Name", "Mohamed", key="n2")
    w2 = st.radio("Week Selection", ["Current Week", "Next Week"], key="w2", horizontal=True)
    d2 = st.selectbox("Day of Shift", days, index=2, key="d2")
    s2 = st.selectbox("Start Time", hours, index=14, key="s2")
    
    dt2_start = get_dt(w2, days.index(d2), s2)
    dt2_end = dt2_start + timedelta(hours=duration)
    st.info(f"📍 Shift: {dt2_end.strftime('%A (%b %d)')} | Ends: {dt2_end.strftime('%I %p')}")

st.divider()

# --- VALIDATION LOGIC ---
if st.button("🚀 Run Swap Validation", use_container_width=True):
    # Sort shifts by start time to find the gap correctly
    shifts = sorted([(dt1_start, dt1_end, name1), (dt2_start, dt2_end, name2)])
    
    first_end = shifts[0][1]
    second_start = shifts[1][0]
    
    # Calculate differences
    time_diff = second_start - first_end
    total_seconds = time_diff.total_seconds()
    gap_hours = total_seconds / 3600
    gap_days = abs((dt2_start - dt1_start).days)

    is_valid = True
    error_messages = []

    # 1. Check 12-Hour Rest Rule
    if gap_hours < 12:
        is_valid = False
        error_messages.append(f"⚠️ **Rest Violation:** Only **{max(0, gap_hours):.1f} hours** of rest between these shifts. (Minimum required: 12H)")

    # 2. Check 7-Day Limit Rule
    if gap_days > 7:
        is_valid = False
        error_messages.append(f"⚠️ **Timeline Violation:** The shifts are **{gap_days} days** apart. (Maximum allowed: 7 days)")

    # 3. Overlap Check
    if first_end > second_start:
        is_valid = False
        error_messages.append("⚠️ **Collision Error:** These shifts overlap in time. A swap is physically impossible.")

    # Final Output Display
    if is_valid:
        st.success(f"✅ **Swap Approved!** The gap between shifts is {gap_hours:.1f} hours.")
        st.balloons()
    else:
        st.error("🚫 **Swap Rejected**")
        st.warning("The swap cannot be completed due to the following reasons:")
        for msg in error_messages:
            st.write(msg)

st.markdown("<br><br>", unsafe_allow_name=True)
st.info("Created by Abdelrahman heshmat @abheshma")
