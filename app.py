import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Class Tracker", layout="wide")

# --- Initialize in-memory data ---
if "class_data" not in st.session_state:
    st.session_state.class_data = {
        "Monday": [
            {"subject": "Math", "teacher": "Mr. Sharma", "time": "9:00 AM"},
            {"subject": "Physics", "teacher": "Mrs. Singh", "time": "11:00 AM"},
        ],
        "Tuesday": [
            {"subject": "Chemistry", "teacher": "Dr. Patel", "time": "10:00 AM"},
            {"subject": "Biology", "teacher": "Ms. Rao", "time": "2:00 PM"},
        ],
        "Wednesday": [
            {"subject": "English", "teacher": "Mr. Verma", "time": "9:00 AM"},
            {"subject": "Computer", "teacher": "Mr. Khan", "time": "12:00 PM"},
        ],
        "Thursday": [
            {"subject": "History", "teacher": "Ms. Kapoor", "time": "10:00 AM"},
            {"subject": "Geography", "teacher": "Mr. Das", "time": "1:00 PM"},
        ],
        "Friday": [
            {"subject": "Math", "teacher": "Mr. Sharma", "time": "9:00 AM"},
            {"subject": "Art", "teacher": "Ms. Nair", "time": "11:00 AM"},
        ],
    }

# --- Helper: Convert to DataFrame ---
def get_timetable_df():
    rows = []
    for day, classes in st.session_state.class_data.items():
        for c in classes:
            rows.append({
                "Day": day,
                "Subject": c["subject"],
                "Teacher": c["teacher"],
                "Time": c["time"]
            })
    return pd.DataFrame(rows)

# --- Header ---
st.title("📘 Class Tracker Dashboard")

# --- Sidebar filters ---
st.sidebar.header("🔍 Filters")

day_filter = st.sidebar.selectbox("Filter by Day", ["All"] + list(st.session_state.class_data.keys()))
subjects = sorted({cls["subject"] for d in st.session_state.class_data.values() for cls in d})
teachers = sorted({cls["teacher"] for d in st.session_state.class_data.values() for cls in d})

subject_filter = st.sidebar.selectbox("Filter by Subject", ["All"] + subjects)
teacher_filter = st.sidebar.selectbox("Filter by Teacher", ["All"] + teachers)

# --- Add new class section ---
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Add New Class")

new_day = st.sidebar.selectbox("Day", list(st.session_state.class_data.keys()))
new_subject = st.sidebar.text_input("Subject")
new_teacher = st.sidebar.text_input("Teacher")
new_time = st.sidebar.text_input("Time (e.g. 10:00 AM)")

if st.sidebar.button("Add Class"):
    if new_subject and new_teacher and new_time:
        st.session_state.class_data[new_day].append({
            "subject": new_subject,
            "teacher": new_teacher,
            "time": new_time
        })
        st.success(f"Added class: {new_subject} on {new_day}")
        st.rerun()
    else:
        st.warning("Please fill all fields.")

# --- Main dashboard ---
tab1, tab2, tab3 = st.tabs(["🏠 Dashboard", "📅 Timetable", "📤 Download CSV"])

# --- Dashboard ---
with tab1:
    st.subheader("Upcoming Classes (Next 7 Days)")

    today = datetime.now()
    next_week = [(today + timedelta(days=i)).strftime("%A") for i in range(7)]

    found_any = False
    for day in next_week:
        if day in st.session_state.class_data and st.session_state.class_data[day]:
            st.markdown(f"### {day}")
            st.table(pd.DataFrame(st.session_state.class_data[day]))
            found_any = True

    if not found_any:
        st.info("No upcoming classes found in the next 7 days.")

    # Search by day
    st.subheader("🔍 Search Classes by Day")
    search_day = st.text_input("Enter a day (e.g., Monday)")
    if search_day:
        search_day = search_day.strip().capitalize()
        if search_day in st.session_state.class_data:
            st.write(f"**Classes on {search_day}:**")
            st.table(pd.DataFrame(st.session_state.class_data[search_day]))
        else:
            st.error("Invalid day name or no classes found.")

# --- Timetable ---
with tab2:
    st.subheader("Full Weekly Timetable")

    df = get_timetable_df()
    if day_filter != "All":
        df = df[df["Day"] == day_filter]
    if subject_filter != "All":
        df = df[df["Subject"] == subject_filter]
    if teacher_filter != "All":
        df = df[df["Teacher"] == teacher_filter]

    st.dataframe(df, use_container_width=True)

# --- CSV Download ---
with tab3:
    st.subheader("📤 Download Timetable as CSV")
    df = get_timetable_df()
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "timetable.csv", "text/csv")
