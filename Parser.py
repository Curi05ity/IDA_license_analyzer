import re
from datetime import datetime

def parse_log_entry(line):
    """
    Parse a log entry line, returning a tuple of the timestamp, action (IN/OUT), license, user, and machine.
    Return None if the line doesn't match the expected format.
    """
    match = re.match(r'( ?\d{1,2}:\d{2}:\d{2}) \(hexrays\) (IN|OUT): "([^"]+)" (\S+)@(\S+).*', line)
    if match:
        return match.groups()[:5]
    return None

def process_log_file(filepath):
    sessions = {}  # {license: {timestamp: count}}
    max_concurrent_sessions = {}
    prev_timestamp = None
    prev_user_machine = {} # {license : user}
    current_users_per_license = {}
    with open(filepath, 'r') as file:
        for line in file:
            entry = parse_log_entry(line)
            if entry:
                time_str, action, license, user, machine = entry
                time_str = time_str.strip()
                # Convert time_str to a datetime object (assuming date is not relevant for the calculation)
                timestamp = datetime.strptime(time_str, '%H:%M:%S').time()
                if license not in sessions:
                    sessions[license] = 0
                if prev_timestamp and timestamp < prev_timestamp:
                    for license_item in sessions:
                        sessions[license_item]  = 0
                if license not in current_users_per_license:
                    current_users_per_license[license] = set()
                if action == 'OUT':
                    #if not prev_user_machine or license not in prev_user_machine or user not in prev_user_machine[license]:
                    if user not in current_users_per_license[license]:
                        sessions[license] += 1
                        if license not in max_concurrent_sessions:
                            max_concurrent_sessions[license] = sessions[license] #license = 1
                        else:
                            max_concurrent_sessions[license] = max(max_concurrent_sessions[license], sessions[license])
                            #if license == "IDAPROFW" and max_concurrent_sessions[license] == 3:
                             #   print('IDAPROFW' + ' | ' + timestamp.__str__())
                    prev_user_machine[license] = user
                    current_users_per_license[license].add(user)
                elif action == 'IN':
                    sessions[license] -= 1
                    if user in current_users_per_license[license]: current_users_per_license[license].remove(user)

                prev_timestamp = timestamp

    return max_concurrent_sessions

def print_max_concurrent_sessions_table(max_concurrent_sessions):
    print(f'{"License":<20} | {"Max Concurrent Sessions":<20}')
    print('-' * 42)
    for license, max_sessions in max_concurrent_sessions.items():
        print(f'{license:<20} | {max_sessions:<20}')

if __name__ == '__main__':
    log_file_path = r"C:\Users\lavi\Desktop\hexrays_22_23.txt"  # Update this to the path of your log file
    max_concurrent_sessions = process_log_file(log_file_path)
    print_max_concurrent_sessions_table(max_concurrent_sessions)
