from datetime import date, timedelta, datetime

days = list()
start_date_string = '2022-02-05'
start_date = datetime.strptime(start_date_string, '%Y-%m-%d').date()
today_date = date.today()
intermediate_day = start_date
while intermediate_day <= today_date:
    days.append(intermediate_day.strftime('%d.%m'))
    intermediate_day += timedelta(days=1)

print(days)