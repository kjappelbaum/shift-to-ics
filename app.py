import streamlit as st
import datetime
from datetime import timedelta
import io
import pandas as pd

DEFAULT_SHIFTS = {
    "DF": {"description": "Dienstfrei", "all_day": True},
    "IMC": {
        "description": "Station",
        "all_day": False,
        "start_time": "08:00",
        "end_time": "16:54",
    },
    "SN": {
        "description": "Spätnacht",
        "all_day": False,
        "start_time": "15:30",
        "end_time": "08:45",
        "next_day": True,
    },
    "ND2": {
        "description": "Nachtdienst",
        "all_day": False,
        "start_time": "20:00",
        "end_time": "08:45",
        "next_day": True,
    },
    "TD2": {
        "description": "Tagdienst Wochenende",
        "all_day": False,
        "start_time": "08:00",
        "end_time": "20:45",
    },
    "SH": {"description": "Stoffwechsel SH", "all_day": True},
    "Free": {"description": "Free", "all_day": True},
    "WS": {
        "description": "Wochenstation",
        "all_day": False,
        "start_time": "10:30",
        "end_time": "15:30",
    },
    "Poli": {
        "description": "Wochenstation",
        "all_day": False,
        "start_time": "10:30",
        "end_time": "15:30",
    },
}


def get_shift_details(shift_code, custom_shifts=None):
    """Get the details for a specific shift code."""

    # Use custom shifts if provided, otherwise default
    shift_details = custom_shifts if custom_shifts else DEFAULT_SHIFTS
    return shift_details.get(shift_code, {"description": shift_code, "all_day": True})


def create_ics_content(shifts, start_date, exclude_free=False, custom_shifts=None):
    """Create ICS file content from a list of shift codes."""
    calendar_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Shift Calendar Generator//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    current_date = start_date

    for i, shift in enumerate(shifts):
        if shift == "Free":
            shift = "DF"
        # Skip free and DF days if exclude_free is True
        if exclude_free and (shift == "Free" or shift == "DF"):
            current_date += timedelta(days=1)
            continue

        details = get_shift_details(shift, custom_shifts)

        # Generate a unique identifier for this event
        uid = f"shift-{current_date.strftime('%Y%m%d')}-{i}@shiftcalendar.com"

        # Get the current timestamp for DTSTAMP
        now = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")

        # Start adding the event
        calendar_lines.append("BEGIN:VEVENT")
        calendar_lines.append(f"UID:{uid}")
        calendar_lines.append(f"DTSTAMP:{now}")
        calendar_lines.append(f"SUMMARY:{shift} - {details['description']}")

        if details.get("all_day", True):
            # Format all-day events
            calendar_lines.append(
                f"DTSTART;VALUE=DATE:{current_date.strftime('%Y%m%d')}"
            )
            next_day = current_date + timedelta(days=1)
            calendar_lines.append(f"DTEND;VALUE=DATE:{next_day.strftime('%Y%m%d')}")
        else:
            # Format time-specific events
            start_hours, start_minutes = details["start_time"].split(":")
            start_datetime = current_date.replace(
                hour=int(start_hours), minute=int(start_minutes), second=0
            )
            calendar_lines.append(f"DTSTART:{start_datetime.strftime('%Y%m%dT%H%M%S')}")

            if details.get("next_day", False):
                # Handle overnight shifts
                end_day = current_date + timedelta(days=1)
            else:
                end_day = current_date

            end_hours, end_minutes = details["end_time"].split(":")
            end_datetime = end_day.replace(
                hour=int(end_hours), minute=int(end_minutes), second=0
            )
            calendar_lines.append(f"DTEND:{end_datetime.strftime('%Y%m%dT%H%M%S')}")

        calendar_lines.append(f"DESCRIPTION:{details['description']}")
        calendar_lines.append("END:VEVENT")

        # Move to the next day
        current_date += timedelta(days=1)

    calendar_lines.append("END:VCALENDAR")

    return "\r\n".join(calendar_lines)


def create_schedule_preview(shifts, start_date, exclude_free=False, custom_shifts=None):
    """Create a preview dataframe of the schedule."""
    schedule_data = []
    current_date = start_date

    for i, shift in enumerate(shifts):
        if shift == "Free":
            shift = "DF"
        # Skip free and DF days if exclude_free is True
        if exclude_free and (shift == "Free" or shift == "DF"):
            current_date += timedelta(days=1)
            continue

        details = get_shift_details(shift, custom_shifts)

        if details.get("all_day", True):
            time_info = "All day"
        else:
            start_time = details.get("start_time", "08:00")
            end_time = details.get("end_time", "16:00")
            if details.get("next_day", False):
                time_info = f"{start_time} - {end_time} (+1 day)"
            else:
                time_info = f"{start_time} - {end_time}"

        schedule_data.append(
            {
                "Date": current_date.strftime("%Y-%m-%d"),
                "Day": current_date.strftime("%A"),
                "Shift Code": shift,
                "Description": details["description"],
                "Time": time_info,
            }
        )

        current_date += timedelta(days=1)

    return pd.DataFrame(schedule_data)


