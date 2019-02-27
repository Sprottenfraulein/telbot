import json
import modules.db
import datetime

button_row = []
button_grid = []

def quick_keyboard(buttons):
    row = []
    grid = []
    for i in buttons:
        button = {'text': i[0], 'callback_data': i[1]}
        row.append(button)
    grid.append(row[:])
    row.clear
    keyboard = json.dumps({'inline_keyboard': grid})
    grid.clear()
    return keyboard

def new_button(text, data):
    button = {'text': text, 'callback_data': data}
    button_row.append(button)

def close_row():
    button_grid.append(button_row[:])
    button_row.clear()

def get_inline_keyboard():
    json_keyboard = json.dumps({'inline_keyboard': button_grid})
    button_grid.clear()
    #print("Just received json keyboard string: \n", json_keyboard)
    return json_keyboard

def generate_checklist_totals(checklist_id):
    totals = modules.db.get_checklist_total(checklist_id)
    total_buys_info = ''
    if totals[0] > 0:
        total_buys_info = '🏷' + str(totals[0]) + '' + '💰' + str(totals[1])
    total_items_info = ''
    if totals[2] > 0:
        total_items_info = '💡' + str(totals[2])
    separator = ''
    if total_buys_info and total_items_info:
        separator = ' '
    if sum(totals) == 0:
        return ''
    else:
        #return ' {1}{0}{2}'.format(separator, total_items_info, total_buys_info)
        return '{1}{0}{2}'.format(separator, total_items_info, total_buys_info)

def datetime_to_timestamp(dt):
    time_stamp_to_minutes = round((dt - datetime.datetime(1970,1,1)).total_seconds() // 60)
    print(dt, 'is', time_stamp_to_minutes, 'minutes.')
    return time_stamp_to_minutes

def timestamp_to_datetime(timestamp):
    dt = datetime.datetime(1970,1,1) + datetime.timedelta(seconds = timestamp * 60)
    print(timestamp, 'minutes is', dt)
    return dt

def string_to_alarm(string, user_id):
    alarm_list = string.split(' ')
    parsed_string = parse_datetime(alarm_list[0], alarm_list[1], user_id)
    if parsed_string != -1:
        dt = datetime_to_timestamp(parsed_string)
        alarm = {'datetime': dt}
        print(string, 'is parsed as', alarm['datetime'])
        try:
            alarm['note'] = ' '.join(alarm_list[2:])
            print('the note is', alarm['note'])
            return alarm
        except:
            alarm['note'] = ''
            return alarm
    else:
        return -1

def parse_datetime(date, time, user_id):
    try:
        splitters = ',/_\\:- |'
        for i in splitters:
            date = date.replace(i,'.')
            time = time.replace(i,':')
        date_list = date.split('.')
        time_list = time.split(':')
        try:
            date_list[0] = int(date_list[0])
        except:
            date_list[0] = 1
        try:
            date_list[1] = int(date_list[1])
        except:
            date_list[1] = 1
        try:
            date_list[2] = int(date_list[2])
        except:
            date_list[2] = 1970
        try:
            time_list[0] = int(time_list[0])
        except:
            time_list[0] = 12
        try:
            time_list[1] = int(time_list[1])
        except:
            time_list[1] = 0
        valid_datetime = timezone_user_to_server(date_list[2], date_list[1], date_list[0], time_list[0], time_list[1], user_id)
        return valid_datetime
    except:
        return -1

def validate_datetime(year, month, day, hours, minutes):
    while minutes > 59:
        minutes -= 60
        hours += 1
    while minutes < 0:
        minutes += 60
        hours -= 1
    while hours > 23:
        hours -= 24
        day += 1
    while hours < 0:
        hours += 24
        day -= 1  
    while day > days_in_month(month, year):
        day -= days_in_month(month, year)
        month += 1
    while day < 1:
        day += days_in_month(month - 1, year)
        month -= 1
    while month > 12:
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1
    return datetime.datetime(year, month, day, hours, minutes)

def days_in_month(month, year):
    while month < 1:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1
    if month in (1,3,5,7,8,10,12):
        max_day = 31
    elif month in (4,6,9,11):
        max_day = 30
    elif month == 2:
        if year % 4 != 0 or (year % 100 == 0 and year % 400 != 0):
            max_day = 28
        else:
            max_day = 29
    return max_day

def timezone_user_to_server(year, month, day, hours, minutes, user_id):
    tz_user = modules.db.get_value('timezone', 'users', 'tel_id', user_id) or 0
    hours -= tz_user 
    hours += 3 # Moscow timezone where the server is located
    return validate_datetime(year, month, day, hours, minutes)

def timezone_server_to_user(year, month, day, hours, minutes, user_id):
    tz_user = modules.db.get_value('timezone', 'users', 'tel_id', user_id) or 0
    hours -= 3 # Moscow timezone where the server is located
    hours += tz_user 
    return validate_datetime(year, month, day, hours, minutes)

def user_local_datetime(fulldatetime, user_id):
    return friendly_datetime(timezone_server_to_user(fulldatetime.year, fulldatetime.month, fulldatetime.day, fulldatetime.hour, fulldatetime.minute, user_id))

def friendly_datetime(fulldatetime):
    string = ''
    string += str(fulldatetime.hour) + ':' + str(fulldatetime.minute).zfill(2) + ', '
    string += str(fulldatetime.day) + ' '
    string += ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'][fulldatetime.month - 1] + ' '
    string += str(fulldatetime.year) + ' г.'
    return string