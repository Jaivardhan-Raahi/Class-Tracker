import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="Class Tracker", layout="wide")

DATA_FILE = "class_data.json"

# -------------------------------
# INITIAL DATA LOAD / CREATE
# -------------------------------
def load_data():
    """Load local class data, create file if not found."""
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {
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
            json.dump(data, f, indent=4)
    return data

def save_data(data):
    """Save updated data to local JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def get_upcoming_classes(data):
    """Return next classes based on current day/time."""
    today = datetime.now().strftime("%A")
    current_time = datetime.now().time()

    upcoming = []
    for day, classes in data.items():
        for cls in classes:
            cls_time = datetime.strptime(cls["time"], "%H:%M").time()
            if day == today and cls_time >= current_time:
                upcoming.append({"day": day, **cls})
            elif datetime.strptime(day, "%A").weekday() > datetime.now().weekday():
                # Classes later in the week
                upcoming.append({"day": day, **cls})

    # Sort by weekday + time
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df = pd.DataFrame(upcoming)
    if df.empty:
        return df
    df["day_index"] = df["day"].apply(lambda x: day_order.index(x))
    df["time_dt"] = pd.to_datetime(df["time"], format="%H:%M")
    df = df.sort_values(["day_index", "time_dt"]).drop(columns=["day_index", "time_dt"])
    return df.reset_index(drop=True)

def search_classes(data, day):
    """Return classes for the searched day."""
    day = day.capitalize()
    if day in data:
        return pd.DataFrame(data[day])
    else:
        return pd.DataFrame()

# -------------------------------
# MAIN APP
# -------------------------------
st.title("📚 Class Tracker Dashboard")

data = load_data()

# Columns layout
col1, col2 = st.columns([3, 2])

# -------------------------------
# DASHBOARD (Upcoming Classes)
# -------------------------------
with col1:
    st.subheader("⏰ Upcoming Classes")
    upcoming_df = get_upcoming_classes(data)
    if upcoming_df.empty:
        st.info("No upcoming classes found for this week.")
    else:
        st.dataframe(upcoming_df, use_container_width=True)

# -------------------------------
# SEARCH BY DAY
# -------------------------------
with col2:
    st.subheader("🔍 Search by Day")
    search_day = st.text_input("Enter day (e.g., Monday):").strip()
    if search_day:
        results = search_classes(data, search_day)
        if not results.empty:
            st.success(f"Classes on {search_day.capitalize()}:")
            st.dataframe(results, use_container_width=True)
        else:
            st.warning("No classes found for that day.")

# -------------------------------
# ADD / EDIT CLASSES
# -------------------------------
st.markdown("---")
st.subheader("📝 Add a New Class")

with st.form("add_class_form"):
    day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    subject = st.text_input("Subject Name")
    time = st.time_input("Class Time")
    teacher = st.text_input("Teacher Name")
    submitted = st.form_submit_button("Add Class")

    if submitted:
        new_class = {"subject": subject, "time": time.strftime("%H:%M"), "teacher": teacher}
        if day not in data:
            data[day] = []
        data[day].append(new_class)
        save_data(data)
        st.success(f"Added class for {day}: {subject} at {time.strftime('%H:%M')}")

# -------------------------------
# VIEW ALL DATA
# -------------------------------
with st.expander("📋 View Full Timetable"):
    for day, classes in data.items():
        st.markdown(f"**{day}**")
        st.table(pd.DataFrame(classes))

