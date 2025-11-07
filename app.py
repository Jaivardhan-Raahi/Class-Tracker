import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.set_page_config(page_title="📚 Class Tracker", layout="wide")

# --------------------------
# INITIAL DATA (stored in memory)
# --------------------------
if "class_data" not in st.session_state:
    st.session_state.class_data = {
        "2025-11-07": [
            {"subject": "Math", "time": "09:00", "teacher": "Mr. Sharma"},
            {"subject": "Physics", "time": "11:00", "teacher": "Mrs. Verma"},
        ],
        "2025-11-08": [
            {"subject": "Chemistry", "time": "10:00", "teacher": "Mr. Singh"},
        ],
    }

data = st.session_state.class_data


# --------------------------
# HELPER FUNCTIONS
# --------------------------
def get_upcoming_classes(data):
    now = datetime.now()
    upcoming = []

    for date_str, classes in data.items():
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue

        for cls in classes:
            cls_time = datetime.strptime(cls["time"], "%H:%M").time()
            class_dt = datetime.combine(date_obj.date(), cls_time)
            if class_dt >= now:
                upcoming.append({
                    "date": date_str,
                    "day": date_obj.strftime("%A"),
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


def search_classes(data, date_input):
    if not date_input:
        return pd.DataFrame()
    date_str = date_input.strftime("%Y-%m-%d")
    if date_str in data:
        df = pd.DataFrame(data[date_str])
        df["date"] = date_str
        df["day"] = date_input.strftime("%A")
        return df
    return pd.DataFrame()


# --------------------------
# LAYOUT
# --------------------------
st.title("📅 Class Tracker Dashboard")

col1, col2 = st.columns([3, 2])

# --------------------------
# UPCOMING CLASSES
# --------------------------
with col1:
    st.subheader("⏰ Upcoming Classes (Next 14 Days)")
    upcoming_df = get_upcoming_classes(data)
    if upcoming_df.empty:
        st.info("No upcoming classes found.")
    else:
        st.dataframe(upcoming_df, use_container_width=True)

# --------------------------
# SEARCH BY DATE
# --------------------------
with col2:
    st.subheader("🔍 Search by Date")
    selected_date = st.date_input("Select a date")
    if selected_date:
        result_df = search_classes(data, selected_date)
        if result_df.empty:
            st.warning("No classes found for that date.")
        else:
            st.success(f"Classes on {selected_date.strftime('%A, %Y-%m-%d')}:")
            st.dataframe(result_df, use_container_width=True)

# --------------------------
# ADD A CLASS
# --------------------------
st.markdown("---")
st.subheader("📝 Add New Class")

with st.form("add_class_form"):
    date_input = st.date_input("Class Date", value=datetime.today())
    subject = st.text_input("Subject Name")
    time_input = st.time_input("Class Time", value=time(9, 0))
    teacher = st.text_input("Teacher Name")

    submitted = st.form_submit_button("Add Class")
    if submitted:
        date_str = date_input.strftime("%Y-%m-%d")
        new_class = {
            "subject": subject,
            "time": time_input.strftime("%H:%M"),
            "teacher": teacher,
        }
        if date_str not in data:
            data[date_str] = []
        data[date_str].append(new_class)
        st.success(f"✅ Added {subject} on {date_str} at {time_input.strftime('%H:%M')}")
        st.session_state.class_data = data  # update in memory
        st.experimental_rerun()

# --------------------------
# FULL TIMETABLE
# --------------------------
with st.expander("📋 View All Scheduled Classes"):
    for date_str, classes in sorted(data.items()):
        try:
            day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
        except ValueError:
            day_name = "Invalid Date"
        st.markdown(f"**{date_str} ({day_name})**")
        st.table(pd.DataFrame(classes))
