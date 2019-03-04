#Модуль распознания команд

import modules.db
import modules.authorize
import modules.bothandle
import modules.tools
import datetime

todo_list = []
names_list = []
hashtags_list = []
cashtags_list = []
bold_list = []

def update_users_list(user_from, the_bot):
    the_bot.get_user_avatar(user_from['id'], 0, 100)

def checklist_pass_to_children(checklist_id, user_id):
    checklist = modules.db.get_checklist(checklist_id)
    for i in checklist:
        if i[10] and i[10] > 0:
            modules.db.checklist_inherit(checklist_id, i[10])

def get_checklists_tags(user_id):
    return modules.db.get_hashtag_mentions_chart('count', 'DESC', user_id)

def compose_checklists_tags(user_id):
    tag_cloud = get_checklists_tags(user_id)
    tag_list = []
    for key, value in sorted(tag_cloud.items(), key=lambda item: (-item[1], item[0]), reverse = False):
        #string += '#' + key + ' (' + str(value) + '), '
        tag_list.append('#' + key + ' <i>' + str(value) + '</i>')
    string = '\n' + ', '.join(tag_list)
    tag_list.clear()
    return string

def generate_checklist_alarm_info(checklist_table, item_table, alarm_id, user_id):
    item_alarm = modules.db.read_from_db('*', 'alarms', 'id', [int(alarm_id),], '', '', '')
    if item_alarm:
        if item_table[0][3] == 0:
            checkbox_icon = ''
        if item_table[0][3] == 1:
            checkbox_icon = '✔️'
        string = ''
        string += "Start → Списки → 📒 " + checklist_table[0][1]
        string += modules.tools.generate_checklist_totals(checklist_table[0][0])
        if item_table[0][2] > 0:
            item_cost_info = ', 💰' + str(item_table[0][2])
        else:
            item_cost_info = ''
        string += ' → ' + str(item_table[0][1]) + item_cost_info
        if item_alarm[0][5] == 0:
            checkbox_icon = ''
        if item_alarm[0][5] == 1:
            checkbox_icon = '✔️'
        print(item_alarm)
        string += '\n\n'
        string += checkbox_icon + '' + str(modules.tools.friendly_datetime(modules.tools.timestamp_to_datetime(int(item_alarm[0][3])))) + ''
        string += '\n' + str(item_alarm[0][4])
        return string
    return 'This alarm is orphan'

def generate_sorting_tips(checklist_info, user_id):
    string = ''
    string += 'Сортировка списка:\n🏷 по наименованию\n💰 по цене\n⏱ по времени добавления\n▲ в порядке возрастания\n▼ в порядке убывания'
    return string

def generate_checklist_item_details_tips(checklist_table, item_table, user_id):
    if item_table[0][3] == 0:
        checkbox_icon = ''
    if item_table[0][3] == 1:
        checkbox_icon = '✔️'
    string = ''
    string += "Start → Списки → 📒 " + checklist_table[0][1]
    string += modules.tools.generate_checklist_totals(checklist_table[0][0])
    if item_table[0][2] > 0:
        item_cost_info = ', 💰' + str(item_table[0][2])
    else:
        item_cost_info = ''
    string += '\n\n' + str(item_table[0][1]) + item_cost_info + ''
    string += '\n' + str(item_table[0][6] or '(нет описания)')
    item_alarms = modules.db.checklist_item_get_alarm(checklist_table[0][0], item_table[0][0], user_id)
    if item_alarms:
        string += '\n\nНапоминания:'
        for item_alarm in item_alarms:
            if item_alarm[5] == 0:
                checkbox_icon = ''
            if item_alarm[5] == 1:
                checkbox_icon = '✔️'
            print(item_alarm)
            string += '\n'
            string += checkbox_icon + str(modules.tools.user_local_datetime(modules.tools.timestamp_to_datetime(int(item_alarm[3])), user_id)) + ' (' + str(item_alarm[4]) + ')'
    string += '\n\nЗапись добавлена ' + modules.tools.user_local_datetime(item_table[0][5], user_id) #+ ' @' + modules.db.get_user_info([item_table[0][4],], 'tel_firstname')[0][0]
    return string

def generate_checklist_tips(checklist_info, user_id):
    string = ''
    string += '\n\n'
    if str(user_id) == str(checklist_info[0][6]):
        if checklist_info[0][4]:
            string += 'Смотрят: '
            for user_info in modules.db.get_user_info(checklist_info[0][4].split(','), 'tel_username'):
                string += ('@' + user_info[0] + ' ')
            string += '\n'    
        if checklist_info[0][5]:
            string += 'Редактируют: '
            for user_info in modules.db.get_user_info((checklist_info[0][6] + ',' + checklist_info[0][5]).split(','), 'tel_username'):
                string += ('@' + user_info[0] + ' ')
            string += '\n'
    if str(user_id) in checklist_info[0][5] or str(user_id) == str(checklist_info[0][6]):
        string += 'Автор: '
        string += ('@' + modules.db.get_user_info([checklist_info[0][6],], 'tel_username')[0][0])

    string += '\n'
    string += 'Создан: '
    string += (modules.tools.user_local_datetime(checklist_info[0][8], user_id))

    string += '\n'
    string += 'Изменен: '
    string += (modules.tools.user_local_datetime(checklist_info[0][7], user_id))

    #breadcrumps
    string += '\n\nStart → Списки → 📒 ' + checklist_info[0][1] + ''
    #total
    string += modules.tools.generate_checklist_totals(checklist_info[0][0])
    #hashtags
    string += '\n\n'
    for i in modules.db.get_checklist_hashtags(checklist_info[0][0],'count', 'DESC', user_id):
        string += ('#' + i[1] + ' ')
    return string

def generate_users_management_tips(checklist_info, user_id):
    string = ''
    #breadcrumps
    string += '\n\nStart → Списки → 📒 ' + checklist_info[0][1] + ''
    #total
    string += modules.tools.generate_checklist_totals(checklist_info[0][0]) + ' →\n\n'
    string += 'Настройки списка\n'
    if checklist_info[0][4]:
        string += 'Смотрят: '
        for user_info in modules.db.get_user_info(checklist_info[0][4].split(','), 'tel_username'):
            string += ('@' + user_info[0] + ' ')
        string += '\n'
    if checklist_info[0][5]:
        string += 'Редактируют: '
        for user_info in modules.db.get_user_info(checklist_info[0][5].split(','), 'tel_username'):
            string += ('@' + user_info[0] + ' ')
        string += '\n'
    string += 'Автор: '
    string += ('@' + modules.db.get_user_info([checklist_info[0][6],], 'tel_username')[0][0])
    string += '\n'
    string += 'Дата создания списка: '
    string += (modules.tools.user_local_datetime(checklist_info[0][8], user_id))
    string += '\n'
    string += 'Дата последнего изменения: '
    string += (modules.tools.user_local_datetime(checklist_info[0][7], user_id))
    #hashtags
    string += '\n\n'
    for i in modules.db.get_checklist_hashtags(checklist_info[0][0],'count', 'DESC', user_id):
        string += ('#' + i[1] + ' ')
    return string

def generate_checklist_access_tips(checklist_id, access_type, user_id):
    checklist_info = modules.db.get_checklists("id", int(checklist_id), user_id)
    string = ''
    #breadcrumps
    string += '\n\nStart → Списки → 📒 ' + checklist_info[0][1] + ''
    #total
    string += modules.tools.generate_checklist_totals(checklist_info[0][0]) + ' →\n\n'
    string += 'Права пользователей\n'
    if checklist_info[0][4]:
        string += 'Смотрят: '
        for user_info in modules.db.get_user_info(checklist_info[0][4].split(','), 'tel_username'):
            string += ('@' + user_info[0] + ' ')
        string += '\n'
    if checklist_info[0][5]:
        string += 'Редактируют: '
        for user_info in modules.db.get_user_info(checklist_info[0][5].split(','), 'tel_username'):
            string += ('@' + user_info[0] + ' ')
        string += '\n'
    string += 'Автор: '
    string += ('@' + modules.db.get_user_info([checklist_info[0][6],], 'tel_username')[0][0])
    return string

def generate_checklist_hashtags_tips(checklist_info, user_id):
    string = ''
    #breadcrumps
    string += '\n\nStart → Списки → 📒 ' + checklist_info[0][1] + ''
    string += modules.tools.generate_checklist_totals(checklist_info[0][0])
    string += '\n'
    #hashtags
    string += '\n'
    for i in modules.db.get_checklist_hashtags(checklist_info[0][0],'count', 'DESC', user_id):
        string += ('#' + i[1] + ' ')
    return string

def generate_checklists_tips(type):
    tips_string = ''
    if type == "all_checklists" or type == "viewable_checklists" or type == "editable_checklists" or type == "my_checklists" or type == 'public_checklists':
        tips_string += "⌂ вернуться в начало\n📣 публичные списки \n👭 все совместные списки\n# поиск списков по тегам \n👁 списки только для просмотра\n✍🏻 списки доступные для редактирования\n©️ списки созданные вами"
    if type == "hashtag_checklists":
        tips_string += 'Поиск списков по хэштегам. Отправьте сообщение с одним или несколькими ключевыми словами для поиска среди доступных вам списков по тегам.'
    return tips_string

def generate_start_tips():
    return "🛍 S O C I A L L I S T S 🛍\n\nВместе со своими друзьями, коллегами, близкими создавайте и редактируйте списки важных дел, покупок, сохраняйте памятки и заводите будильники чтобы ничего не пропустить! 😃 В вашем распоряжении вложенные списки, картинки и текстовые описания для каждого пункта, а также удобный интерфейс.\nНажмите на кнопку ниже, чтобы начать.\n \
    \n(Created by Laima Renard)"

