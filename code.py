#!/usr/bin/env python3
import datetime
import uuid
import os
from datetime import timedelta

def parse_shifts_file(file_path):
    """Parse a text file with shift codes, one per line."""
    shifts = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            # Try to parse the line as a shift code
            parts = line.strip().split()
            if len(parts) >= 1:
                shifts.append(parts[0])
    return shifts

def get_shift_details(shift_code):
    """Get the details for a specific shift code."""
    shift_details = {
        "DF": {
            "description": "Dienstfrei", 
            "all_day": True
        },
        "IMC": {
            "description": "Station", 
            "all_day": False, 
            "start_time": "08:00", 
            "end_time": "16:54"
        },
        "SN": {
            "description": "Spätnacht", 
            "all_day": False, 
            "start_time": "15:30", 
            "end_time": "08:45", 
            "next_day": True
        },
        "ND2": {
            "description": "Nachtdienst", 
            "all_day": False, 
            "start_time": "20:00", 
            "end_time": "08:45", 
            "next_day": True
        },
        "TD2": {
            "description": "Tagdienst Wochenende", 
            "all_day": False, 
            "start_time": "08:00", 
            "end_time": "20:45"
        },
        "SH": {
            "description": "Stoffwechsel SH", 
            "all_day": True
        },
        "Free": {
            "description": "Free", 
            "all_day": True
        }
    }
    
    # Return default empty details if shift code not recognized
    return shift_details.get(shift_code, {"description": shift_code, "all_day": True})

def create_ics_file(shifts, start_date, file_path, exclude_free=False):
    """Create an ICS file from a list of shift codes."""
    calendar_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Shift Calendar Generator//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    
    current_date = start_date
    
    for i, shift in enumerate(shifts):
        # Skip free and DF days if exclude_free is True
        if exclude_free and (shift == "Free" or shift == "DF"):
            current_date += timedelta(days=1)
            continue
            
        details = get_shift_details(shift)
        
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
            calendar_lines.append(f"DTSTART;VALUE=DATE:{current_date.strftime('%Y%m%d')}")
            next_day = current_date + timedelta(days=1)
            calendar_lines.append(f"DTEND;VALUE=DATE:{next_day.strftime('%Y%m%d')}")
        else:
            # Format time-specific events
            start_hours, start_minutes = details["start_time"].split(":")
            start_datetime = current_date.replace(
                hour=int(start_hours), 
                minute=int(start_minutes),
                second=0
            )
            calendar_lines.append(f"DTSTART:{start_datetime.strftime('%Y%m%dT%H%M%S')}")
            
            if details.get("next_day", False):
                # Handle overnight shifts
                end_day = current_date + timedelta(days=1)
            else:
                end_day = current_date
                
            end_hours, end_minutes = details["end_time"].split(":")
            end_datetime = end_day.replace(
                hour=int(end_hours), 
                minute=int(end_minutes),
                second=0
            )
            calendar_lines.append(f"DTEND:{end_datetime.strftime('%Y%m%dT%H%M%S')}")
        
        calendar_lines.append(f"DESCRIPTION:{details['description']}")
        calendar_lines.append("END:VEVENT")
        
        # Move to the next day
        current_date += timedelta(days=1)
    
    calendar_lines.append("END:VCALENDAR")
    
    # Write the ICS file
    with open(file_path, 'w') as f:
        f.write("\r\n".join(calendar_lines))
    
    return file_path

def main():
    print("Shift Calendar Generator")
    print("=======================")
    
    # Get input file
    input_file = input("Enter the path to your shifts text file: ")
    
    # Get start date
    start_date_str = input("Enter start date (YYYY-MM-DD): ")
    try:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Using today's date.")
        start_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get output preferences
    exclude_free = input("Exclude free days and days off? (y/n): ").lower() == 'y'
    
    # Parse shifts
    try:
        shifts = parse_shifts_file(input_file)
        
        # Create output file paths
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_calendar{'_work_only' if exclude_free else ''}.ics"
        
        # Create ICS file
        create_ics_file(shifts, start_date, output_file, exclude_free)
        
        print(f"Calendar generated successfully: {output_file}")
        print(f"Found {len(shifts)} shifts")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
