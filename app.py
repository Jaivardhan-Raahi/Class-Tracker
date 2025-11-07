import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Class Tracker", layout="wide")

# --- Initialize Data (Dictionary only) ---
if "class_data" not in st.session_state:
    st.session_state.class_data = {
        "2025-11-07": [
            {"subject": "Math", "time": "10:00 AM", "teacher": "Mr. Raj"},
            {"subject": "Physics", "time": "12:00 PM", "teacher": "Dr. Mehta"},
            {"subject": "English", "time": "2:00 PM", "teacher": "Ms. Verma"},
        ],
        "2025-11-08": [
            {"subject": "Biology", "time": "9:00 AM", "teacher": "Dr. Arora"},
            {"subject": "Chemistry", "time": "11:00 AM", "teacher": "Dr. Khan"},
            {"subject": "PE", "time": "3:00 PM", "teacher": "Mr. Singh"},
        ],
        "2025-11-09": [
            {"subject": "History", "time": "10:00 AM", "teacher": "Mr. Sharma"},
            {"subject": "Geography", "time": "12:00 PM", "teacher": "Ms. Patel"},
        ],
        "2025-11-10": [
            {"subject": "Math", "time": "9:00 AM", "teacher": "Mr. Raj"},
            {"subject": "Computer", "time": "11:00 AM", "teacher": "Ms. Nair"},
        ],
    }


# --- Helper Functions ---
def get_upcoming_classes():
    today = datetime.today().date()
    upcoming = {}
    for date_str, classes in st.session_state.class_data.items():
        class_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if today <= class_date <= today + timedelta(days=7):
            upcoming[date_str] = classes
    return upcoming


def add_class(date, subject, time, teacher):
    date_str = date.strftime("%Y-%m-%d")
    if date_str not in st.session_state.class_data:
        st.session_state.class_data[date_str] = []
    st.session_state.class_data[date_str].append(
        {"subject": subject, "time": time, "teacher": teacher}
    )
    st.rerun()


def timetable_to_df():
    rows = []
    for date_str, classes in st.session_state.class_data.items():
        day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
        for cls in classes:
            rows.append(
                {
                    "Date": date_str,
                    "Day": day_name,
                    "Subject": cls["subject"],
                    "Time": cls["time"],
                    "Teacher": cls["teacher"],
                }
            )
    return pd.DataFrame(rows)


# --- Sidebar: Add New Class ---
st.sidebar.header("➕ Add New Class")
date_input = st.sidebar.date_input("Class Date", datetime.today())
subject = st.sidebar.text_input("Subject")
time = st.sidebar.text_input("Time (e.g. 10:30 AM)")
teacher = st.sidebar.text_input("Teacher Name")

if st.sidebar.button("Add Class"):
    if subject and time and teacher:
        add_class(date_input, subject, time, teacher)
        st.sidebar.success("✅ Class added successfully!")
    else:
        st.sidebar.error("⚠️ Fill all fields first.")

# --- Main Dashboard Tabs ---
tab1, tab2, tab3 = st.tabs(["🏠 Dashboard", "📅 Full Timetable", "📥 Upload / Export"])

with tab1:
    st.title("📚 Class Tracker Dashboard")

    # Upcoming week
    st.subheader("📆 Upcoming Week’s Classes")
    upcoming = get_upcoming_classes()
    if upcoming:
        for date_str, classes in sorted(upcoming.items()):
            weekday = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
            st.markdown(f"**{date_str} ({weekday})**")
            df = pd.DataFrame(classes)
            st.dataframe(df, use_container_width=True)
    else:
        st.info("No upcoming classes in the next 7 days.")

    # Search by date
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


with tab2:
    st.header("📋 Full Weekly Timetable")

    df = timetable_to_df()

    # --- Filters ---
    f_day = st.selectbox(
        "Filter by Day", ["All"] + sorted(df["Day"].unique().tolist())
    )
    f_subject = st.selectbox(
        "Filter by Subject", ["All"] + sorted(df["Subject"].unique().tolist())
    )
    f_teacher = st.selectbox(
        "Filter by Teacher", ["All"] + sorted(df["Teacher"].unique().tolist())
    )

    if f_day != "All":
        df = df[df["Day"] == f_day]
    if f_subject != "All":
        df = df[df["Subject"] == f_subject]
    if f_teacher != "All":
        df = df[df["Teacher"] == f_teacher]

    if df.empty:
        st.info("No data for selected filters.")
    else:
        st.dataframe(df.reset_index(drop=True), use_container_width=True)

    # --- Download as CSV ---
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Timetable (CSV)", csv_data, "timetable.csv", "text/csv")


with tab3:
    st.header("📤 Upload or Replace Timetable")

    uploaded_file = st.file_uploader("Upload a CSV timetable", type=["csv"])
    if uploaded_file:
        try:
            new_df = pd.read_csv(uploaded_file)
            new_dict = {}
            for _, row in new_df.iterrows():
                date_str = str(row["Date"])
                if date_str not in new_dict:
                    new_dict[date_str] = []
                new_dict[date_str].append(
                    {
                        "subject": row["Subject"],
                        "time": row["Time"],
                        "teacher": row["Teacher"],
                    }
                )
            st.session_state.class_data = new_dict
            st.success("✅ Timetable replaced successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Upload failed: {e}")
