import streamlit as st
import pandas as pd
import json
from datetime import datetime, time, timedelta

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="Class Tracker", layout="wide")
DATA_FILE = "class_data.json"

# -------------------------------
# LOAD OR CREATE DATA
# -------------------------------
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        default_data = {
            "Monday": [
                {"subject": "Math", "time": "09:00", "teacher": "Mr. Sharma"},
                {"subject": "Physics", "time": "11:00", "teacher": "Mrs. Verma"},
            ],
            "Tuesday": [
                {"subject": "Chemistry", "time": "10:00", "teacher": "Mr. Singh"},
                {"subject": "English", "time": "13:00", "teacher": "Ms. Roy"},
            ],
            "Wednesday": [
                {"subject": "Computer Science", "time": "09:30", "teacher": "Mr. Mehta"},
                {"subject": "Biology", "time": "12:00", "teacher": "Dr. Gupta"},
            ],
        }
        with open(DATA_FILE, "w") as f:
            json.dump(default_data, f, indent=4)
        return default_data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def get_upcoming_classes(data):
    """Show next 7 days of classes from current time."""
    now = datetime.now()
    today_idx = now.weekday()  # Monday=0

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    upcoming = []

    for offset in range(7):  # next 7 days window
        check_date = now + timedelta(days=offset)
        day_name = check_date.strftime("%A")
        if day_name not in data:
            continue

        for cls in data[day_name]:
            cls_time = datetime.strptime(cls["time"], "%H:%M").time()
            class_datetime = datetime.combine(check_date.date(), cls_time)

            # Only show classes in the future
            if class_datetime >= now:
                upcoming.append({
                    "day": day_name,
                    "date": check_date.strftime("%Y-%m-%d"),
                    "subject": cls["subject"],
                    "time": cls["time"],
                    "teacher": cls["teacher"],
                })

    if not upcoming:
        return pd.DataFrame()
    df = pd.DataFrame(upcoming)
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
    df = df.sort_values("datetime").drop(columns=["datetime"])
    return df.reset_index(drop=True)


def search_classes(data, day):
    """Return all classes for the given day name."""
    if not day:
        return pd.DataFrame()
    day = day.strip().capitalize()
    if day in data and len(data[day]) > 0:
        df = pd.DataFrame(data[day])
        df["day"] = day
        return df
    return pd.DataFrame()

# -------------------------------
# MAIN APP
# -------------------------------
st.title("📚 Class Tracker Dashboard")
data = load_data()

col1, col2 = st.columns([3, 2])

# -------------------------------
# UPCOMING CLASSES
# -------------------------------
with col1:
    st.subheader("⏰ Upcoming Classes (Next 7 Days)")
    upcoming_df = get_upcoming_classes(data)
    if upcoming_df.empty:
        st.info("No upcoming classes in the next 7 days.")
    else:
        st.dataframe(upcoming_df, use_container_width=True)

# -------------------------------
# SEARCH BY DAY
# -------------------------------
with col2:
    st.subheader("🔍 Search by Day")
    search_day = st.text_input("Enter day (e.g., Monday, Tuesday):").strip()
    if search_day:
        results = search_classes(data, search_day)
        if not results.empty:
            st.success(f"Classes on {search_day.capitalize()}:")
            st.dataframe(results, use_container_width=True)
        else:
            st.warning("No classes found for that day.")

# -------------------------------
# ADD NEW CLASS
# -------------------------------
st.markdown("---")
st.subheader("📝 Add a New Class")

with st.form("add_class_form"):
    day = st.selectbox(
        "Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )
    subject = st.text_input("Subject Name")
    time_input = st.time_input("Class Time", value=time(9, 0))
    teacher = st.text_input("Teacher Name")

    submitted = st.form_submit_button("Add Class")
    if submitted:
        new_entry = {"subject": subject, "time": time_input.strftime("%H:%M"), "teacher": teacher}
        if day not in data:
            data[day] = []
        data[day].append(new_entry)
        save_data(data)
        st.success(f"✅ Added {subject} on {day} at {time_input.strftime('%H:%M')}")

# -------------------------------
# VIEW FULL TIMETABLE
# -------------------------------
with st.expander("📋 View Full Timetable"):
    for day, classes in data.items():
        st.markdown(f"**{day}**")
        if classes:
            st.table(pd.DataFrame(classes))
        else:
            st.caption("No classes scheduled.")

