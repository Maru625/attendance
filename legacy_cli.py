import app.services.sheet_service as google_client

def main():
    print("=== Kada Commute System ===")
    
    # 1. Connect to Google Sheets
    spreadsheet = google_client.connect_to_spreadsheet()
    if not spreadsheet:
        print("Failed to connect to Google Sheets. Exiting.")
        return

    # 2. Input Name
    name = input("이름을 입력하세요: ").strip()
    if not name:
        print("이름이 입력되지 않았습니다.")
        return

    # 3. Find Employee
    print(f"'{name}' 님을 조회 중입니다...")
    employee = google_client.find_employee(spreadsheet, name)

    if employee:
        print(f"\n환영합니다, {employee.get('name')}님!")
        print(f"ID: {employee.get('id')}")
        print(f"위치: {employee.get('location')}")
        
        # Show all records
        print("\n[출퇴근 기록]")
        records = google_client.get_all_employee_records(spreadsheet, employee.get('id'))
        if records:
            print(f"{'날짜':<12} {'출근 시간':<10} {'퇴근 시간':<10} {'사유'}")
            print("-" * 50)
            for r in records:
                check_in = r.get('checkin_time', '')
                check_out = r.get('checkout_time', '')
                reason = r.get('reason', '-')
                print(f"{r.get('date'):<12} {check_in:<10} {check_out:<10} {reason}")
        else:
            print("기록이 없습니다.")
        
        # 4. Ask Check-in/Check-out
        while True:
            action = input("\n원하시는 작업을 선택하세요 (1: 출근, 2: 퇴근, 3: 기록 삭제, 4: 기록 수정, q: 종료): ").strip()
            
            if action == '1':
                print("\n[시간 입력 안내]")
                print("- 직접 입력: HH:MM:SS 형식 (예: 09:30:00)")
                print("- 랜덤 생성: 그냥 엔터(Enter) 키를 누르세요")
                time_input = input("입력: ").strip()
                specific_time = time_input if time_input else None
                google_client.check_in(spreadsheet, employee, specific_time)
                break
            elif action == '2':
                print("\n[시간 입력 안내]")
                print("- 직접 입력: HH:MM:SS 형식 (예: 21:30:00)")
                print("- 랜덤 생성: 그냥 엔터(Enter) 키를 누르세요")
                time_input = input("입력: ").strip()
                specific_time = time_input if time_input else None
                google_client.check_out(spreadsheet, employee, specific_time)
                break
            elif action == '3':
                date_to_delete = input("삭제할 날짜를 입력하세요 (YYYY-MM-DD): ").strip()
                if not date_to_delete:
                    print("날짜가 입력되지 않았습니다.")
                else:
                    google_client.delete_record(spreadsheet, employee.get('id'), date_to_delete)
            elif action == '4':
                date_to_edit = input("수정할 날짜를 입력하세요 (YYYY-MM-DD): ").strip()
                if not date_to_edit:
                    print("날짜가 입력되지 않았습니다.")
                    continue
                
                print("\n[수정할 항목 선택]")
                print("1. 출근 시간")
                print("2. 퇴근 시간")
                edit_type = input("선택: ").strip()
                
                new_time = input("새로운 시간을 입력하세요 (HH:MM:SS): ").strip()
                if not new_time:
                    print("시간이 입력되지 않았습니다.")
                    continue

                if edit_type == '1':
                    google_client.update_record(spreadsheet, employee.get('id'), date_to_edit, checkin=new_time)
                elif edit_type == '2':
                    google_client.update_record(spreadsheet, employee.get('id'), date_to_edit, checkout=new_time)
                else:
                    print("잘못된 선택입니다.")
            elif action.lower() == 'q':
                print("종료합니다.")
                break
            else:
                print("잘못된 입력입니다.")
    else:
        print(f"\n'{name}' 직원을 찾을 수 없습니다.")
        print("등록된 이름인지 확인해주세요.")

if __name__ == "__main__":
    main()
