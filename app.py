import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Class Tracker", layout="wide")

# ------------------------- #
# Initialize Data
# ------------------------- #
if "class_data" not in st.session_state:
    st.session_state.class_data = {
        "Monday": [
            {"subject": "Math", "teacher": "Mr. Sharma", "time": "09:00 AM"},
            {"subject": "Physics", "teacher": "Mrs. Singh", "time": "11:00 AM"},
            {"subject": "Computer", "teacher": "Mr. Khan", "time": "02:00 PM"},
        ],
        "Tuesday": [
            {"subject": "Chemistry", "teacher": "Dr. Patel", "time": "10:00 AM"},
            {"subject": "Biology", "teacher": "Ms. Rao", "time": "02:00 PM"},
        ],
        "Wednesday": [
            {"subject": "English", "teacher": "Mr. Verma", "time": "09:00 AM"},
            {"subject": "History", "teacher": "Ms. Kapoor", "time": "11:30 AM"},
        ],
        "Thursday": [
            {"subject": "Geography", "teacher": "Mr. Das", "time": "10:00 AM"},
            {"subject": "Art", "teacher": "Ms. Nair", "time": "01:00 PM"},
        ],
        "Friday": [
            {"subject": "Math", "teacher": "Mr. Sharma", "time": "09:00 AM"},
            {"subject": "PE", "teacher": "Coach Sharma", "time": "11:00 AM"},
        ],
        "Saturday": [
            {"subject": "Computer Lab", "teacher": "Mr. Khan", "time": "10:00 AM"},
        ],
    }

# ------------------------- #
# Helper Functions
# ------------------------- #
def timetable_to_df():
    rows = []
    for day, classes in st.session_state.class_data.items():
        for c in classes:
            rows.append({
                "Day": day,
                "Subject": c.get("subject", ""),
                "Teacher": c.get("teacher", ""),
                "Time": c.get("time", "")
            })
    return pd.DataFrame(rows, columns=["Day", "Subject", "Teacher", "Time"])

def add_class(day, subject, teacher, time_str):
    st.session_state.class_data[day].append(
        {"subject": subject, "teacher": teacher, "time": time_str}
    )
    st.success(f"Added: {subject} on {day} at {time_str}")
    st.rerun()

def delete_class(day, index):
    if 0 <= index < len(st.session_state.class_data[day]):
        st.session_state.class_data[day].pop(index)
        if not st.session_state.class_data[day]:
            del st.session_state.class_data[day]
        st.rerun()

# ------------------------- #
# Sidebar (Add + Filters)
# ------------------------- #
st.sidebar.header("➕ Add New Class")

day_choices = sorted(list(st.session_state.class_data.keys()))
new_day = st.sidebar.selectbox("Day", options=day_choices)
new_subject = st.sidebar.text_input("Subject")
new_teacher = st.sidebar.text_input("Teacher")
new_time = st.sidebar.text_input("Time (e.g. 10:30 AM)")

if st.sidebar.button("Add Class"):
    if new_subject.strip() and new_teacher.strip() and new_time.strip():
        add_class(new_day, new_subject.strip(), new_teacher.strip(), new_time.strip())
    else:
        st.sidebar.error("Fill all fields to add a class.")

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filters")

df_all = timetable_to_df()
days = ["All"] + sorted(df_all["Day"].unique().tolist())
subjects = ["All"] + sorted(df_all["Subject"].unique().tolist())
teachers = ["All"] + sorted(df_all["Teacher"].unique().tolist())

f_day = st.sidebar.selectbox("Day", days)
f_subject = st.sidebar.selectbox("Subject", subjects)
f_teacher = st.sidebar.selectbox("Teacher", teachers)

# ------------------------- #
# Tabs
# ------------------------- #
tab1, tab2, tab3 = st.tabs(["🏠 Dashboard", "📅 Timetable", "📤 Download CSV"])

# ------------------------- #
# Dashboard Tab
# ------------------------- #
with tab1:
    st.header("Upcoming Classes (Next 7 Days)")
    today = datetime.today()
    next_7 = [(today + timedelta(days=i)).strftime("%A") for i in range(7)]

    found = False
    for day in next_7:
        if day in st.session_state.class_data and st.session_state.class_data[day]:
            found = True
            st.subheader(day)
            st.table(pd.DataFrame(st.session_state.class_data[day]))
            for i, cls in enumerate(st.session_state.class_data[day]):
                if st.button(f"🗑 Delete {cls['subject']} ({day})", key=f"del_{day}_{i}"):
                    delete_class(day, i)
    if not found:
        st.info("No upcoming classes in the next 7 days.")

    st.markdown("---")
    st.subheader("Search Classes by Day")
    search_day = st.text_input("Enter day (e.g. Monday)")
    if search_day:
        d = search_day.strip().capitalize()
        if d in st.session_state.class_data:
            st.table(pd.DataFrame(st.session_state.class_data[d]))
        else:
            st.warning("No classes found for that day.")

# ------------------------- #
# Timetable Tab
# ------------------------- #
with tab2:
    st.header("Full Weekly Timetable")
    df = timetable_to_df()

    # Apply filters
    if f_day != "All":
        df = df[df["Day"] == f_day]
    if f_subject != "All":
        df = df[df["Subject"] == f_subject]
    if f_teacher != "All":
        df = df[df["Teacher"] == f_teacher]

    if df.empty:
        st.info("No data for selected filters.")
    else:
        st.dataframe(df.reset_index(drop=True), use_conta
