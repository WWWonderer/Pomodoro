# Can be used to generate test data for GUI's data visualization

import random
from datetime import datetime, timedelta
import os
import numpy as np

MAX_TIME_PER_SESSION = 25
MAX_SESSIONS_PER_DAY = 10
SPARCITY = 0.8
DATA_FOLDER = os.path.join(os.getenv("APPDATA"), "Pomodoro")

def generate(start_date, end_date, max_time_per_session, max_sessions_per_day, sparcity):
    test_data_start_times = []
    test_data_end_times = []
    current_date = start_date
    while current_date < end_date:
        r = random.random()
        if r > sparcity:
            current_date = current_date + timedelta(days=1) 
            continue
        test_data_start_times.append(round(current_date.year + current_date.month/100 + current_date.day/10000, 4))
        test_data_end_times.append(round(current_date.year + current_date.month/100 + current_date.day/10000, 4))
        
        session_cnt = 0
        start_limit = 0
        end_limit = random.randint(1, 1440) 
        while session_cnt < max_sessions_per_day:
            try:
                start_time = random.randint(start_limit, end_limit - 1)
                end_time = min(end_limit, start_time + random.randint(1, max_time_per_session))
            except ValueError:
                break
            
            test_data_start_times.append(start_time)
            test_data_end_times.append(end_time)
            start_limit = end_time + 1
            session_cnt += 1

        current_date = current_date + timedelta(days=1)

    return test_data_start_times, test_data_end_times

def generate_month(year, month):
    start_date = datetime.strptime(f'{year}-{month}-01', '%Y-%m-%d')
    next_month = month + 1
    if month == 12:
        end_date = datetime.strptime(f'{year}-{month}-31', '%Y-%m-%d')
    else:
        end_date = datetime.strptime(f'{year}-{next_month}-01', '%Y-%m-%d') - timedelta(days=1)

    starts, ends = generate(start_date, end_date, MAX_TIME_PER_SESSION, MAX_SESSIONS_PER_DAY, SPARCITY)
    save_monthly_data(starts, ends, year, month)

def generate_year(year):
    for month in range(1, 13):
        generate_month(year, month)

def save_monthly_data(start_times, end_times, year, month):
        filename = str(year) + '_' + str(month) + '.csv'
        filepath = os.path.join(DATA_FOLDER, filename)
        os.makedirs(DATA_FOLDER, exist_ok=True)
        data = [start_times, end_times]
        with open(filepath, 'w') as f:
            for i in data:
                np.savetxt(f, [i], delimiter=',', fmt='%.4f')

if __name__ == '__main__':
    generate_year(2000)
