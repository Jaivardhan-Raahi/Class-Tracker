import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Class Tracker", layout="wide")

# --- Local In-Memory Data ---
if "class_data" not in st.session_state:
    st.session_state.class_data = {
        "2025-11-07": [
            {"subject": "Mathematics", "time": "9:00 AM", "teacher": "Mr. Raj"},
            {"subject": "Physics", "time": "10:30 AM", "teacher": "Dr. Mehta"},
            {"subject": "Chemistry", "time": "1:00 PM", "teacher": "Ms. Kaur"},
            {"subject": "Computer Science", "time": "3:00 PM", "teacher": "Mr. Kumar"},
        ],
        "2025-11-08": [
            {"subject": "English", "time": "8:30 AM", "teacher": "Ms. Verma"},
            {"subject": "Biology", "time": "11:00 AM", "teacher": "Dr. Singh"},
            {"subject": "History", "time": "2:00 PM", "teacher": "Mr. Ali"},
        ],
        "2025-11-09": [
            {"subject": "Geography", "time": "9:00 AM", "teacher": "Ms. Iyer"},
            {"subject": "Political Science", "time": "11:30 AM", "teacher": "Mr. Sen"},
        ],
        "2025-11-10": [
            {"subject": "Physics Lab", "time": "9:00 AM", "teacher": "Dr. Mehta"},
            {"subject": "Mathematics", "time": "11:00 AM", "teacher": "Mr. Raj"},
            {"subject": "Physical Education", "time": "1:30 PM", "teacher": "Coach Sharma"},
        ],
        "2025-11-11": [
            {"subject": "Chemistry", "time": "9:30 AM", "teacher": "Ms. Kaur"},
            {"subject": "English Literature", "time": "11:30 AM", "teacher": "Ms. Verma"},
            {"subject": "Computer Lab", "time": "2:00 PM", "teacher": "Mr. Kumar"},
        ],
    }

# --- Helper Functions ---
def get_upcoming_classes():
    today = datetime.today().date()
    upcoming = {}
    for date_str, classes in st.session_state.class_data.items():
        try:
            class_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if today <= class_date <= today + timedelta(days=7):
                upcoming[date_str] = classes
        except ValueError:
            continue
    return upcoming


def add_class(date, subject, time, teacher):
    date_str = date.strftime("%Y-%m-%d")
    if date_str not in st.session_state.class_data:
        st.session_state.class_data[date_str] = []
    st.session_state.class_data[date_str].append(
        {"subject": subject, "time": time, "teacher": teacher}
    )
    st.rerun()


def delete_class(date_str, index):
    st.session_state.class_data[date_str].pop(index)
    if not st.session_state.class_data[date_str]:
        del st.session_state.class_data[date_str]
    st.rerun()


def flatten_class_data(filter_subject=None, filter_teacher=None):
    rows = []
    for date_str, classes in st.session_state.class_data.items():
        for cls in classes:
            if (filter_subject and cls["subject"] != filter_subject) or (
                filter_teacher and cls["teacher"] != filter_teacher
            ):
                continue
            rows.append({
                "Date": date_str,
                "Day": datetime.strptime(date_str, "%Y-%m-%d").strftime("%A"),
                "Subject": cls["subject"],
                "Time": cls["time"],
                "Teacher": cls["teacher"]
            })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        df.sort_values(by=["Date", "Time"], inplace=True)
    return df


# --- UI Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Add Class", "🔍 Search & Filter", "📥 Download"])

# --- Dashboard Tab ---
with tab1:
    st.header("📅 Upcoming Week's Classes")
    upcoming = get_upcoming_classes()
    if upcoming:
        for date_str, classes in sorted(upcoming.items()):
            weekday = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
            st.markdown(f"### {date_str} ({weekday})")
            df = pd.DataFrame(classes)
            st.dataframe(df, use_container_width=True)

            # delete controls
            for i, cls in enumerate(classes):
                col1, col2, col3 = st.columns([4, 2, 1])
                with col3:
                    if st.button("🗑️ Delete", key=f"del_{date_str}_{i}"):
                        delete_class(date_str, i)
    else:
        st.info("No upcoming classes found for the next 7 days.")