def compose_checklists_gui(checklists, nav_back, user_id, type):
    modules.tools.new_button('⌂', 'nav_to_start')
    modules.tools.new_button('📣', 'public_checklists')
    modules.tools.new_button('👭', 'all_checklists')
    if nav_back == 'hashtag_checklists':
        modules.tools.new_button('←', nav_back)    
    else:
        modules.tools.new_button('#', 'hashtag_checklists')
    modules.tools.new_button('👁', 'viewable_checklists')
    modules.tools.new_button('✍🏻', 'editable_checklists')
    modules.tools.new_button('©', 'my_checklists')
    modules.tools.close_row()
    for checklist in checklists:
        if checklist[2] != 'sub':
            modules.tools.new_button('📒 ' + checklist[1] + ' ' + modules.tools.generate_checklist_totals(checklist[0]), 'checklist_items_info-' + str(checklist[0]))
            modules.tools.close_row()
    if not type == 'public_checklists':
        modules.tools.new_button('＋', 'new_checklist')
        modules.tools.close_row()
    return generate_checklists_tips(type)

def compose_checklist_gui(checklist_table, checklist_id, item_icon, checklist_function, nav_back, user_id):
    parent = modules.db.get_checklists('id', checklist_id, user_id)[0][3].split('-')[0]
    if parent != '0':
        modules.tools.new_button('←', 'checklist_items_info-' + str(parent))  
    else:
        modules.tools.new_button('←', nav_back)   
    user_rights = modules.db.get_user_rights(user_id, checklist_id)
    
    if user_rights in ('creator', 'editor'):
        if checklist_function != 'toggle_item_in_checklist-':
            modules.tools.new_button('🔳', 'checklist_items_toggle-'+str(checklist_id))
        else:
            modules.tools.new_button('OK', 'checklist_items_info-'+str(checklist_id))
        if checklist_function != 'hide_item_in_checklist-':
            modules.tools.new_button('➖', 'checklist_items_delete-'+str(checklist_id))
        else:
            modules.tools.new_button('OK', 'checklist_items_info-'+str(checklist_id))
        modules.tools.new_button('📶', 'checklist_items_sort-'+str(checklist_id))
    else:
        modules.tools.new_button(' ', 'no_command')
        modules.tools.new_button(' ', 'no_command')
        modules.tools.new_button(' ', 'no_command')
    if user_rights == 'creator':
        modules.tools.new_button('🔑', 'checklist_users-'+str(checklist_id))
        modules.tools.new_button('❌', 'checklist_hide-'+str(checklist_id))
    else:
        modules.tools.new_button(' ', 'no_command')
        modules.tools.new_button(' ', 'no_command')
    modules.tools.close_row()

    if checklist_table != -1:
        for table_row in checklist_table:
            checkbox_icon = ' '
            if table_row[3] == 0:
                if checklist_function == 'toggle_item_in_checklist-':
                    checkbox_icon = '⬜️'
                else:
                    checkbox_icon = ' '
            elif table_row[3] == 1:
                if checklist_function == 'toggle_item_in_checklist-':
                    checkbox_icon = '🔳'
                else:
                    checkbox_icon = '◼️'
            if table_row[2] and table_row[2] > 0:
                item_cost_info = ', 💰' + str(table_row[2])
            else:
                item_cost_info = ''
            alarm_count = ''
            alarms = modules.db.checklist_item_get_alarm(checklist_id, table_row[0], user_id)
            if alarms:
                alarm_count = ' ⏰' + str(len(alarms))
            if table_row[10] and table_row[10] > 0:
                checklist_link = modules.db.get_checklists('id', table_row[10], user_id)
                modules.tools.new_button('📒 ' + checklist_link[0][1] + ' ' + modules.tools.generate_checklist_totals(checklist_link[0][0]) + ' ', 'checklist_items_info-' + str(table_row[10]))
            else:
                modules.tools.new_button(item_icon + ' ' + checkbox_icon + " " +table_row[1] + item_cost_info + alarm_count + ' ', checklist_function + str(checklist_id)+'-'+str(table_row[0]))

            modules.tools.close_row()
        if user_rights in ('creator', 'editor', 'pub_add'):
            modules.tools.new_button('＋', 'checklist_add_item-'+str(checklist_id))
            modules.tools.close_row()

def compose_checklist_item_details_gui(checklist_table, item_table, nav_back, user_id):
    user_rights = modules.db.get_user_rights(user_id, checklist_table[0][0])
    if user_rights in ('creator', 'editor') and checklist_table[0][11] == 1:
        modules.tools.new_button('Редактировать название', 'edit_checklist_item_name-' + str(checklist_table[0][0]) + '-' + str(item_table[0][0]))
        modules.tools.close_row()
    modules.tools.new_button('←', nav_back)
    modules.tools.new_button('👭', 'all_checklists')
    modules.tools.new_button('📄📄', 'checklist_item_transfer-copy-' + str(checklist_table[0][0]) + '-' + str(item_table[0][0]))
    if user_rights in ('creator', 'editor') and checklist_table[0][11] == 1:
        modules.tools.new_button('📄→', 'checklist_item_transfer-move-' + str(checklist_table[0][0]) + '-' + str(item_table[0][0]))
        modules.tools.new_button('⏰', 'checklist_item_alarm-' + str(checklist_table[0][0]) + '-' + str(item_table[0][0]))
        modules.tools.new_button('❌', 'hide_item_in_checklist-' + str(checklist_table[0][0]) + '-' + str(item_table[0][0]))
    else:
        modules.tools.new_button(' ', 'no_command')
        modules.tools.new_button(' ', 'no_command')
        modules.tools.new_button(' ', 'no_command')
    modules.tools.close_row()

def compose_sorting_gui(checklist_table, checklist_id, checklist_function, nav_back, user_id):
    user_rights = modules.db.get_user_rights(user_id, checklist_id)
    modules.tools.new_button('←', nav_back)
    modules.tools.new_button('⌂', 'nav_to_start')
    modules.tools.new_button('️️✔️▲', 'checklist_sort-' + str(checklist_id) + '-checkbox-asc')
    modules.tools.new_button('🏷▲', 'checklist_sort-' + str(checklist_id) + '-item-asc')
    modules.tools.new_button('💰▲', 'checklist_sort-' + str(checklist_id) + '-cost-asc')
    modules.tools.new_button('⏱▲', 'checklist_sort-' + str(checklist_id) + '-lastedit_time-asc')
    modules.tools.close_row()
    modules.tools.new_button(' ', 'no_command')
    modules.tools.new_button(' ', 'no_command')
    modules.tools.new_button('✔️▼', 'checklist_sort-' + str(checklist_id) + '-item-desc')
    modules.tools.new_button('🏷▼', 'checklist_sort-' + str(checklist_id) + '-item-desc')
    modules.tools.new_button('💰▼', 'checklist_sort-' + str(checklist_id) + '-cost-desc')
    modules.tools.new_button('⏱▼', 'checklist_sort-' + str(checklist_id) + '-lastedit_time-desc')
    modules.tools.close_row()

    if checklist_table != -1:
        for table_row in checklist_table:
            checkbox_icon = ' '
            if table_row[3] == 0:
                checkbox_icon = ' '
            elif table_row[3] == 1:
                checkbox_icon = "✔️"
            if table_row[2] > 0:
                item_cost_info = ', 💰' + str(table_row[2])
            else:
                item_cost_info = ''
            modules.tools.new_button(checkbox_icon + " " +table_row[1]+ item_cost_info, checklist_function+str(checklist_id)+'-'+str(table_row[0]))
            modules.tools.close_row()

def compose_checklist_item_alarm_gui(checklist_id, item_id, button_function, nav_back, user_id):
    modules.tools.new_button('←', nav_back)
    modules.tools.new_button('⌂', 'nav_to_start')
    modules.tools.new_button('👭', 'all_checklists')
    modules.tools.close_row()
    for alarm in modules.db.checklist_item_get_alarm(checklist_id, item_id, user_id):
        if alarm[5] == 1:
            checkbox_icon = '✔️'
        if alarm[5] == 0:
            checkbox_icon = ' '
        modules.tools.new_button(checkbox_icon + str(modules.tools.user_local_datetime(modules.tools.timestamp_to_datetime(int(alarm[3])), user_id)), button_function + '-' + str(alarm[0]))
        modules.tools.close_row()
    user_rights = modules.db.get_user_rights(user_id, checklist_id)
    if user_rights in ('creator', 'editor'):
        modules.tools.new_button('＋', 'checklist_item_alarm_new-'+str(checklist_id) + '-' + item_id)
        modules.tools.close_row()

def compose_checklist_item_alarm_info_gui(checklist_id, item_id, alert_id, nav_back, user_id):
    modules.tools.new_button('←', nav_back)
    modules.tools.new_button('⌂', 'nav_to_start')
    modules.tools.new_button('👭', 'all_checklists')
    modules.tools.new_button('✍🏻', 'checklist_item_alarm_note_edit-' + str(checklist_id) + '-' + str(item_id) + '-' + str(alert_id))
    modules.tools.new_button('❌', 'delete_checklist_item_alarm-' + str(checklist_id) + '-' + str(item_id) + '-' + str(alert_id))
    modules.tools.close_row()

def compose_checklist_management_gui(checklist_id, user_id):
    modules.tools.new_button('←', 'checklist_items_info-' + str(checklist_id))
    modules.tools.new_button('Имя', 'checklist_name_edit-' + str(checklist_id))
    modules.tools.new_button('Тэги', 'checklist_hashtags_edit-' + str(checklist_id))
    modules.tools.new_button('Доступ', 'checklist_access-allowview-' + str(checklist_id))
    modules.tools.close_row()

