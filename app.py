# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Class Tracker", layout="wide")

# -------------------------
# In-memory initial data
# -------------------------
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

# -------------------------
# Helpers
# -------------------------
def timetable_to_df():
    """Flatten the nested dict into a DataFrame with columns Day, Subject, Teacher, Time."""
    rows = []
    for day, classes in st.session_state.class_data.items():
        for c in classes:
            rows.append({
                "Day": day,
                "Subject": c.get("subject", ""),
                "Teacher": c.get("teacher", ""),
                "Time": c.get("time", "")
            })
    df = pd.DataFrame(rows)
    # Keep stable ordering
    if not df.empty:
        df = df[["Day", "Subject", "Teacher", "Time"]]
    else:
        df = pd.DataFrame(columns=["Day", "Subject", "Teacher", "Time"])
    return df

def add_class(day, subject, teacher, time_str):
    if day not in st.session_state.class_data:
        st.session_state.class_data[day] = []
    st.session_state.class_data[day].append({"subject": subject, "teacher": teacher, "time": time_str})
    st.success(f"Added: {subject} on {day} at {time_str}")
    st.rerun()

def delete_class(day, index):
    try:
        st.session_state.class_data[day].pop(index)
        if not st.session_state.class_data[day]:
            del st.session_state.class_data[day]
    except Exception:
        pass
    st.rerun()

# -------------------------
# UI: Sidebar - Add Class & Filters
# -------------------------
st.sidebar.header("➕ Add New Class")

day_choices = sorted(list(st.session_state.class_data.keys()))
# allow new day creation
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
st.sidebar.header("🔍 Filters (affect Timetable & Download)")

# Build options for filters safely (deduplicate)
df_full = timetable_to_df()
all_days = ["All"] + sorted(df_full["Day"].unique().tolist())
all_subjects = ["All"] + sorted(df_full["Subject"].unique().tolist())
all_teachers = ["All"] + sorted(df_full["Teacher"].unique().tolist())

selected_day = st.sidebar.selectbox("Day", options=all_days, index=0)
selected_subject = st.sidebar.selectbox("Subject", options=all_subjects, index=0)
selected_teacher = st.sidebar.selectbox("Teacher", options=all_teachers, index=0)

# -------------------------
# Main: Tabs
# -------------------------
tab1, tab2, tab3 = st.tabs(["🏠 Dashboard", "📅 Timetable", "📤 Download & Export"])

# --- Dashboard Tab ---
with tab1:
    st.header("Upcoming (Next 7 Days by Weekday)")
    # compute list of names for next 7 calendar days (weekday names)
    today = datetime.today()
    next_7 = [(today + timedelta(days=i)).strftime("%A") for i in range(7)]
    found = False
    for weekday in next_7:
        entries = st.session_state.class_data.get(weekday, [])
        if entries:
            found = True
            st.subheader(f"{weekday}")
            rows = []
            for i, e in enumerate(entries):
                rows.append({"Subject": e["subject"], "Teacher": e["teacher"], "Time": e["time"], "index": i})
            df_display = pd.DataFrame(rows).drop(columns=["index"])
            st.table(df_display)
            # Allow deletion per entry
            cols = st.columns(len(entries))
            for i, e in enumerate(entries):
                if st.button(f"Delete {weekday} - {e['subject']}", key=f"del_{weekday}_{i}"):
                    delete_class(weekday, i)
    if not found:
        st.info("No classes scheduled in the upcoming 7 days.")

    st.markdown("---")
    st.subheader("Quick Search by Day")
    q = st.text_input("Enter day name (e.g., Monday)")
    if q:
        q_name = q.strip().capitalize()
        if q_name in st.session_state.class_data:
            st.write(f"Classes on {q_name}:")
            st.table(pd.DataFrame(st.sess