# --- Add Class Tab ---
with tab2:
    st.header("➕ Add New Class")
    date_input = st.date_input("Select Class Date", datetime.today())
    subject = st.text_input("Subject")
    time = st.text_input("Time (e.g., 10:30 AM)")
    teacher = st.text_input("Teacher Name")

    if st.button("Add Class"):
        if subject and time and teacher:
            add_class(date_input, subject, time, teacher)
            st.success("✅ Class added successfully!")
        else:
            st.error("⚠️ Please fill all fields before adding.")


# --- Search & Filter Tab ---
with tab3:
    st.header("🔍 Search & Filter Classes")
    search_date = st.date_input("Select a date to view classes")
    search_str = search_date.strftime("%Y-%m-%d")

    all_subjects = sorted(
        list({cls["subject"] for d in st.session_state.class_data.values() for cls in d})
    )
    all_teachers = sorted(
        list({cls["teacher"] for d in st.session_state.class_data.values() for cls in d})
    )

    col1, col2 = st.columns(2)
    with col1:
        subject_filter = st.selectbox("Filter by Subject", ["All"] + all_subjects)
    with col2:
        teacher_filter = st.selectbox("Filter by Teacher", ["All"] + all_teachers)

    subject_filter = None if subject_filter == "All" else subject_filter
    teacher_filter = None if teacher_filter == "All" else teacher_filter

    df = flatten_class_data(subject_filter, teacher_filter)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No classes found matching your filters.")

    if search_str in st.session_state.class_data:
        st.markdown(f"### Classes on {search_str} ({search_date.strftime('%A')})")
        df_date = pd.DataFrame(st.session_state.class_data[search_str])
        st.dataframe(df_date, use_container_width=True)
    else:
        st.info("No classes scheduled for this date.")


