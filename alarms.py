import config
import modules.bothandle
import modules.db
import modules.tools

the_bot = modules.bothandle.BotHandle(config.telbot_config['bot_token'])   

def check_alarm_done(alarm_id):
    print('Checking alarm', alarm_id, 'as done...')
    sql = 'UPDATE alarms SET done = 1 WHERE id = %s'
    val = (int(alarm_id),)
    modules.db.mycursor.execute(sql, val)
    modules.db.mydb.commit()

def telbot_send_alarms(alarms_list):
    now = modules.bothandle.datetime.datetime.now()
    for alarm in alarms_list:
        message = ''
        message += '\n\nНАПОМИНАНИЕ'
        if alarm['item_card'][3] == '1':
            checkbox = 'V'
        else:
            checkbox = ''
        if alarm['item_card'][2] > 0:
            price = ' $' + str(alarm['item_card'][2])
        else:
            price = ''
        author = modules.db.get_user_info([alarm['item_card'][4],], 'tel_username')[0][0]
        message += ('\n' + checkbox + alarm['item_card'][1] + price + ' (' + author + ')')
        message += ('\nИз списка ' + alarm['checklist_card'][1] + modules.tools.generate_checklist_totals(alarm['checklist_card'][0]))
        message += '\n'
        message += alarm['alarm_note']

        modules.tools.new_button('К спискам', 'all_checklists')
        modules.tools.new_button('💡 Подробнее', 'show_checklist_item_details-' + str(alarm['checklist_card'][0]) + '-' + str(alarm['item_card'][0]))
        modules.tools.close_row()
        keyboard = modules.tools.get_inline_keyboard()

        users_to_announce = ','.join(alarm['checklist_card'][4:6]).replace(',', ' ').strip().split(' ')
        if not alarm['checklist_card'][6] in users_to_announce:
            users_to_announce.append(alarm['checklist_card'][6])
        for user in users_to_announce:
            custom_time_message = ''
            custom_time_message += ('Сейчас ' + str(modules.tools.user_local_datetime(now, user)) + '')
            custom_time_message += ('\nНапоминание на ' + str(modules.tools.user_local_datetime(modules.tools.timestamp_to_datetime(int(alarm['datetime'])), user)))
            print('Send message to', user, ':\n', custom_time_message + message)
            try:
                the_bot.send_message(user, custom_time_message + message, keyboard)
            except:
                print('Send message failed (', user, ':\n', custom_time_message + message, ')')
        
        check_alarm_done(alarm['id'])

def telbot_checklists_alarms(alarms_table):
    alarms_list = []
    for alarm in alarms_table:
        alarm_id = alarm[0]
        checklist_id = alarm[1]
        item_id = alarm[2]
        
        sql = 'SELECT * FROM checklists WHERE id = %s'
        val = (checklist_id,)
        modules.db.mycursor.execute(sql, val)
        checklist = mycursor.fetchall()[0]

        sql = 'SELECT * FROM {0} WHERE id = %s'.format('checklist' + str(checklist_id))
        val = (item_id,)
        modules.db.mycursor.execute(sql, val)
        item = mycursor.fetchall()[0]

        alarms_list.append({'id': alarm_id, 'checklist_card': checklist, 'item_card': item, 'datetime': alarm[3], 'alarm_note': alarm[4]})
    print(alarms_list)
    return alarms_list

def check_alarms(timestamp):
    sql = 'SELECT * FROM alarms WHERE datetime <= %s AND done <> 1 ORDER BY id ASC'
    val = (int(timestamp),)
    modules.db.mycursor.execute(sql, val)
    return modules.db.mycursor.fetchall()

def run_alarms_check():  
    now = modules.bothandle.datetime.datetime.now()

    new_offset = None
    today = now.day
    hour = now.hour

    print('Time convertion test:')
    modules.tools.timestamp_to_datetime(modules.tools.datetime_to_timestamp(now))

    hot_alarms = check_alarms(modules.tools.datetime_to_timestamp(now))
    print('Actual alarms:\n', hot_alarms)
    alarms_list = telbot_checklists_alarms(hot_alarms)
    telbot_send_alarms(alarms_list)