def compose_checklist_hashtags_gui(checklist_info, checklist_function, nav_back, user_id):
    modules.tools.new_button('←', nav_back)
    if checklist_function == 'checklist_hashtags_add-':
        modules.tools.new_button('Удалять', 'checklist_hashtags_delete-' + str(checklist_info[0][0]))
    else:
        modules.tools.new_button('Добавлять', 'checklist_hashtags_edit-' + str(checklist_info[0][0]))
    modules.tools.new_button(' ', 'no_command')
    modules.tools.new_button(' ', 'no_command')
    modules.tools.close_row()
    if checklist_function == 'checklist_hashtags_add-':
        items_per_row = 2
        items_counter = 0
        for i in get_checklists_tags(user_id):
            modules.tools.new_button('#' + str(i[1]), checklist_function + str(checklist_info[0][0]) + '-' + i[1])
            items_counter += 1
            if items_counter >= items_per_row:
                modules.tools.close_row()
                items_counter = 0
        modules.tools.close_row()
    else:
        items_per_row = 2
        items_counter = 0
        for i in modules.db.get_checklist_hashtags(checklist_info[0][0],'count', 'DESC', user_id):
            modules.tools.new_button('❌ ' + '#' + i[1], checklist_function + str(checklist_info[0][0]) + '-' + i[1])
            items_counter += 1
            if items_counter >= items_per_row:
                modules.tools.close_row()
                items_counter = 0
        modules.tools.close_row()
        

def compose_checklist_access_gui(checklist_id, user_id, button_function, nav_back):
    checklist_table_info = modules.db.get_checklists("id", int(checklist_id), user_id)
    modules.tools.new_button('←', nav_back)
    if button_function == 'checklist_access-allowview-':
        modules.tools.new_button('✍🏻 Редактирование', 'checklist_access-allowedit-' + str(checklist_id))
    elif button_function == 'checklist_access-allowedit-':
        modules.tools.new_button('👁 Просмотр', 'checklist_access-allowview-' + str(checklist_id))
    modules.tools.close_row()
    for i in modules.db.get_user_mentions_chart('count', 'DESC', user_id):
        if str(i[1]) not in checklist_table_info[0][6]:
            press_function = button_function
            if button_function =='checklist_access-allowview-':
                if str(i[1]) in checklist_table_info[0][4]:
                    action_icon = '❌'
                    user_icon = 'Закрыть доступ для '
                    press_function = 'checklist_access-remove-'
                elif str(i[1]) in checklist_table_info[0][5]:
                    action_icon = '🔻'
                    user_icon = 'Только просмотр для '
                else:
                    action_icon = '🔸'
                    user_icon = 'Открыть просмотр для '
            if button_function =='checklist_access-allowedit-':
                if str(i[1]) in checklist_table_info[0][4]:
                    action_icon = '🔸'
                    user_icon = 'Просмотр и редактирование '
                elif str(i[1]) in checklist_table_info[0][5]:
                    action_icon = '❌'
                    user_icon = 'Закрыть доступ для '
                    press_function = 'checklist_access-remove-'
                else:
                    action_icon = '❗️🔸'
                    user_icon = 'Позволить редактировать '
            modules.tools.new_button(action_icon + ' ' + user_icon + i[5] + '(' + i[4] + ')', press_function + checklist_id + '-' + str(i[1]))
            modules.tools.close_row()

def compose_transfer_gui(checklists, button_function, nav_back, user_id):
    function_data = button_function.split('-')
    modules.tools.new_button('←', nav_back)
    if function_data[1] == 'copy':
        if modules.db.get_user_rights(user_id, function_data[2]) in ('editor', 'creator'):
            modules.tools.new_button('Перемещать', 'checklist_item_transfer-move-' + '-'.join(function_data[2:4]))
        function_prefix = 'Скопировать в '
    elif function_data[1] == 'move':
        modules.tools.new_button('Копировать', 'checklist_item_transfer-copy-' + '-'.join(function_data[2:4]))
        function_prefix = 'Переместить в '
    else:
        modules.tools.new_button(' ', 'no_command')
    modules.tools.close_row()
    for i in checklists:
        if not function_data[2] == str(i[0]):
            modules.tools.new_button(function_prefix + ' ' + i[1] + ' ' + modules.tools.generate_checklist_totals(i[0]), button_function + str(i[0]))
            modules.tools.close_row()

def collect_entity(entity, type_value, string, collection):
    if entity['type'] == type_value:
        if type_value == 'bold':
            a = entity['offset']
        else:
            a = entity['offset'] + 1
        b = entity['offset'] + entity['length']
        collected_entity = string[a:b]
        if collected_entity not in collection:
            collection.append(collected_entity) 
        if len(collection) > 16:
            del collection[0]
        return collected_entity

def clean_text(string):
    for x in todo_list:
        string = string.replace("/"+x, "")
    for x in names_list:
        string = string.replace("@"+x, "")
    for x in hashtags_list:
        string = string.replace("#"+x, "")
    string = ' '.join(string.split())
    string.strip()
    return string

def string_to_hashtags_list(string): #obsolete
    hashtags_list = []
    for word in string.replace(',',' ').split(' '):
        if word.isalnum() and not word in hashtags_list:
            hashtags_list.append(word)
    return hashtags_list


def generate_help(user_rank):
    help_message = "SocialLists bot, v0.6.\n\n"
    help_message += "Вместе со своими друзьями, коллегами, близкими создавайте и редактируйте списки важных дел, покупок, сохраняйте памятки и заводите будильники чтобы ничего не пропустить! 😃 В вашем распоряжении вложенные списки, картинки и текстовые описания для каждого пункта, а также удобный интерфейс.\n"

    if user_rank == 0:
        help_message += "\nСпасибо, что заглянули в гости, я очень рад случайным посетителям. Приходите еще!\n" #(Или наберите /riddle чтобы попытаться ответить на загадку)\n"

    #checklists service
    if user_rank >= 1:
        help_message += "\nНаберите /myrank чтобы узнать свой уровень доступа. От уровня доступа зависит перечень доступных для выполнения команд. Чем выше уровень -- тем больше возможностей ;)\n"
        help_message += '\nИз меню /start доступна кнопка "Списки". Нажав ее вы попадете в сервис списков с функционалом отметок и настраиваемой приватностью.'
    
    if user_rank >= 3:
        help_message += "\n\nВы можете использовать команду /tell чтобы посылать через меня сообщения пользователям, с которыми я знакома. Укажите в сообщении юзернеймы адресатов (например @abcdefgh1999 и тд) и я доставлю его каждому из них. Естественно, ни команды ни юзернеймы в сообщении не пересылаются. Никто кроме вас не увидит списка рассылки. Наберите команду и юзернейм(ы) в подписи к картинке, чтобы разослать ее по тому же принципу.\n"
    
        if user_rank >= 5:
            help_message += "\nЕсли вы хотите отправить кому-нибудь сообщение инкогнито, добавьте к сообщению команду /nosign ;) \n"
            help_message += "\nВы можете создавать публичные списки, которые видны всем без исключения пользователям в разделе Публичные Списки.\nПри вводе имени нового списка добавьте команду /pub для того чтобы создать публичный список не поддающийся изменениям никому кроме вас. Если вы хотите создать публичный список, в который любой желающий мог бы добавлять наименования, воспользуйтесь командой /pubadd.\n"
            

        if user_rank >= 7:
            help_message += "\nВведите команду /all вместо имен пользователей, чтобы разослать сообщение всем зарегистрированным в боте пользователям."

    if user_rank >= 9:
        help_message += "\n\nВы имеете достаточно высокий уровень доступа для того, чтобы менять уровни доступа других пользователей (включая себя). Для этого укажите в сообщении, наряду с юзернеймами пользователей чьи уровни доступа будут изменены, команду /rank и число от 0 до 9, обозначающее новый уровень доступа для указанных пользователей. Каждый пользователь, чей уровень доступа изменится, получит об этом извещение. Будьте осторожны: если вы понизите свой уровень доступа, то, вероятно, не сможете вновь воспользоваться командой /rank \n"
        help_message += "Чтобы увидеть все списки всех зарегистрированных пользователей, введите команду /alluserschecklists\n"
        help_message += "Чтобы отобразить картотеку пользователей, введите команду /allusers"

    
    if user_rank == 10:
        help_message += "\n\nА еще я знаю, что вы успешно воспользовались командой /skeletonkey. Long Live the Queens!\n"

    return help_message

