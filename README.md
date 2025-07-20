# How to Use the Shift Schedule ICS Generator

This Python script converts a simple text file containing shift codes into an ICS calendar file that you can import into Google Calendar, Outlook, or any other calendar application that supports the ICS format.

## Prerequisites

- Python 3.6 or higher
- A text file with your shift codes (one per line)

## Step 1: Prepare Your Shift Text File

Create a text file with your shift codes, one per line. For example:

```
DF
SN
ND2
ND2
DF
...
```

The script recognizes the following shift codes by default:

- `DF` - Dienstfrei (day off)
- `IMC` - Station (8:00-16:54)
- `SN` - Spätnacht (15:30-8:45 next day)
- `ND2` - Nachtdienst (20:00-8:45 next day)
- `TD2` - Tagdienst Wochenende (8:00-20:45)
- `SH` - Stoffwechsel SH (all-day event)
- `Free` - Free day (all-day event)

You can easily add more shift types by modifying the `get_shift_details` function in the script.

## Step 2: Run the Script

Run the script from your terminal or command prompt:

```bash
python shift_to_ics.py
```

The script will prompt you for:

1. The path to your shifts text file
2. The start date for your schedule (YYYY-MM-DD format)
3. Whether you want to exclude free days and days off

## Step 3: Import the Generated ICS File

The script will generate an ICS file in the same directory as your input file. The filename will be based on your input file with "_calendar" or "_calendar_work_only" added to the end.

To import this file into Google Calendar:

1. Go to Google Calendar
2. Click on the "+" icon next to "Other calendars"
3. Select "Import"
4. Upload the generated ICS file
5. Select the calendar where you want to import these events
6. Click "Import"

## Customizing Shift Types

If you need to add or modify shift types, open the script and find the `get_shift_details` function. Add your custom shift types to the `shift_details` dictionary using the following format:

```python
"YOUR_CODE": {
    "description": "Your Shift Description", 
    "all_day": False,  # True for all-day events
    "start_time": "HH:MM",  # Only needed if all_day is False
    "end_time": "HH:MM",  # Only needed if all_day is False
    "next_day": False  # Set to True for overnight shifts
}
```

## Example Usage

1. Create a file called `may_2025.txt` with your shift codes
2. Run `python shift_to_ics.py`
3. Enter `may_2025.txt` when prompted for the input file
4. Enter `2025-05-01` when prompted for the start date
5. Choose whether to exclude free days
6. Import the generated `may_2025_calendar.ics` file into your calendar app
