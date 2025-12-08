import gspread
from google.oauth2.service_account import Credentials
import datetime

# Configuration
SERVICE_ACCOUNT_FILE = 'kada-admin.json'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
# TODO: Replace with your actual Google Sheet name or URL
SHEET_NAME = 'kada_attendance' 

def connect_to_spreadsheet():
    """Connects to Google Sheets using the service account and returns the Spreadsheet object."""
    try:
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        # Open the spreadsheet
        try:
            spreadsheet = client.open(SHEET_NAME)
            print(f"Successfully connected to spreadsheet: {SHEET_NAME}")
            return spreadsheet
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"Error: Spreadsheet '{SHEET_NAME}' not found.")
            print("Please make sure the sheet exists and is shared with:")
            print("kada-admin@kada-469004.iam.gserviceaccount.com")
            return None
    except Exception as e:
        print(f"Authentication Error: {e}")
        return None

def get_worksheet(spreadsheet, worksheet_name):
    """Helper to get a specific worksheet."""
    try:
        return spreadsheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        print(f"Error: Worksheet '{worksheet_name}' not found.")
        return None

def read_data(spreadsheet, worksheet_name):
    """Reads and prints all data from the specified worksheet."""
    sheet = get_worksheet(spreadsheet, worksheet_name)
    if not sheet:
        return
    
    print(f"\n--- Reading Data from {worksheet_name} ---")
    try:
        data = sheet.get_all_records()
        if not data:
            print("Sheet is empty or has no headers.")
        else:
            for i, row in enumerate(data, start=2): # 1 is header
                print(f"Row {i}: {row}")
    except Exception as e:
        print(f"Error reading data: {e}")

def add_data(spreadsheet, worksheet_name, data_dict):
    """Adds a new row to the specified worksheet."""
    sheet = get_worksheet(spreadsheet, worksheet_name)
    if not sheet:
        return

    print(f"\n--- Adding Data to {worksheet_name} ---")
    try:
        # Check if headers exist (simple check)
        if not sheet.row_values(1):
            print("Warning: Sheet appears to be empty (no headers).")

        # Prepare row data based on worksheet type
        # This is a simple implementation; ideally, we map keys to columns dynamically
        # For now, we assume the dict keys match the order or we just append values if we know the order.
        # But `append_row` takes a list.
        
        # To be safe, let's just append the values from the dict in a specific order if known,
        # or just append the values if the dict is ordered (Python 3.7+).
        # Better: Read headers and map.
        
        headers = sheet.row_values(1)
        if not headers:
             print("Error: Cannot add data to a sheet without headers.")
             return

        row = []
        for header in headers:
            row.append(data_dict.get(header, ''))
        
        sheet.append_row(row, value_input_option='USER_ENTERED')
        print(f"Added row: {row}")
    except Exception as e:
        print(f"Error adding data: {e}")

def find_employee(spreadsheet, name):
    """Finds an employee by name in the 'Employees' sheet."""
    sheet = get_worksheet(spreadsheet, 'Employees')
    if not sheet:
        return None
    
    try:
        # Get all records
        records = sheet.get_all_records()
        for record in records:
            if record.get('name') == name:
                return record
        return None
    except Exception as e:
        print(f"Error finding employee: {e}")
        return None

import random

def get_current_week_sheet_name():
    """Returns the sheet name for the current week in YYYY_WW format."""
    today = datetime.date.today()
    year = today.year
    week = today.isocalendar()[1]
    return f"{year}_{week}"

def check_in(spreadsheet, employee, specific_time=None):
    """Handles the check-in process."""
    sheet_name = get_current_week_sheet_name()
    sheet = get_worksheet(spreadsheet, sheet_name)
    
    if not sheet:
        print(f"이번 주차 시트 없음 ({sheet_name})")
        return False

    if specific_time:
        checkin_time_str = specific_time
    else:
        # Generate random time between 09:00 and 10:00
        now = datetime.datetime.now()
        random_minute = random.randint(0, 59)
        random_second = random.randint(0, 59)
        checkin_dt = now.replace(hour=9, minute=random_minute, second=random_second)
        checkin_time_str = checkin_dt.strftime("%H:%M:%S")
    
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Prepare data based on schema: 
    # ['date', 'name', 'location', 'checkin_time', 'checkout_time', 'employee_id', 'reason']
    data = {
        'date': today_str,
        'name': employee.get('name'),
        'location': employee.get('location'),
        'checkin_time': checkin_time_str,
        'checkout_time': '',
        'employee_id': employee.get('id'),
        'reason': '-'
    }
    
    add_data(spreadsheet, sheet_name, data)
    print(f"출근 처리가 완료되었습니다. 시간: {checkin_time_str}, 사유: -")
    return True