def comprehend(the_bot, update):
    last_update = update

    last_update_id = last_update['update_id']

    content = -1
    #ВОСПРИЯТИЕ
    if 'from' in last_update:
        content = 'from'
        conversation_id = last_update[content]['chat']['id']
        message_id = int(last_update['message_id'])

    if 'message' in last_update:
        content = 'message'
        conversation_id = last_update[content]['chat']['id']
        message_id = int(last_update[content]['message_id'])

    if 'edited_message' in last_update:
        content = 'edited_message'
        conversation_id = last_update[content]['chat']['id']
        message_id = int(last_update[content]['message_id'])

    if 'channel_post' in last_update:
        content = 'channel_post'
        conversation_id = last_update[content]['chat']['id']

    if 'edited_channel_post' in last_update:
        content = 'edited_channel_post'
        conversation_id = last_update[content]['chat']['id']

    if 'callback_query' in last_update:
        content = 'callback_query'
        conversation_id = last_update[content]['message']['chat']['id']
        message_id = int(last_update[content]['message']['message_id'])

    if content != -1:
        if 'from' in last_update[content]:
            print('Attempting to update sender info←')
            modules.db.update_user_info(last_update[content]['from'])
            user_id = last_update[content]['from']['id']
            update_users_list(last_update[content]['from'], the_bot)
            print('User', last_update[content]['from']['id'], "updated successfully.")

            #ask db about user access rights
            user_rank = modules.db.get_user_rank(user_id)
        else:
            user_id = last_update[content]['chat']['id']
            user_rank = 1
        
        bot_context = modules.db.get_navigation_history(user_id, 0)
        bot_context_card = bot_context.split('-')
        prev_bot_context = modules.db.get_navigation_history(user_id, 1)
        
        print('Bot theme context is: '+ bot_context)

        if 'data' in last_update[content]:
            data = last_update[content]['data']     
        else:
            data = ''   

        entities = -1

        if 'entities' in last_update[content]:
            entities = 'entities'
        
        if 'caption_entities' in last_update[content]:
            entities = 'caption_entities'

        
        string = -1

        if 'text' in last_update[content]:
            string = 'text'
            print('string is text')
        if 'caption' in last_update[content]:
            string = 'caption'
            print('string is caption')
        if entities != -1:
            for x in last_update[content][entities]:
                collect_entity(x, 'bot_command', last_update[content][string], todo_list)
                collect_entity(x, 'mention', last_update[content][string], names_list)
                collect_entity(x, 'hashtag', last_update[content][string], hashtags_list)
                collect_entity(x, 'cashtag', last_update[content][string], cashtags_list)
                collect_entity(x, 'bold', last_update[content][string], bold_list)
            if todo_list:
                print("Received commands from", conversation_id, ':\n', todo_list)
            if names_list: 
                print("Mentioned users by", conversation_id, ':\n', names_list)
                ids_list = []
                for i in modules.db.get_user_id(names_list):
                    ids_list.append(i[1])
                if ids_list:
                    modules.db.store_user_mention(ids_list, user_id)
            if hashtags_list:
                print("Hashtags by", conversation_id, ':\n', hashtags_list)
                #modules.db.store_hashtag_mention(hashtags_list, user_id)
            if cashtags_list:
                print("Cashtags by", conversation_id, ':\n', cashtags_list)
        if string == 'text' or string == 'caption' :
            clean_string = clean_text(last_update[content][string])
            print("Input:", clean_string)
        else:
            clean_string = ''

        
        
        #СЛИВ МЕДИА

        #storing all media
        if 'photo' in last_update[content]:
            #the_bot.download_photo(last_update[content]['photo'][-1]['file_id'], str(user_id))
            incoming_photo_id = last_update[content]['photo'][-1]['file_id']
        else:
            incoming_photo_id = ''
        """
        if 'voice' in last_update[content]:
            the_bot.download_voice(last_update[content]['voice']['file_id'], str(user_id))
        if 'animation' in last_update[content]:
            the_bot.download_animation(last_update[content]['animation']['file_id'], str(user_id))
        if 'video' in last_update[content]:
            the_bot.download_video(last_update[content]['video']['file_id'], str(user_id))
        if 'audio' in last_update[content]:
            the_bot.download_music(last_update[content]['audio']['file_id'], str(user_id))
            """

        default_photo_id = 'AgADAgADT6sxGx2SUErCYavk1g5IHzA-8w4ABJLS4VZn8rOt7SYGAAEC'
        print('------------------------------------------------------------|', modules.tools.user_local_datetime(datetime.datetime.now(), user_id))
        
        if clean_string or incoming_photo_id:
            if bot_context_card[0] == 'checklist_item_name_edit':
                try:
                    user_rights = modules.db.get_user_rights(user_id, bot_context_card[1])
                except:
                    user_rights = 'no_rights'
                if user_rights in ('creator', 'editor'):
                    print("analysing input:", clean_string)
                    cut_string = clean_string.split(' ')
                    try:
                        item_cost = float(cut_string[-1])
                        cut_string.pop()
                    except:
                        item_cost = 0
                    item_name = ' '.join(cut_string)
                    modules.db.update_checklist_item(int(bot_context_card[1]), int(bot_context_card[2]), user_id, '', '', item_name, item_cost)
                    checklist_item = modules.db.get_checklist_item(int(bot_context_card[1]), int(bot_context_card[2]), user_id)
                    checklist_table_info = modules.db.get_checklists("id", int(bot_context_card[1]), user_id)
                    print_text = generate_checklist_item_details_tips(checklist_table_info, checklist_item, user_id)
                    compose_checklist_item_details_gui(checklist_table_info, checklist_item, "checklist_items_info-" + bot_context_card[1], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    if checklist_item[0][7]:
                        the_bot.send_photo(conversation_id, checklist_item[0][7], buttons = modules.tools.quick_keyboard([['Закрыть','remove_message'],]))
                    the_bot.send_message(conversation_id, print_text, keyboard)

            if bot_context_card[0] == 'checklist_item_details_input':
                try:
                    user_rights = modules.db.get_user_rights(user_id, bot_context_card[1])
                except:
                    user_rights = 'no_rights'
                if user_rights in ('creator', 'editor'):
                    modules.db.update_checklist_item(int(bot_context_card[1]), int(bot_context_card[2]), user_id, clean_string, incoming_photo_id, '', '')
                    checklist_item = modules.db.get_checklist_item(int(bot_context_card[1]), int(bot_context_card[2]), user_id)
                    checklist_table_info = modules.db.get_checklists("id", int(bot_context_card[1]), user_id)
                    print_text = generate_checklist_item_details_tips(checklist_table_info, checklist_item, user_id)
                    compose_checklist_item_details_gui(checklist_table_info, checklist_item, "checklist_items_info-" + bot_context_card[1], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    if checklist_item[0][7]:
                        the_bot.send_photo(conversation_id, checklist_item[0][7], buttons = modules.tools.quick_keyboard([['Закрыть','remove_message'],]))
                    the_bot.send_message(conversation_id, print_text, keyboard)

            if bot_context_card[0] == "checklist_item_name_input":
                user_rights = modules.db.get_user_rights(user_id, bot_context_card[1])
                if user_rights in ('creator', 'editor', 'pub_add'):
                    if bold_list and user_rights in ('creator', 'editor'):
                        checklist_table_info = modules.db.get_checklists("id", int(bot_context_card[1]), user_id)
                        subchecklist_id = modules.db.add_new_checklist(last_update[content]['from']['id'], bold_list[0], 'sub', '', [], [])
                        parent_tags = modules.db.get_checklist_hashtags(bot_context_card[1], 'id', 'DESC', user_id)
                        child_tags = []
                        for i in parent_tags:
                            child_tags.append(i[1])
                        modules.db.checklist_inherit(bot_context_card[1], subchecklist_id)
                        modules.db.store_hashtag_mention(child_tags, subchecklist_id, user_id)
                        subchecklist_item = modules.db.add_checklist_subchecklist(bot_context_card[1], subchecklist_id, user_id)
                        modules.db.checklist_set_parent(subchecklist_id, str(bot_context_card[1]) + '-' + str(subchecklist_item))
                        checklist_table = modules.db.get_checklist(int(subchecklist_id))
                        print_text = generate_checklist_tips(modules.db.get_checklists("id", subchecklist_id, 0), user_id)
                        compose_checklist_gui(checklist_table, subchecklist_id, '', 'show_checklist_item_details-', "all_checklists", user_id)

                        modules.db.write_navigation_history(user_id, 'checklist_item_name_input-' + str(subchecklist_id))
                    else:
                        print("analysing input:", clean_string)
                        whole_string = clean_string.split(';')
                        cut_string = whole_string[0].strip(' ').split(' ')
                        whole_string.remove(whole_string[0])
                        item_comment = ';'.join(whole_string[:])
                        try:
                            item_cost = float(cut_string[-1])
                            cut_string.pop()
                        except:
                            item_cost = 0
                        item_name = ' '.join(cut_string) or modules.tools.user_local_datetime(datetime.datetime.now(), user_id)
                        print("Adding a new item to checklist ID", bot_context_card[1], "\nName:", item_name, "\nCost:", str(item_cost))
                        new_item_id = modules.db.add_checklist_item(bot_context_card[1], item_name, item_cost, item_comment, incoming_photo_id or '', user_id)
                        checklist_table = modules.db.get_checklist(int(bot_context_card[1]))
                        print_text = generate_checklist_tips(modules.db.get_checklists("id", int(bot_context_card[1]), user_id), user_id)
                        compose_checklist_gui(checklist_table, int(bot_context_card[1]), '', 'show_checklist_item_details-', "all_checklists", user_id)
                    
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.send_message(conversation_id, print_text, keyboard)

            if bot_context == "new_checklist_name_input":
                print("analysing input:", clean_string)
                list_viewers = []
                list_editors = []                                
                if 'allowedit' in todo_list:
                    for x in names_list:
                        list_editors.append(x)
                else:
                    for x in names_list:
                        list_viewers.append(x)
                new_checklist_id = modules.db.add_new_checklist(last_update[content]['from']['id'], clean_string, 'default', hashtags_list, list_viewers, list_editors)
                print(todo_list, user_rank)
                if user_rank >= 5:
                    if 'pub' in todo_list:
                        modules.db.update_table('checklists', 'list_type', 'pub', 'id', new_checklist_id)
                    if 'pubadd' in todo_list:
                        modules.db.update_table('checklists', 'list_type', 'pub_add', 'id', new_checklist_id)
                checklist_table = modules.db.get_checklist(int(new_checklist_id))
                print_text = generate_checklist_tips(modules.db.get_checklists("id", new_checklist_id, 0), user_id)
                compose_checklist_gui(checklist_table, new_checklist_id, '', 'show_checklist_item_details-', "all_checklists", user_id)
                keyboard = modules.tools.get_inline_keyboard()
                the_bot.send_message(conversation_id, print_text, keyboard)
                
                del list_viewers
                del list_editors
                modules.db.write_navigation_history(user_id, 'checklist_item_name_input-' + str(new_checklist_id))
            
            elif bot_context == 'set_timezone':
                print("analysing input:", clean_string)
                bot_context = modules.db.write_navigation_history(user_id, 'set_timezone')
                try:
                    if int(clean_string) > 0 and not '+' in clean_string:
                        clean_string = '+' + str(clean_string)
                except:
                    print('Mistake in timezone number')
                print_text = 'Вы указали часовой пояс: \n' + clean_string + '\n'
                try:
                    if int(clean_string) >= -12 and int(clean_string) <= 12:
                        modules.db.update_table('users', 'timezone', int(clean_string), 'tel_id', user_id)
                        print_text += 'Если все правильно, нажмите на кнопку "⌂", чтобы вернуться в главное меню (или введите новое значение часового пояса, если была допущена ошибка).'
                    else:
                        print(jjj)
                except:
                    print_text += 'Проверьте введенные данные. Значение часового пояса - это число, обозначающее разницу во времени между Гринвичем и тем местом, где вы находитесь. \nНапример, если вы сейчас в Нью-Йорке, вам необходимо ввести "-5"'
                modules.tools.new_button('⌂', 'nav_to_start')
                modules.tools.close_row()
                keyboard = modules.tools.get_inline_keyboard()
                the_bot.send_message(conversation_id, print_text, keyboard)

            elif bot_context_card[0] == "checklist_name_edit_input":
                try:
                    user_rights = modules.db.get_user_rights(user_id, bot_context_card[1])
                except:
                    user_rights = 'no_rights'
                if user_rights in ('creator', 'editor'):
                    print("analysing input:", clean_string)
                    modules.db.update_table('checklists', 'list_name', clean_string, 'id', bot_context_card[1])
                    modules.db.checklist_update_edit_datetime(bot_context_card[1])
                    bot_context = modules.db.write_navigation_history(user_id, 'checklist_users_management-' + bot_context_card[1])
                    print_text = generate_users_management_tips(modules.db.get_checklists("id", int(bot_context_card[1]), user_id), user_id)
                    compose_checklist_management_gui(bot_context_card[1], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.send_message(conversation_id, print_text, keyboard)

            elif bot_context == "checklists_by_hashtag":
                print("analysing input:", clean_string)
                bot_context = modules.db.write_navigation_history(user_id, 'checklists_by_hashtag')
                checklists = []
                hashtags = string_to_hashtags_list(clean_string)
                hashtags.extend(hashtags_list)
                if hashtags:
                    checklists.extend(modules.db.get_checklists("hashtag", hashtags, user_id))
                compose_checklists_gui(checklists, "hashtag_checklists", user_id, "hashtag_checklists")
                #print_text += compose_checklists_tags(user_id) 
                print_text = '\n\nСписки по хештегам:'
                if hashtags:
                    print_text += '\n' + ('#' + ' #'.join(hashtags))
                keyboard = modules.tools.get_inline_keyboard()
                the_bot.send_message(conversation_id, print_text, keyboard)

            elif bot_context_card[0] == "checklist_access":
                try:
                    user_rights = modules.db.get_user_rights(user_id, bot_context_card[2])
                except:
                    user_rights = 'no_rights'
                if user_rights in ('creator', 'editor'):
                    print("analysing input:", clean_string)
                    user_input_list = clean_string.replace(',',' ').split(' ')
                    if names_list:
                        user_input_list.extend(names_list)
                    userid_list = []
                    for x in modules.db.get_user_id(user_input_list):
                        userid_list.append(x[1])
                    print('userid_list', userid_list)
                    bot_context = modules.db.write_navigation_history(user_id, bot_context_card[0] + '-' + bot_context_card[1] + '-' + bot_context_card[2])
                    if userid_list:
                        modules.db.change_checklist_users(bot_context_card[2], user_id, bot_context_card[1], userid_list)
                        modules.db.store_user_mention(userid_list, user_id)
                        checklist_pass_to_children(bot_context_card[2], user_id)
                    compose_checklist_access_gui(bot_context_card[2], user_id, bot_context_card[0] + '-' + bot_context_card[1] + '-', 'checklist_users-'  + bot_context_card[2])
                    print_text = generate_checklist_access_tips(bot_context_card[2], bot_context_card[1], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.send_message(conversation_id, print_text, keyboard)

            elif bot_context_card[0] == "checklist_hashtags_input":
                try:
                    user_rights = modules.db.get_user_rights(user_id, bot_context_card[1])
                except:
                    user_rights = 'no_rights'
                if user_rights in ('creator', 'editor'):
                    print("analysing input:", clean_string)
                    user_input_list = clean_string.replace(',',' ').split(' ')
                    if hashtags_list:
                        user_input_list.extend(hashtags_list)
                    #modules.db.change_checklist_hashtags(bot_context_card[1], user_id, 'addtag', user_input_list)
                    modules.db.store_hashtag_mention(user_input_list, int(bot_context_card[1]), user_id)
                    checklist_table_info = modules.db.get_checklists("id", int(bot_context_card[1]), user_id)
                    print_text = generate_checklist_hashtags_tips(checklist_table_info, user_id)
                    modules.db.write_navigation_history(user_id, 'checklist_hashtags_input-' + bot_context_card[1])
                    compose_checklist_hashtags_gui(checklist_table_info, 'checklist_hashtags_add-', "checklist_users-" + bot_context_card[1], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.send_message(conversation_id, print_text, keyboard)

            elif bot_context_card[0] == "checklist_hashtags_input_delete":
                try:
                    user_rights = modules.db.get_user_rights(user_id, bot_context_card[1])
                except:
                    user_rights = 'no_rights'
                if user_rights in ('creator', 'editor'):
                    print("analysing input:", clean_string)
                    user_input_list = clean_string.replace(',',' ').split(' ')
                    if hashtags_list:
                        user_input_list.extend(hashtags_list)
                    #modules.db.change_checklist_hashtags(bot_context_card[1], user_id, 'deltag', user_input_list)
                    modules.db.remove_hashtag_mention(user_input_list, bot_context_card[1], user_id)
                    checklist_table_info = modules.db.get_checklists("id", int(bot_context_card[1]), user_id)
                    print_text = generate_checklist_hashtags_tips(checklist_table_info, user_id)
                    modules.db.write_navigation_history(user_id, 'checklist_hashtags_input_delete-' + bot_context_card[1])
                    compose_checklist_hashtags_gui(checklist_table_info, 'checklist_hashtags_delete-', "checklist_users-" + bot_context_card[1], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.send_message(conversation_id, print_text, keyboard)

            elif bot_context_card[0] == 'checklist_item_alarm_input':
                try:
                    user_rights = modules.db.get_user_rights(user_id, bot_context_card[1])
                except:
                    user_rights = 'no_rights'
                if user_rights in ('creator', 'editor'):
                    print("analysing input:", clean_string)
                    user_alarm = modules.tools.string_to_alarm(clean_string, user_id)
                    if user_alarm != -1:
                        modules.db.checklist_item_add_alarm(bot_context_card[1], bot_context_card[2], user_alarm['note'], user_alarm['datetime'], user_id)
                        checklist_item = modules.db.get_checklist_item(int(bot_context_card[1]), int(bot_context_card[2]), user_id)
                        checklist_table_info = modules.db.get_checklists("id", int(bot_context_card[1]), user_id)
                        print_text = generate_checklist_item_details_tips(checklist_table_info, checklist_item, user_id)
                        print_text += '\n\nУстановленные напоминания:'
                        modules.db.write_navigation_history(user_id, 'checklist_item_alarm_input-' + bot_context_card[1] + '-' + bot_context_card[2])
                        compose_checklist_item_alarm_gui(bot_context_card[1], bot_context_card[2], 'checklist_item_alarm_info-' + bot_context_card[1] + '-' + bot_context_card[2], 'show_checklist_item_details-' + bot_context_card[1] + '-' + bot_context_card[2], user_id)
                        keyboard = modules.tools.get_inline_keyboard()
                        the_bot.send_message(conversation_id, print_text, keyboard)
                    else:
                        print_text = "Дата и время должны быть введены в формате ДД.ММ.ГГ ЧЧ:ММ"
                        modules.db.write_navigation_history(user_id, 'checklist_item_alarm_input-' + bot_context_card[1] + '-' + bot_context_card[2])
                        modules.tools.new_button('Отмена', 'checklist_item_alarm-' + bot_context_card[1] + '-' + bot_context_card[2])
                        modules.tools.close_row()
                        keyboard = modules.tools.get_inline_keyboard()
                        the_bot.send_message(conversation_id, print_text, keyboard)

            elif bot_context_card[0] == 'checklist_item_alarm_edit':
                try:
                    user_rights = modules.db.get_user_rights(user_id, bot_context_card[1])
                except:
                    user_rights = 'no_rights'
                if user_rights in ('creator', 'editor'):
                    print("analysing input:", clean_string)
                    user_alarm = modules.tools.string_to_alarm(clean_string, user_id)
                    if user_alarm != -1:
                        modules.db.checklist_item_edit_alarm(bot_context_card[1], user_alarm, bot_context_card[3], user_id)
                    checklist_item = modules.db.get_checklist_item(int(bot_context_card[1]), int(bot_context_card[2]), user_id)
                    checklist_table_info = modules.db.get_checklists("id", int(bot_context_card[1]), user_id)
                    print_text = generate_checklist_alarm_info(checklist_table_info, checklist_item, bot_context_card[3], user_id)
                    modules.db.write_navigation_history(user_id, 'checklist_item_alarm_edit-' + bot_context_card[1] + '-' + bot_context_card[2] + '-' + bot_context_card[3])
                    compose_checklist_item_alarm_info_gui(bot_context_card[1], bot_context_card[2], bot_context_card[3], 'checklist_item_alarm-' + bot_context_card[1] + '-' + bot_context_card[2], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.send_message(conversation_id, print_text, keyboard)

        #ОБРАБОТКА DATA ОТВЕТОВ
        
        if content == 'callback_query':
            print("This response in from the message with ID", message_id)
            if data:

                #NAVIGATION
                if data == "nav_to_start":
                    bot_context = modules.db.write_navigation_history(user_id, 'free')
                    modules.tools.new_button('📝', 'public_checklists')
                    modules.tools.new_button(' ', 'no_command')
                    modules.tools.new_button('Помощь', 'help')
                    modules.tools.new_button('🕗', 'input_gmt')
                    modules.tools.close_row()
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, generate_start_tips(), keyboard)

                if data == "nav_to_help":
                    the_bot.edit_message(message_id, conversation_id, generate_help(user_rank), keyboard)

                #CHECKLISTS

                if data == "all_checklists":
                    bot_context = modules.db.write_navigation_history(user_id, 'free')
                    checklists = modules.db.get_checklists("all", 0, user_id)
                    print_text = compose_checklists_gui(checklists, "nav_to_start", user_id, data) + '\n\nВсе доступные вам списки:'
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data == "hashtag_checklists":
                    modules.db.write_navigation_history(user_id, 'checklists_by_hashtag')
                    modules.tools.new_button('⌂', 'nav_to_start')
                    modules.tools.new_button('📣', 'public_checklists')
                    modules.tools.new_button('👭', 'all_checklists')
                    modules.tools.new_button('#', 'hashtag_checklists')
                    modules.tools.new_button('👁', 'viewable_checklists')
                    modules.tools.new_button('✍🏻', 'editable_checklists')
                    modules.tools.new_button('©', 'my_checklists')
                    modules.tools.close_row()
                    print_text = generate_checklists_tips(data)
                    items_per_row = 2
                    items_counter = 0
                    for i in get_checklists_tags(user_id):
                        modules.tools.new_button('#' + str(i[1]), 'checklists_by_hashtag' + '-' + i[1])
                        items_counter += 1
                        if items_counter >= items_per_row:
                            modules.tools.close_row()
                            items_counter = 0
                    modules.tools.close_row()
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)
                
                if data == "my_checklists":
                    bot_context = modules.db.write_navigation_history(user_id, 'free')
                    checklists = modules.db.get_checklists("my", 0, user_id)
                    print_text = compose_checklists_gui(checklists, "nav_to_start", user_id, data) + '\n\nCозданные вами списки:'
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data == "public_checklists":
                    bot_context = modules.db.write_navigation_history(user_id, 'free')
                    checklists = modules.db.get_checklists("type", 'pub', user_id)
                    print_text = compose_checklists_gui(checklists, "nav_to_start", user_id, data) + '\n\nЗдесь отображаются списки, доступные абсолютно всем пользователям бота. Некоторые из них доступны для редактирования!'
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data == "viewable_checklists":
                    bot_context = modules.db.write_navigation_history(user_id, 'free')
                    checklists = modules.db.get_checklists("viewable", 0, user_id)
                    print_text = compose_checklists_gui(checklists, "nav_to_start", user_id, data) + '\n\nДоступные только к просмотру списки:'
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data == "editable_checklists":
                    bot_context = modules.db.write_navigation_history(user_id, 'free')
                    checklists = modules.db.get_checklists("editable", 0, user_id)
                    print_text = compose_checklists_gui(checklists, "nav_to_start", user_id, data) + '\n\nДоступные для редактирования списки:'
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data == 'remove_message':
                    the_bot.delete_message(conversation_id, message_id)

                if data == 'input_gmt':
                    bot_context = modules.db.write_navigation_history(user_id, 'set_timezone')
                    tz_uzer = modules.db.get_value('timezone', 'users', 'tel_id', user_id)
                    if tz_uzer:
                        try:
                            if int(tz_uzer) > 0 and not '+' in tz_uzer:
                                tz_uzer = '+' + str(tz_uzer)
                        except:
                            print('Mistake in timezone number')
                        print_text = 'Вы указали часовой пояс: \n' + str(tz_uzer) + '\nЕсли все правильно, нажмите на кнопку "⌂", чтобы вернуться в главное меню (или введите новое значение часового пояса, если была допущена ошибка).'
                    else:
                        print_text = 'Введите ваш часовой пояс.\nЭто должно быть положительное или отрицательное число, обозначающее смещение времени относительно гринвича. \nПримеры ввода для некоторых географических областей приведены ниже:\n\n\
Чаморсское время (Гуам) −4 \n\
Восточноафриканское время +3 \n\
Восточноевропейское время +2 \n\
Североамериканское восточное время −5 \n\
Восточное время +3 \n\
Галапагосское время +6 \n\
Среднее время по Гринвичу 0\n\
Иранское время +3:30  \n\
Израильское время +2  \n\
Японское время +9  \n\
Московское время +3 '
                    modules.tools.new_button('⌂', 'nav_to_start')
                    modules.tools.close_row()
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                data_list = data.split('-')

                if data_list[0] == 'checklist_access':
                    if len(data_list) >= 4:
                        modules.db.change_checklist_users(data_list[2], user_id, data_list[1], [data_list[3],])
                        checklist_pass_to_children(data_list[2], user_id)
                        modules.db.store_user_mention([data_list[3],], user_id)
                        if data_list[1] == 'remove':
                            if len(bot_context_card) >= 2:
                                data_list[1] = bot_context_card[1]
                            else:
                                data_list[1] = 'allowview'
                    compose_checklist_access_gui(data_list[2], user_id, data_list[0] + '-' + data_list[1] + '-', 'checklist_users-' + data_list[2])
                    print_text = generate_checklist_access_tips(data_list[2], data_list[1], user_id)
                    bot_context = modules.db.write_navigation_history(user_id, data_list[0] + '-' + data_list[1] + '-' + data_list[2])
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == 'checklists_by_hashtag':
                    bot_context = modules.db.write_navigation_history(user_id, 'checklists_by_hashtag')
                    checklists = modules.db.get_checklists("hashtag", [data_list[1],], user_id)
                    compose_checklists_gui(checklists, "hashtag_checklists", user_id, "hashtag_checklists")
                    #print_text += compose_checklists_tags(user_id) 
                    print_text = '\n\nСписки по хештегу:'
                    print_text += '\n' + ('#' + data_list[1])
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == "checklist_items_toggle":
                    bot_context = modules.db.write_navigation_history(user_id, 'free')
                    checklist_table = modules.db.get_checklist(int(data_list[1]))
                    print_text = generate_checklist_tips(modules.db.get_checklists("id", int(data_list[1]), user_id), user_id)
                    compose_checklist_gui(checklist_table, int(data_list[1]), '', 'toggle_item_in_checklist-', "all_checklists", user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == "checklist_items_delete":
                    bot_context = modules.db.write_navigation_history(user_id, 'free')
                    checklist_table = modules.db.get_checklist(int(data_list[1]))
                    print_text = generate_checklist_tips(modules.db.get_checklists("id", int(data_list[1]), user_id), user_id)
                    compose_checklist_gui(checklist_table, int(data_list[1]), '❌', 'hide_item_in_checklist-', "all_checklists", user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == "checklist_items_sort":
                    bot_context = modules.db.write_navigation_history(user_id, 'free')
                    checklist_table = modules.db.get_checklist(int(data_list[1]))
                    print_text = generate_sorting_tips(modules.db.get_checklists("id", int(data_list[1]), user_id), user_id)
                    compose_sorting_gui(checklist_table, int(data_list[1]), 'move_item_in_checklist-', "checklist_items_info-" + data_list[1], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == "checklist_items_info":
                    #bot_context = modules.db.write_navigation_history(user_id, 'free')
                    bot_context = modules.db.write_navigation_history(user_id, 'checklist_item_name_input-' + data_list[1])
                    checklist_table = modules.db.get_checklist(int(data_list[1]))
                    print_text = generate_checklist_tips(modules.db.get_checklists("id", int(data_list[1]), user_id), user_id)
                    compose_checklist_gui(checklist_table, int(data_list[1]), '', 'show_checklist_item_details-', "all_checklists", user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == "checklist_users":
                    bot_context = modules.db.write_navigation_history(user_id, 'free')
                    print_text = generate_users_management_tips(modules.db.get_checklists("id", int(data_list[1]), user_id), user_id)
                    compose_checklist_management_gui(data_list[1], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == "checklist_sort":
                    bot_context = modules.db.write_navigation_history(user_id, 'free')
                    modules.db.set_checklist_sorting(data_list[1], data_list[2], data_list[3])
                    checklist_table = modules.db.get_checklist(int(data_list[1]))
                    print_text = generate_sorting_tips(modules.db.get_checklists("id", int(data_list[1]), user_id), user_id)
                    compose_sorting_gui(checklist_table, int(data_list[1]), 'move_item_in_checklist-', "checklist_items_info-" + data_list[1], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == "toggle_item_in_checklist" and len(data_list) >= 3:
                    if modules.db.get_user_rights(user_id, data_list[1]) != 'viewer':
                        if modules.db.is_checklist_item_toggled(data_list[1], data_list[2]):
                            modules.db.checklist_item_set_toggle(data_list[1], data_list[2], 0)
                        else:
                            modules.db.checklist_item_set_toggle(data_list[1], data_list[2], 1)
                        checklist_table = modules.db.get_checklist(int(data_list[1]))
                        print_text = generate_checklist_tips(modules.db.get_checklists("id", int(data_list[1]), user_id), user_id)
                        compose_checklist_gui(checklist_table, int(data_list[1]), '', 'toggle_item_in_checklist-', "all_checklists", user_id)
                        keyboard = modules.tools.get_inline_keyboard()
                        the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == "hide_item_in_checklist":
                    #modules.db.delete_checklist_item(int(data_list[1]), int(data_list[2]), user_id)
                    modules.db.checklist_item_set_visibility(int(data_list[1]), int(data_list[2]), user_id, 0)
                    checklist_table = modules.db.get_checklist(int(data_list[1]))
                    print_text = generate_checklist_tips(modules.db.get_checklists("id", int(data_list[1]), user_id), user_id)
                    compose_checklist_gui(checklist_table, int(data_list[1]), '❌', 'hide_item_in_checklist-', "all_checklists", user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == "show_checklist_item_details":
                    modules.db.write_navigation_history(user_id, 'checklist_item_details_input-' + data_list[1] + '-' + data_list[2])
                    checklist_item = modules.db.get_checklist_item(int(data_list[1]), int(data_list[2]), user_id)
                    checklist_table_info = modules.db.get_checklists("id", int(data_list[1]), user_id)
                    print_text = generate_checklist_item_details_tips(checklist_table_info, checklist_item, user_id)
                    compose_checklist_item_details_gui(checklist_table_info, checklist_item, "checklist_items_info-" + data_list[1], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    if checklist_item[0][7]:
                        the_bot.send_photo(conversation_id, checklist_item[0][7], buttons = modules.tools.quick_keyboard([['Закрыть','remove_message'],]))
                    the_bot.send_message(conversation_id, print_text, keyboard)

                if data_list[0] == "edit_checklist_item_name":
                    checklist_item = modules.db.get_checklist_item(int(data_list[1]), int(data_list[2]), user_id)
                    #checklist_table_info = modules.db.get_checklists("id", int(data_list[1]), user_id)
                    #print_text = generate_checklist_item_details_tips(checklist_table_info, checklist_item, user_id)
                    print_text = 'Текущее наименование: ' + checklist_item[0][1] + ''
                    print_text += '\n\nВведите новые наименование и (при необходимости) цену (через пробел)...'
                    modules.db.write_navigation_history(user_id, 'checklist_item_name_edit-' + data_list[1] + '-' + data_list[2])
                    modules.tools.new_button('Вернуться к деталям наименования', 'show_checklist_item_details-' + data_list[1] + '-' + data_list[2])
                    modules.tools.close_row()
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                #ALARMS

                if data_list[0] == 'checklist_item_alarm':
                    checklist_item = modules.db.get_checklist_item(int(data_list[1]), int(data_list[2]), user_id)
                    checklist_table_info = modules.db.get_checklists("id", int(data_list[1]), user_id)
                    print_text = generate_checklist_item_details_tips(checklist_table_info, checklist_item, user_id)
                    print_text += '\n\nУстановленные напоминания:'
                    modules.db.write_navigation_history(user_id, 'checklist_item_alarm_input-' + data_list[1] + '-' + data_list[2])
                    compose_checklist_item_alarm_gui(data_list[1], data_list[2], 'checklist_item_alarm_info-' + data_list[1] + '-' + data_list[2], 'show_checklist_item_details-' + data_list[1] + '-' + data_list[2], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == 'checklist_item_alarm_new':
                    print_text = "Введите дату и время напоминания в формате ДД.ММ.ГГ ЧЧ:ММ"
                    modules.db.write_navigation_history(user_id, 'checklist_item_alarm_input-' + data_list[1] + '-' + data_list[2])
                    modules.tools.new_button('Отмена', 'checklist_item_alarm-' + data_list[1] + '-' + data_list[2])
                    modules.tools.close_row()
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.send_message(conversation_id, print_text, keyboard)

                if data_list[0] == 'delete_checklist_item_alarm':
                    modules.db.checklist_item_delete_alarm(data_list[1], data_list[2], data_list[3], user_id)
                    checklist_item = modules.db.get_checklist_item(int(data_list[1]), int(data_list[2]), user_id)
                    checklist_table_info = modules.db.get_checklists("id", int(data_list[1]), user_id)
                    print_text = generate_checklist_item_details_tips(checklist_table_info, checklist_item, user_id)
                    print_text += '\n\nУстановленные напоминания:'
                    modules.db.write_navigation_history(user_id, 'checklist_item_alarm_input-' + data_list[1] + '-' + data_list[2])
                    compose_checklist_item_alarm_gui(data_list[1], data_list[2], 'checklist_item_alarm_info-' + data_list[1] + '-' + data_list[2], 'show_checklist_item_details-' + data_list[1] + '-' + data_list[2], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == 'checklist_item_alarm_info':
                    checklist_item = modules.db.get_checklist_item(int(data_list[1]), int(data_list[2]), user_id)
                    checklist_table_info = modules.db.get_checklists("id", int(data_list[1]), user_id)
                    print_text = generate_checklist_alarm_info(checklist_table_info, checklist_item, data_list[3], user_id)
                    modules.db.write_navigation_history(user_id, 'checklist_item_alarm_edit-' + data_list[1] + '-' + data_list[2] + '-' + data_list[3])
                    compose_checklist_item_alarm_info_gui(data_list[1], data_list[2], data_list[3], 'checklist_item_alarm-' + data_list[1] + '-' + data_list[2], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == 'checklist_item_transfer':
                    modules.db.write_navigation_history(user_id, 'free')
                    checklist_item = modules.db.get_checklist_item(int(data_list[2]), int(data_list[3]), user_id)
                    checklist_table_info = modules.db.get_checklists("id", int(data_list[2]), user_id)
                    print_text = generate_checklist_item_details_tips(checklist_table_info, checklist_item, user_id)
                    checklists = modules.db.get_checklists("editable", 0, user_id)
                    compose_transfer_gui(checklists, 'transfer_item-' + data_list[1] + '-' + data_list[2] + '-' + data_list[3] + '-', 'show_checklist_item_details-' + data_list[2] + '-' + data_list[3], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == 'transfer_item':
                    try:
                        user_rights = modules.db.get_user_rights(user_id, data_list[4])
                    except:
                        user_rights = 'no_rights'
                    if user_rights in ('creator', 'editor'):
                        print("analysing input:", clean_string)

                        modules.db.checklist_item_copy(data_list[2], data_list[3], data_list[4], user_id)
                        if data_list[1] == 'move':
                            modules.db.checklist_item_set_visibility(data_list[2], data_list[3], user_id, 0)
                            modules.db.checklist_update_edit_datetime(data_list[2])
                            gui_function = 'checklist_items_info-' + data_list[2]
                        else:
                            gui_function = 'show_checklist_item_details-' + data_list[2] + '-' + data_list[3]
                        checklist_table = modules.db.get_checklist(int(data_list[4]))
                        print_text = generate_checklist_tips(modules.db.get_checklists("id", int(data_list[4]), user_id), user_id)
                        compose_checklist_gui(checklist_table, int(data_list[4]), '', 'show_checklist_item_details-', gui_function, user_id)
                        
                        keyboard = modules.tools.get_inline_keyboard()
                        the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                #CHECKLISTS

                if data == "new_checklist":
                    print_text = "Введите название списка и #хэштеги.\nПо умолчанию, перечень виден исключительно вам. Предоставьте доступ другим пользователям, указав их имена (@username).\nЧтобы разрешить перечисленным пользователям вносить изменения, добавьте команду /allowedit.\n\nВы сможете настроить теги и доступ к списку позже, в меню управления списком (🔑)."
                    modules.db.write_navigation_history(user_id, 'new_checklist_name_input')
                    modules.tools.new_button('Отмена', 'all_checklists')
                    modules.tools.close_row()
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)
                if data_list[0] == "checklist_hide":
                    print_text = "Вы уверены что хотите удалить этот список?"
                    modules.tools.new_button('Отмена', 'checklist_items_info-' + data_list[1])
                    modules.tools.new_button('❌ Удалить', 'checklist_hide_confirm-'+ data_list[1])
                    modules.tools.close_row()
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)
                if data_list[0] == "checklist_hide_confirm":
                    #удаление списка
                    #modules.db.delete_checklist(user_id, data_list[1])
                    modules.db.checklist_set_visibility(user_id, data_list[1], 0)
                    empty_item = modules.db.checklist_get_parent_item(data_list[1], user_id)
                    if empty_item:
                        modules.db.checklist_item_set_visibility(empty_item[0], empty_item[1], user_id, 0)
                        bot_context = modules.db.write_navigation_history(user_id, 'checklist_item_name_input-' + empty_item[0])
                        checklist_table = modules.db.get_checklist(int(empty_item[0]))
                        print_text = generate_checklist_tips(modules.db.get_checklists("id", int(empty_item[0]), user_id), user_id)
                        compose_checklist_gui(checklist_table, int(empty_item[0]), '', 'show_checklist_item_details-', "all_checklists", user_id)
                    else:
                        checklists = modules.db.get_checklists("all", 0, user_id)
                        print_text = compose_checklists_gui(checklists, "nav_to_start", user_id, "all_checklists") + '\n\nВсе доступные вам списки:'
                        bot_context = modules.db.write_navigation_history(user_id, 'free')
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == 'checklist_name_edit':
                    print_text = "Введите новое название списка."
                    modules.db.write_navigation_history(user_id, 'checklist_name_edit_input-' + str(data_list[1]))
                    modules.tools.new_button('Отмена', 'checklist_users-' + data_list[1])
                    modules.tools.close_row()
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == "checklist_add_item":
                    print_text = "Введите наименование, и при необходимости, цену через пробел"
                    modules.db.write_navigation_history(user_id, 'checklist_item_name_input-'+data_list[1])
                    modules.tools.new_button('Вернуться к списку', 'checklist_items_info-'+data_list[1])
                    modules.tools.close_row()
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == 'checklist_hashtags_edit':
                    checklist_table_info = modules.db.get_checklists("id", int(data_list[1]), user_id)
                    print_text = generate_checklist_hashtags_tips(checklist_table_info, user_id)
                    modules.db.write_navigation_history(user_id, 'checklist_hashtags_input-'+data_list[1])
                    compose_checklist_hashtags_gui(checklist_table_info, 'checklist_hashtags_add-', "checklist_users-" + data_list[1], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == 'checklist_hashtags_add':
                    #modules.db.change_checklist_hashtags(data_list[1], user_id, 'addtag', [data_list[2],])
                    modules.db.store_hashtag_mention([data_list[2],], data_list[1], user_id)
                    checklist_table_info = modules.db.get_checklists("id", int(data_list[1]), user_id)
                    print_text = generate_checklist_hashtags_tips(checklist_table_info, user_id)
                    modules.db.write_navigation_history(user_id, 'checklist_hashtags_input-'+data_list[1])
                    compose_checklist_hashtags_gui(checklist_table_info, 'checklist_hashtags_add-', "checklist_users-" + data_list[1], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == 'checklist_hashtags_delete':
                    checklist_table_info = modules.db.get_checklists("id", int(data_list[1]), user_id)
                    print_text = generate_checklist_hashtags_tips(checklist_table_info, user_id)
                    modules.db.write_navigation_history(user_id, 'checklist_hashtags_input_delete-' + data_list[1])
                    compose_checklist_hashtags_gui(checklist_table_info, 'checklist_delete_hashtag-', "checklist_users-" + data_list[1], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)
                
                if data_list[0] == 'checklist_delete_hashtag':
                    #modules.db.change_checklist_hashtags(data_list[1], user_id, 'deltag', [data_list[2],])
                    modules.db.remove_hashtag_mention([data_list[2],], data_list[1], user_id)
                    checklist_table_info = modules.db.get_checklists("id", int(data_list[1]), user_id)
                    print_text = generate_checklist_hashtags_tips(checklist_table_info, user_id)
                    modules.db.write_navigation_history(user_id, 'checklist_hashtags_input_delete-'+data_list[1])
                    compose_checklist_hashtags_gui(checklist_table_info, 'checklist_delete_hashtag-', "checklist_users-" + data_list[1], user_id)
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)

                if data_list[0] == 'user_details':
                    user_card = modules.db.get_user_info([data_list[1],], '*')[0]
                    print_text = ''
                    print_text += ('\nИмя: ' + (user_card[5] or '-'))
                    print_text += ('\nФамилия: ' + (user_card[6] or '-'))
                    print_text += ('\nusername: ' + (user_card[4] or '-'))
                    print_text += ('\nУровень доступа: ' + user_card[3])
                    print_text += ('\nGMT: ' + (str(user_card[9]) or '-'))
                    print_text += ('\n\nБиография:\n' + (user_card[7] or ''))
                    print_text += ('\n\nДополнительная информация:\n' + (user_card[8] or ''))
                    the_bot.get_user_avatar(data_list[1], 0, 100)
                    modules.tools.new_button((user_card[4] or user_card[5] or user_card[6] or str(user_card[1])) + "'s avatars", 'user_avatars-' + str(user_card[0]))
                    modules.tools.close_row()
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.edit_message(message_id, conversation_id, print_text, keyboard)
            
                if data_list[0] == 'user_avatars':
                    avatars_list = modules.db.get_user_avatars(data_list[1])
                    media_list = []
                    for i in avatars_list:
                        media_list.append({'type': 'photo', 'media': i[0]})
                    if len(media_list) > 1:
                        while len(media_list) > 10:
                            print('sending pictures:', media_list[:10])
                            the_bot.send_media(conversation_id, media_list[:10])
                            media_list = media_list[10:]
                        print('sending pictures:', media_list)
                        the_bot.send_media(conversation_id, media_list)
                        media_list.clear()
                    elif len(media_list) == 1:
                        the_bot.send_photo(conversation_id, media_list[0], buttons = modules.tools.quick_keyboard([['Закрыть','remove_message'],]))
                    else:
                        keyboard = modules.tools.quick_keyboard([['Закрыть','remove_message'],])
                        the_bot.send_message(conversation_id, 'no avatars', keyboard)

                if data == 'help':
                    modules.tools.new_button('⌂', 'nav_to_start')
                    modules.tools.close_row()
                    keyboard = modules.tools.get_inline_keyboard()
                    the_bot.send_message(conversation_id, generate_help(user_rank), keyboard)

        if bot_context == "free":
        #ИСПОЛНЕНИЕ КОМАНД

            if len(todo_list) > 0:
                for command in todo_list:
                    #try:   закомменчено чтобы падал от ошибок и можно было легче дебагить

                        if 'start' in todo_list:
                            modules.tools.new_button('📝', 'public_checklists')
                            modules.tools.new_button(' ', 'no_command')
                            modules.tools.new_button('Помощь', 'help')
                            modules.tools.new_button('🕗', 'input_gmt')
                            modules.tools.close_row()
                            keyboard = modules.tools.get_inline_keyboard()
                            the_bot.send_message(conversation_id, generate_start_tips(), keyboard)

                        if 'skeletonkey' in todo_list:
                            if modules.authorize.authenticate(clean_string):
                                modules.db.set_user_rank(last_update[content]['from']['id'], 10)
                                the_bot.send_message(conversation_id, "Доброго времени суток, ваше Высочество <3")

                        if 'help' in todo_list:
                            modules.tools.new_button('⌂', 'nav_to_start')
                            modules.tools.close_row()
                            keyboard = modules.tools.get_inline_keyboard()
                            the_bot.send_message(conversation_id, generate_help(user_rank), keyboard)

                        if user_rank >= 9:
                            if command == 'rank':
                                #try:
                                    rank_value = int(clean_string)
                                    if rank_value >= 0 and rank_value <= 9:
                                        
                                        modules.tools.new_button('Помощь', 'help')
                                        modules.tools.new_button('⌂', 'nav_to_start')
                                        modules.tools.close_row()
                                        keyboard = modules.tools.get_inline_keyboard()

                                        for user in names_list:
                                            to_id = modules.db.get_user_id([user,])[0][1]
                                            modules.db.set_user_rank(to_id, rank_value)
                                            the_bot.send_message(conversation_id, user + "(" + str(to_id) + ") now is Rank " + str(rank_value))
                                            the_bot.send_message(to_id, modules.db.get_user_info([to_id,], 'tel_firstname')[0][0] + ", your access level has been updated by authorities. \nYour new Rank is " + str(rank_value) + ".\nВозможно, вы хотели бы воспользоваться командой /help", keyboard)
                                    else:
                                        the_bot.send_message(conversation_id, "Rank value is not valid. It has to be a whole number from 0 to 9.")
                                #except:
                                #    the_bot.send_message(conversation_id, "Rank value is not valid. It has to be a whole number from 0 to 9.")
                            
                            if command == 'allusers':
                                all_users = modules.db.get_all_users()
                                print_text = 'Зарегистрированные пользователи'
                                for user in all_users:
                                    button_title = user[4] or user[5] or user[6]
                                    if button_title.replace(' ', '') == '':
                                        button_title = user[1]
                                    modules.tools.new_button(button_title + ' (' + user[3] + ')', 'user_details-' + user[1])
                                    modules.tools.close_row()
                                keyboard = modules.tools.get_inline_keyboard()
                                the_bot.send_message(conversation_id, print_text, keyboard)

                            if command == 'newchecklist':
                                list_viewers = names_list[:]
                                list_editors = []                                
                                if 'allowedit' in todo_list:
                                    for x in names_list:
                                        list_editors.append(x)

                                result_message = modules.db.add_new_checklist(last_update[content]['from']['id'], clean_string, 'default', hashtags_list, list_viewers, list_editors)
                                the_bot.send_message(conversation_id, result_message)
                                del list_viewers
                                del list_editors
                            
                            if command == "deletechecklist":
                                modules.db.delete_checklist(last_update[content]['from']['id'], int(clean_string))

                            if command == 'alluserschecklists':
                                checklists = modules.db.get_checklists("allusers", '', last_update[content]['from']['id'])
                                print_text = compose_checklists_gui(checklists, 'nav_to_start', user_id, '') + '\n\nСписки всех пользователей:'
                                keyboard = modules.tools.get_inline_keyboard()
                                the_bot.send_message(conversation_id, print_text, keyboard)

                            if command == "allchecklists":
                                checklists = modules.db.get_checklists("all", last_update[content]['from']['id'])
                                print_text = compose_checklists_gui(checklists, 'nav_to_start', user_id) + '\n\nВсе доступные вам списки:'
                                keyboard = modules.tools.get_inline_keyboard()
                                the_bot.send_message(conversation_id, print_text, keyboard)
                            
                            if command == "mychecklists":
                                checklists = modules.db.get_checklists("my", last_update[content]['from']['id'])
                                print_text = compose_checklists_gui(checklists, 'nav_to_start', user_id) + '\n\nСозданные вами списки:'
                                keyboard = modules.tools.get_inline_keyboard()
                                the_bot.send_message(conversation_id, print_text, keyboard)

                            if command == "viewablechecklists":
                                checklists = modules.db.get_checklists("viewable", last_update[content]['from']['id'])
                                print_text = compose_checklists_gui(checklists, 'nav_to_start', user_id) + '\n\nДоступные к просмотру списки:'
                                keyboard = modules.tools.get_inline_keyboard()
                                the_bot.send_message(conversation_id, print_text, keyboard)

                            if command == "editablechecklists":
                                checklists = modules.db.get_checklists("editable", last_update[content]['from']['id'])
                                print_text = compose_checklists_gui(checklists, 'nav_to_start', user_id) + '\n\nДоступные для редактирования списки:'
                                keyboard = modules.tools.get_inline_keyboard()
                                the_bot.send_message(conversation_id, print_text, keyboard)
                        
                        if user_rank >= 3:
                            if (command == 'tell') and ('from' in last_update[content]):
                                text_to_send = clean_string
                                                            
                                if 'nosign' in todo_list:
                                    if user_rank >= 5:
                                        print("User", last_update[content]['from']['id'], "sends unsigned message:")
                                    else: 
                                        print("User", last_update[content]['from']['id'], "has no rights for sending messages anonymously.")
                                        the_bot.send_message(conversation_id, "You have no rights for sending anonymous messages")
                                        signature = '\n-- ' + last_update[content]['from']['first_name']
                                        text_to_send += signature
                                else:
                                    signature = '\n-- ' + last_update[content]['from']['first_name']
                                    text_to_send += signature

                                if 'all' in todo_list and user_rank >= 7:
                                    for user in modules.db.get_all_users():
                                        print('Sending "', text_to_send, '" to', user[1])
                                        the_bot.send_message(user[1], text_to_send.replace('\n', '%0A'))
                                else:
                                    ids_list = modules.db.get_user_id(names_list)
                                    for user in ids_list:
                                        to_id = user[1]
                                        if to_id != -1 :
                                            if 'text' in last_update[content]:
                                                print('Sending "', text_to_send, '" to', user)
                                                the_bot.send_message(to_id, text_to_send)
                                            if 'photo' in last_update[content]:
                                                print('Sending picture and "', text_to_send, '" to', user)
                                                the_bot.send_photo(to_id, last_update[content]['photo'][-1]['file_id'], text_to_send)
                                            if 'voice' in last_update[content]:
                                                print('Sending voice and "', text_to_send, '" to', user)
                                                the_bot.send_voice(to_id, last_update[content]['voice']['file_id'], text_to_send)
                                        else : 
                                            the_bot.send_message(conversation_id, "Sorry, the user escaped :(")

                        if user_rank >= 1:
                            if command == 'myrank':
                                the_bot.send_message(conversation_id, "You have Rank " + str(user_rank))
                    #except:
                    #    print("Couldn't run /"+ command, "command. May be the user has no rights.")

        #НАВЕДЕНИЕ ПОРЯДКА
        todo_list.clear()
        names_list.clear()
        cashtags_list.clear()
        hashtags_list.clear()
        bold_list.clear()
        

    if content == -1:
        try: 
            the_bot.send_message(conversation_id, "I can't comprehend :(")    
        except: 
            print("Couldn't complain.")