def main():
    st.set_page_config(page_title="Shift Plan to ICS Converter", page_icon="📅")

    st.title("📅 Shift Plan to ICS Converter")
    st.write(
        "Convert your shift schedule to an ICS calendar file that you can import into Google Calendar, Outlook, or any other calendar application."
    )

    # Shift plan input
    st.subheader("Shift Plan")
    shift_text = st.text_area(
        "Paste your shift codes here (one per line):",
        height=150,
        placeholder="DF\nSN\nND2\nND2\nDF\nIMC\nSN",
    )

    # Start date
    start_date = st.date_input("Start Date:", datetime.date.today())

    # Options
    exclude_free = st.checkbox("Exclude free days and days off from calendar")

    # Shift types configuration
    st.subheader("Shift Types Configuration")

    # Initialize session state for custom shifts
    if "custom_shifts" not in st.session_state:
        st.session_state.custom_shifts = DEFAULT_SHIFTS

    # Display current shift types
    for shift_code, details in st.session_state.custom_shifts.items():
        with st.expander(f"{shift_code} - {details['description']}"):
            col1, col2 = st.columns(2)

            with col1:
                new_desc = st.text_input(
                    f"Description for {shift_code}:",
                    value=details["description"],
                    key=f"desc_{shift_code}",
                )
                all_day = st.checkbox(
                    f"All day event",
                    value=details.get("all_day", True),
                    key=f"allday_{shift_code}",
                )

            with col2:
                if not all_day:
                    start_time = st.text_input(
                        f"Start time (HH:MM):",
                        value=details.get("start_time", "08:00"),
                        key=f"start_{shift_code}",
                    )
                    end_time = st.text_input(
                        f"End time (HH:MM):",
                        value=details.get("end_time", "16:00"),
                        key=f"end_{shift_code}",
                    )
                    next_day = st.checkbox(
                        f"Ends next day",
                        value=details.get("next_day", False),
                        key=f"nextday_{shift_code}",
                    )
                else:
                    start_time = None
                    end_time = None
                    next_day = False

            # Update session state
            st.session_state.custom_shifts[shift_code] = {
                "description": new_desc,
                "all_day": all_day,
                "start_time": start_time,
                "end_time": end_time,
                "next_day": next_day,
            }

    # Add new shift type
    st.subheader("Add New Shift Type")
    col1, col2, col3 = st.columns(3)

    with col1:
        new_code = st.text_input("Shift Code:", key="new_code")
    with col2:
        new_description = st.text_input("Description:", key="new_description")
    with col3:
        if st.button("Add Shift Type"):
            if new_code and new_description:
                st.session_state.custom_shifts[new_code] = {
                    "description": new_description,
                    "all_day": True,
                }
                st.success(f"Added shift type: {new_code}")
                st.rerun()

    # Convert button
    if st.button("Convert to ICS", type="primary"):
        if not shift_text.strip():
            st.error("Please enter your shift plan.")
            return

        # Parse shifts
        shifts = [
            line.strip() for line in shift_text.strip().split("\n") if line.strip()
        ]

        for shift in shifts:
            if shift not in st.session_state.custom_shifts:
                st.error(
                    f"Shift code '{shift}' not found in custom shifts. Please add it first."
                )

        if not shifts:
            st.error("No valid shift codes found.")
            return

        try:
            # Create schedule preview
            start_datetime = datetime.datetime.combine(start_date, datetime.time())
            preview_df = create_schedule_preview(
                shifts, start_datetime, exclude_free, st.session_state.custom_shifts
            )

            # Show schedule preview
            st.subheader("📊 Schedule Preview")
            st.dataframe(preview_df, use_container_width=True)

            # Show shift statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Shifts", len(preview_df))
            with col2:
                work_shifts = preview_df[~preview_df["Shift Code"].isin(["DF", "Free"])]
                st.metric("Work Shifts", len(work_shifts))
            with col3:
                free_days = preview_df[preview_df["Shift Code"].isin(["DF", "Free"])]
                st.metric("Free Days", len(free_days))

            # Show shift type breakdown
            shift_counts = preview_df["Shift Code"].value_counts()
            st.subheader("Shift Distribution")
            st.bar_chart(shift_counts)

            # Create ICS content
            ics_content = create_ics_content(
                shifts, start_datetime, exclude_free, st.session_state.custom_shifts
            )

            # Create filename
            filename = f"shift_calendar_{start_date.strftime('%Y_%m_%d')}.ics"

            # Offer download
            st.download_button(
                label="📥 Download ICS File",
                data=ics_content,
                file_name=filename,
                mime="text/calendar",
            )

            st.success(f"Calendar generated successfully! Found {len(shifts)} shifts.")

            # Show ICS preview
            with st.expander("ICS File Preview (first 10 lines):"):
                st.code("\n".join(ics_content.split("\r\n")[:10]))

        except Exception as e:
            st.error(f"Error generating calendar: {str(e)}")


if __name__ == "__main__":
    main()
