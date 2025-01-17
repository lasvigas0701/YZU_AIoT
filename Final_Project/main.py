import attendance
import cheating
# import cheating_test
# import test
# import roll_test

while True:
    print("\n===Function code===")
    print("1: Roll Attendance\n2: Cheating Detection\n3: End program")
    cmd = int(input("Please enter the function code: "))
    if cmd == 1:
        attendance.main()
    elif cmd == 2:
        cheating.main()
    elif cmd == 3:
        print("Exiting program...")
        exit()
    else:
        print("Invalid input. Please try again.")