def check_out(spreadsheet, employee, specific_time=None):
    """Handles the check-out process."""
    sheet_name = get_current_week_sheet_name()
    sheet = get_worksheet(spreadsheet, sheet_name)
    
    if not sheet:
        print(f"이번 주차 시트 없음 ({sheet_name})")
        return False

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    emp_id = str(employee.get('id'))

    # Get all values to find the row
    rows = sheet.get_all_values()
    if not rows:
        print("시트가 비어있습니다.")
        return False

    headers = rows[0]
    try:
        date_idx = headers.index('date')
        id_idx = headers.index('employee_id')
        checkout_idx = headers.index('checkout_time')
        reason_idx = headers.index('reason')
    except ValueError:
        print("필수 컬럼(date, employee_id, checkout_time, reason)이 누락되었습니다.")
        return False

    target_row_idx = -1
    for i, row in enumerate(rows[1:], start=2): # start=2 because row 1 is header
        # Check bounds
        if len(row) <= max(date_idx, id_idx): 
            continue
            
        # Compare date and employee_id
        if row[date_idx] == today_str and str(row[id_idx]) == emp_id:
            target_row_idx = i
            break
    
    if target_row_idx == -1:
        print("오늘 날짜의 출근 기록이 없습니다.")
        return False

    if specific_time:
        checkout_time_str = specific_time
    else:
        # Generate random time 21:00 ~ 22:00
        now = datetime.datetime.now()
        random_minute = random.randint(0, 59)
        random_second = random.randint(0, 59)
        checkout_dt = now.replace(hour=21, minute=random_minute, second=random_second)
        checkout_time_str = checkout_dt.strftime("%H:%M:%S")

    # Update checkout_time and reason
    # Use USER_ENTERED to ensure correct data types (Time, String)
    
    # Helper to convert col index (0-based) to letter (A, B, C...)
    # Assuming cols < 26 for simplicity
    checkout_col_letter = chr(64 + checkout_idx + 1)
    reason_col_letter = chr(64 + reason_idx + 1)
    
    checkout_cell = f"{checkout_col_letter}{target_row_idx}"
    reason_cell = f"{reason_col_letter}{target_row_idx}"
    
    sheet.update(checkout_cell, [[checkout_time_str]], value_input_option='USER_ENTERED')
    sheet.update(reason_cell, [["-"]], value_input_option='USER_ENTERED')
    
    print(f"퇴근 처리가 완료되었습니다. 시간: {checkout_time_str}, 사유: -")
    return True

def get_sheet_name_from_date(date_obj):
    """Returns the sheet name for a given date in YYYY_WW format."""
    year = date_obj.year
    week = date_obj.isocalendar()[1]
    return f"{year}_{week}"

def get_sheet_name_from_date_str(date_str):
    """Returns the sheet name for a given date string (YYYY-MM-DD)."""
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return get_sheet_name_from_date(date_obj)
    except ValueError:
        return None

def get_all_employee_records(spreadsheet, employee_id):
    """Retrieves all attendance records for a specific employee across all weekly sheets."""
    records = []
    emp_id_str = str(employee_id)
    
    try:
        # Get all worksheets
        worksheets = spreadsheet.worksheets()
        
        # Filter for weekly sheets (format YYYY_WW)
        weekly_sheets = [ws for ws in worksheets if len(ws.title) == 7 and '_' in ws.title]
        
        # Sort sheets to show recent data (reverse chronological)
        weekly_sheets.sort(key=lambda x: x.title, reverse=True)

        for sheet in weekly_sheets:
            try:
                rows = sheet.get_all_records()
                for row in rows:
                    if str(row.get('employee_id')) == emp_id_str:
                        records.append(row)
            except Exception as e:
                # Skipping sheet silently or logging
                continue
                
    except Exception as e:
        print(f"Error retrieving all records: {e}")
        
    return records

def delete_record(spreadsheet, employee_id, date_str):
    """Deletes a record for the employee on a specific date."""
    sheet_name = get_sheet_name_from_date_str(date_str)
    if not sheet_name:
        print("잘못된 날짜 형식입니다. (YYYY-MM-DD)")
        return False

    sheet = get_worksheet(spreadsheet, sheet_name)
    if not sheet:
        print(f"해당 날짜({date_str})가 포함된 주차의 기록이 없습니다.")
        return False
        
    emp_id_str = str(employee_id)
    
    try:
        rows = sheet.get_all_values()
        if not rows:
            print("시트가 비어있습니다.")
            return False
            
        headers = rows[0]
        try:
            date_idx = headers.index('date')
            id_idx = headers.index('employee_id')
        except ValueError:
            print("필수 컬럼이 누락되었습니다.")
            return False
            
        target_row_idx = -1
        # Find row to delete
        for i, row in enumerate(rows[1:], start=2):
             if len(row) <= max(date_idx, id_idx): continue
             
             if row[date_idx] == date_str and str(row[id_idx]) == emp_id_str:
                 target_row_idx = i
                 break
        
        if target_row_idx != -1:
            sheet.delete_rows(target_row_idx)
            print(f"{date_str} 기록이 삭제되었습니다.")
            return True
        else:
            print(f"{date_str}에 해당 직원의 기록을 찾을 수 없습니다.")
            return False
            
    except Exception as e:
        print(f"삭제 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    spreadsheet = connect_to_spreadsheet()
    
    if spreadsheet:
        # Test read
        read_data(spreadsheet, 'Employees')