# --- Download Tab ---
with tab4:
    st.header("📥 Download Timetable")

    all_subjects = sorted(
        list({cls["subject"] for d in st.session_state.class_data.values() for cls in d})
    )
    all_teachers = sorted(
        list({cls["teacher"] for d in st.session_state.class_data.values() for c
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Class Tracker", layout="wide")

# --- Local In-Memory Storage ---
if "class_data" not in st.session_state:
    st.session_state.class_data = {
        "2025-11-07": [
            {"subject": "Mathematics", "time": "9:00 AM", "teacher": "Mr. Raj"},
            {"subject": "Physics", "time": "10:30 AM", "teacher": "Dr. Mehta"},
            {"subject": "Chemistry", "time": "1:00 PM", "teacher": "Ms. Kaur"},
            {"subject": "Computer Science", "time": "3:00 PM", "teacher": "Mr. Kumar"},
        ],
        "2025-11-08": [
            {"subject": "English", "time": "8:30 AM", "teacher": "Ms. Verma"},
            {"subject": "Biology", "time": "11:00 AM", "teacher": "Dr. Singh"},
            {"subject": "History", "time": "2:00 PM", "teacher": "Mr. Ali"},
        ],
        "2025-11-09": [
            {"subject": "Geography", "time": "9:00 AM", "teacher": "Ms. Iyer"},
            {"subject": "Political Science", "time": "11:30 AM", "teacher": "Mr. Sen"},
        ],
        "2025-11-10": [
            {"subject": "Physics Lab", "time": "9:00 AM", "teacher": "Dr. Mehta"},
            {"subject": "Mathematics", "time": "11:00 AM", "teacher": "Mr. Raj"},
            {"subject": "Physical Education", "time": "1:30 PM", "teacher": "Coach Sharma"},
        ],
        "2025-11-11": [
            {"subject": "Chemistry", "time": "9:30 AM", "teacher": "Ms. Kaur"},
            {"subject": "English Literature", "time": "11:30 AM", "teacher": "Ms. Verma"},
            {"subject": "Computer Lab", "time": "2:00 PM", "teacher": "Mr. Kumar"},
        ],
        "2025-11-12": [
            {"subject": "Economics", "time": "9:00 AM", "teacher": "Mr. Reddy"},
            {"subject": "Mathematics", "time": "11:30 AM", "teacher": "Mr. Raj"},
            {"subject": "History", "time": "2:00 PM", "teacher": "Mr. Ali"},
        ],
        "2025-11-13": [
            {"subject": "Physics", "time": "8:30 AM", "teacher": "Dr. Mehta"},
            {"subject": "Computer Science", "time": "10:00 AM", "teacher": "Mr. Kumar"},
            {"subject": "English", "time": "1:30 PM", "teacher": "Ms. Verma"},
            {"subject": "Mathematics", "time": "3:00 PM", "teacher": "Mr. Raj"},
        ],
    }

# --- Helper Functions ---
def get_upcoming_classes():
    today = datetime.today().date()
    upcoming = {}
    for date_str, classes in st.session_state.class_data.items():
        try:
            class_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if today <= class_date <= today + timedelta(days=7):
                upcoming[date_str] = classes
        except ValueError:
            continue
    return upcoming


def add_class(date, subject, time, teacher):
    date_str = date.strftime("%Y-%m-%d")
    if date_str not in st.session_state.class_data:
        st.session_state.class_data[date_str] = []
    st.session_state.class_data[date_str].append(
        {"subject": subject, "time": time, "teacher": teacher}
    )
    st.rerun()


def flatten_class_data():
    rows = []
    for date_str, classes in st.session_state.class_data.items():
        for cls in classes:
            rows.append({
                "Date": date_str,
                "Day": datetime.strptime(date_str, "%Y-%m-%d").strftime("%A"),
                "Subject": cls["subject"],
                "Time": cls["time"],
                "Teacher": cls["teacher"]
            })
    return pd.DataFrame(rows)


# --- Sidebar: Add New Class ---
st.sidebar.header("➕ Add New Class")
date_input = st.sidebar.date_input("Select Class Date", datetime.today())
subject = st.sidebar.text_input("Subject")
time = st.sidebar.text_input("Time (e.g., 10:30 AM)")
teacher = st.sidebar.text_input("Teacher Name")

if st.sidebar.button("Add Class"):
    if subject and time and teacher:
        add_class(date_input, subject, time, teacher)
        st.sidebar.success("✅ Class added successfully!")
    else:
        st.sidebar.error("⚠️ Please fill all fields before adding.")


# --- Main Dashboard ---
st.title("📚 Class Tracker Dashboard")

# Upcoming classes
st.subheader("📅 Upcoming Week's Classes")
upcoming = get_upcoming_classes()

if upcoming:
    for date_str, classes in sorted(upcoming.items()):
        weekday = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
        st.markdown(f"### {date_str} ({weekday})")
        df = pd.DataFrame(classes)
        st.dataframe(df, use_container_width=True)
else:
    st.info("No upcoming classes found for the next 7 days.")


# --- Search by Date ---
st.divider()
st.subheader("🔍 Search Classes by Date")
search_date = st.date_input("Select a date to search")
search_str = search_date.strftime("%Y-%m-%d")

if search_str in st.session_state.class_data:
    st.markdown(f"### Classes on {search_str} ({search_date.strftime('%A')})")
    df = pd.DataFrame(st.session_state.class_data[search_str])
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No classes scheduled for this date.")


# --- Download Timetable ---
st.divider()
st.subheader("📥 Download Timetable")

df_all = flatten_class_data()
csv = df_all.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Full Timetable as CSV",
    data=csv,
    file_name="class_timetable.csv",
    mime="text/csv"
)

