#mysql configuration to avoid Illegal mix of collations (utf8mb4_unicode_ci,IMPLICIT) and (utf8_general_ci,COERCIBLE) for operation
#character-set-server = utf8mb4
#collation-server     = utf8mb4_unicode_ci
import config
import mysql.connector
import requests
import datetime
from time import sleep

mydb = mysql.connector.connect(
    host = config.telbot_config['db_host'],
    user = config.telbot_config['db_user'],
    password = config.telbot_config['db_password'],
    database = config.telbot_config['db_name'],
    charset = config.telbot_config['db_charset']
)

mycursor = mydb.cursor()

try:
    print(mycursor.fetchall())
    mycursor.execute("SHOW DATABASES")
    print("Existing databases:")
    
    for x in mycursor:
        print('- ', x[0])
    print("DB connection success.")
except:
    print("Can't reach SQL server")

# db initialization
# alarms table
sql = 'CREATE TABLE IF NOT EXISTS alarms ( \
    id int(11) NOT NULL AUTO_INCREMENT, \
    datetime int(11) NULL DEFAULT NULL, \
    note text NULL DEFAULT NULL, \
    done int(2) NULL DEFAULT NULL, \
    PRIMARY KEY (id) \
    )'
mycursor.execute(sql)
mydb.commit()
# bot_messageid_log table
sql = 'CREATE TABLE IF NOT EXISTS bot_messageid_log ( \
    id int(11) NOT NULL AUTO_INCREMENT, \
    id_conversation int(11) NULL DEFAULT NULL, \
    id_message int(11) NULL DEFAULT NULL, \
    PRIMARY KEY (id) \
    )'
mycursor.execute(sql)
mydb.commit()
# checklists table
sql = 'CREATE TABLE IF NOT EXISTS checklists ( \
    id int(11) NOT NULL AUTO_INCREMENT, \
    list_name TEXT NULL DEFAULT NULL, \
    list_type VARCHAR(24) NULL DEFAULT NULL, \
    parent VARCHAR(24) NULL DEFAULT NULL, \
    view_users text NULL DEFAULT NULL, \
    viewedit_users text NULL DEFAULT NULL, \
    creator_user VARCHAR(24) NULL DEFAULT NULL, \
    lastedit_time DATETIME NULL DEFAULT NULL, \
    creation_time DATETIME NULL DEFAULT NULL, \
    sort_by VARCHAR(24) NULL DEFAULT NULL, \
    sort_order VARCHAR(24) NULL DEFAULT NULL, \
    visible INT(1) NULL DEFAULT NULL, \
    PRIMARY KEY (id) \
    )'
mycursor.execute(sql)
mydb.commit() 
# hashtag_mentions table
sql = 'CREATE TABLE IF NOT EXISTS hashtag_mentions ( \
    id_mention int(11) NOT NULL AUTO_INCREMENT, \
    name_hashtag TEXT NULL DEFAULT NULL, \
    id_user INT(11) NULL DEFAULT NULL, \
    date DATETIME NULL DEFAULT NULL, \
    id_table INT(11) NULL DEFAULT NULL, \
    PRIMARY KEY (id_mention) \
    )'
mycursor.execute(sql)
mydb.commit() 
# security table
sql = 'CREATE TABLE IF NOT EXISTS security ( \
    name varchar(255) NULL DEFAULT NULL, \
    code varchar(255) NULL DEFAULT NULL \
    )'
mycursor.execute(sql)
mydb.commit() 
# user_avatars table
sql = 'CREATE TABLE IF NOT EXISTS user_avatars ( \
    id_avatar int(11) NOT NULL AUTO_INCREMENT, \
    id_file VARCHAR(256) NULL DEFAULT NULL, \
    id_user INT(11) NULL DEFAULT NULL, \
    datetime DATETIME NULL DEFAULT NULL, \
    PRIMARY KEY (id_avatar) \
    )'
mycursor.execute(sql)
mydb.commit() 
# user_mentions table
sql = 'CREATE TABLE IF NOT EXISTS user_mentions ( \
    id_mention int(11) NOT NULL AUTO_INCREMENT, \
    id_mentioned_user INT(11) NULL DEFAULT NULL, \
    id_user INT(11) NULL DEFAULT NULL, \
    date DATETIME NULL DEFAULT NULL, \
    PRIMARY KEY (id_mention) \
    )'
mycursor.execute(sql)
mydb.commit() 
# users table
sql = 'CREATE TABLE IF NOT EXISTS users ( \
    id int(11) NOT NULL AUTO_INCREMENT, \
    tel_id VARCHAR(24) NULL DEFAULT NULL, \
    password VARCHAR(255) NULL DEFAULT NULL, \
    rank VARCHAR(24) NULL DEFAULT NULL, \
    tel_username VARCHAR(255) NULL DEFAULT NULL, \
    tel_firstname VARCHAR(255) NULL DEFAULT NULL, \
    tel_lastname VARCHAR(255) NULL DEFAULT NULL, \
    tel_bio VARCHAR(255) NULL DEFAULT NULL, \
    notes VARCHAR(255) NULL DEFAULT NULL, \
    timezone INT(11) NULL DEFAULT NULL, \
    PRIMARY KEY (id) \
    )'
mycursor.execute(sql)
mydb.commit() 

def update_user_info(last_update_from):
    print('------------------------------------------------------------|', datetime.datetime.now())
    sql = "SELECT COUNT(tel_id) FROM users WHERE tel_id = %s"
    val = (str(last_update_from['id']), )
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    print("Found", myresult[0][0], "record(s) of this user.")
    from_id, from_username, from_firstname, from_lastname = '', '', '', ''
    if 'id' in last_update_from:
        from_id = str(last_update_from['id']).replace('-','Channel')
    if 'username' in last_update_from:
        from_username = last_update_from['username']
    if 'first_name' in last_update_from:
        from_firstname = last_update_from['first_name']
    if 'last_name' in last_update_from:
        from_lastname = last_update_from['last_name']
    if myresult[0][0] == 0 :
        sql = "INSERT INTO users (tel_id, rank, tel_username, tel_firstname, tel_lastname) VALUES (%s, %s, %s, %s, %s)"
        val = (from_id, 1, from_username, from_firstname, from_lastname)
        mycursor.execute(sql, val)

        mydb.commit()
        print(mycursor.rowcount, "user record(s) was added.") 
    else :

        sql = "UPDATE users SET tel_username = %s, tel_firstname = %s, tel_lastname = %s WHERE tel_id = %s"
        val = (from_username, from_firstname, from_lastname, from_id)
        mycursor.execute(sql, val)

        mydb.commit()
        print(mycursor.rowcount, "user record(s) was updated.")

def store_user_avatars(image_ids_list, user_id):
    sql = 'SELECT id FROM users WHERE tel_id = %s'
    val = (user_id,)
    mycursor.execute(sql, val)
    user_table_id = mycursor.fetchall()
    if user_table_id:
        for i in image_ids_list:
            sql = 'SELECT id_avatar FROM user_avatars WHERE id_file = %s AND id_user = %s'
            val = (i, user_table_id[0][0])
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            if mycursor.rowcount == 0:
                sql = 'INSERT INTO user_avatars (id_file, id_user, datetime) VALUES (%s, %s, %s)'
                val = (i, user_table_id[0][0], datetime.datetime.now())
                mycursor.execute(sql, val)
                mydb.commit()
                print(user_id, ':', i, 'saved')
        

def create_navigation_history(user_id):
    user_id = str(user_id).replace('-', 'Channel')
    sql = "CREATE TABLE {0} (id INT AUTO_INCREMENT PRIMARY KEY, navigation VARCHAR(255), timestamp VARCHAR(64))".format('history_user' + user_id)
    mycursor.execute(sql)
    mydb.commit()

    write_navigation_history(user_id, "free")

def navigation_history_exists(user_id):
    user_id = str(user_id).replace('-', 'Channel')
    sql = "SHOW TABLES LIKE %s"
    val = ('history_user' + str(user_id),)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()

    if mycursor.rowcount == 0:
        return 0
    else:
        return myresult

def write_navigation_history(user_id, info):
    user_id = str(user_id).replace('-', 'Channel')
    if not navigation_history_exists(user_id):
        create_navigation_history(user_id)

    sql = "SELECT COUNT(navigation) FROM {0}".format('history_user' + str(user_id))
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    if myresult[0][0] >= 10:
        sql = "DELETE FROM {0} ORDER BY id ASC LIMIT 1".format('history_user' + str(user_id))
        mycursor.execute(sql)
        mydb.commit()

    sql = "INSERT INTO {0} (navigation, timestamp) VALUES (%s, %s)".format('history_user' + str(user_id))
    val = (info, datetime.datetime.now())
    mycursor.execute(sql, val)
    mydb.commit()
    return info

def get_navigation_history(user_id, steps_back):
    user_id = str(user_id).replace('-', 'Channel')
    if not navigation_history_exists(user_id):
        create_navigation_history(user_id)

    sql = "SELECT navigation FROM {0} ORDER BY id DESC LIMIT {1}".format('history_user'+str(user_id), steps_back+1)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    if len(myresult) > steps_back:
        print(str(steps_back) + ' steps back, user with ID ' + str(user_id) + ' navigated to ' + myresult[steps_back][0])
        return myresult[steps_back][0]
    else:
        return ''

def get_user_id(usernames):
    print("Searching for ID by usernames\n", usernames, "\nin the database...")
    sql = "SELECT tel_username, tel_id FROM users WHERE tel_username IN ({0})".format(','.join(['%s'] * len(usernames)))
    val = tuple(usernames)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    if mycursor.rowcount > 0 :
        for x in myresult:
            print(x)
        return myresult
    else :
        print("...but found nothing :(")
        return []

def get_user_info(user_ids, columns):
    print("prepared user ids:", user_ids)
    if columns:
        sql = "SELECT {0} FROM users WHERE tel_id IN ({1})".format(columns, ','.join(['%s'] * len(user_ids)))
        val = tuple(user_ids)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        print(myresult)
        return myresult
    else:
        return []

def get_user_rank(user_id):
    user_id = str(user_id).replace('-', 'Channel')
    print("Looking at", user_id, "rank...")
    sql = "SELECT rank FROM users WHERE tel_id = %s"
    val = (str(user_id), )
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    if mycursor.rowcount > 0 :
        print("...", user_id, "has rank", myresult[0][0])
        return int(myresult[0][0])
    else :
        print("Couldn't find rank of", user_id, ". Returning 0.")
        return 0

def set_user_rank(user_id, user_rank):
    user_id = str(user_id).replace('-', 'Channel')
    print("Looking at", user_id, "rank...")
    sql = "SELECT rank FROM users WHERE tel_id = %s"
    val = (str(user_id), )
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    if mycursor.rowcount > 0 :
        sql = "UPDATE users SET rank = %s WHERE tel_id = %s"
        val = (str(user_rank), str(user_id))
        mycursor.execute(sql, val)
        print("...", user_id, "now has rank", user_rank)

        mydb.commit()
        print(mycursor.rowcount, "user record(s) was updated.")
        return 1
    else :
        print("Couldn't find", user_id, ". Returning 0.")
        return 0

def get_value(valuecolumn, database, keycolumn, key):
    print("Looking at", key, "in the", database, "...")

    sql = "SELECT {0} FROM {1} WHERE {2} = %s".format(valuecolumn, database, keycolumn)
    val = (key, )
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    if myresult:
        print(valuecolumn, "of", key, "is", myresult[0][0])
        return myresult[0][0]
    else:
        return []

def get_all_users():
    sql = "SELECT * FROM users"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    if mycursor.rowcount > 0 :
        print(myresult)
        return myresult
    else :
        print("found no one :(")
        return -1

def get_user_avatars(table_user_id):
    sql = 'SELECT id_file FROM user_avatars WHERE id_user = %s'
    val = (table_user_id,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    return myresult

def set_skeletonkey(skeletonkey):
    sql = "INSERT INTO security (name, code) VALUES ('skeletonkey', '" + skeletonkey + "')"
    mycursor.execute(sql)
    mydb.commit()
    print("Skeletonkey is set")

def add_checklist_item(checklist_id, item_name, item_cost, item_comment, photo_id, user_id):
    user_id = str(user_id).replace('-', 'Channel')
    sql = "SELECT * FROM checklists WHERE id = %s AND viewedit_users LIKE %s OR creator_user = %s"
    val = (checklist_id, '%{0}%'.format(user_id), user_id)
    mycursor.execute(sql,val)
    myresult = mycursor.fetchall()
    print("Alterating checklist match:\n", myresult)
    if mycursor.rowcount > 0:
        sql = "INSERT INTO {0} (item, cost, memo, checkbox, author, lastedit_time, image, visible, id_link) VALUES (%s, %s, %s, %s, %s, %s, %s, 1, -1)".format("checklist"+str(checklist_id))
        val = (item_name, item_cost, item_comment, 0, user_id, datetime.datetime.now(), photo_id)
        mycursor.execute(sql,val)
        mydb.commit()
        checklist_update_edit_datetime(checklist_id)
        return mycursor.lastrowid
    else:
        print("user has no rights to alter the checklist")
        return -1

def add_checklist_subchecklist(checklist_id, subchecklist_id, user_id):
    user_id = str(user_id).replace('-', 'Channel')
    if get_user_rights(user_id, checklist_id) in ('creator', 'editor'):
        sql = "INSERT INTO {0} (id_link, checkbox, visible) VALUES (%s, %s, 1)".format("checklist"+str(checklist_id))
        val = (subchecklist_id, 0)
        mycursor.execute(sql,val)
        last_id = mycursor.lastrowid
        mydb.commit()
        checklist_update_edit_datetime(checklist_id)
        print('subchecklist item id = ', last_id)
        return last_id
    else:
        print("user has no rights to alter the checklist")
        return -1

def checklist_set_parent(checklist_id, parent):
    sql = 'UPDATE checklists SET parent = %s WHERE id = %s'
    val = (parent, checklist_id)
    mycursor.execute(sql,val)
    mydb.commit()

def delete_checklist_item(checklist_id, item_id, user_id):
    user_id = str(user_id).replace('-', 'Channel')
    if get_user_rights(user_id, checklist_id) in ('creator', 'editor'):
        sql = "DELETE FROM {0} WHERE id = %s".format("checklist"+str(checklist_id))
        val = (str(item_id),)
        mycursor.execute(sql, val)

        mydb.commit()    
        print("запись удалена")
        checklist_update_edit_datetime(checklist_id)
        return 1
    else:
        print("user has no rights to alter the checklist")
        return 0

def checklist_item_set_visibility(checklist_id, item_id, user_id, visible):
    user_id = str(user_id).replace('-', 'Channel')
    if get_user_rights(user_id, checklist_id) in ('creator', 'editor'):
        sql = 'UPDATE {0} SET visible = %s WHERE id = %s'.format('checklist' + str(checklist_id))
        val = (visible, item_id)
        mycursor.execute(sql, val)
        checklist_update_edit_datetime(checklist_id)
        mydb.commit()    
        return 1
    else:
        print("user has no rights to alter the checklist")
        return 0

def add_new_checklist(user_id, list_name, list_type, hashtags, viewers, editors):
    user_id = str(user_id).replace('-', 'Channel')
    viewers_ids = ''
    for x in viewers:
        viewers_ids += str(get_user_id(x))+","
    editors_ids = ''
    for x in editors:
        editors_ids += str(get_user_id(x))+","
    sql = "INSERT INTO checklists (list_name, list_type, parent, view_users, viewedit_users, creator_user, lastedit_time, creation_time, visible) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1);"
    val = (list_name, list_type, '0', viewers_ids, editors_ids, user_id, datetime.datetime.now(), datetime.datetime.now())
    mycursor.execute(sql, val)

    mydb.commit()
    print(mycursor.rowcount, "list record was added.") 
    new_table_id = mycursor.lastrowid
    new_checklist_table_name = "checklist"+str(new_table_id)

    sql = "DROP TABLE IF EXISTS {0}".format(new_checklist_table_name)
    mycursor.execute(sql)

    sql = "CREATE TABLE {0} (ID INT AUTO_INCREMENT PRIMARY KEY, item text, cost INT(24), checkbox INT(1), author VARCHAR(64), lastedit_time datetime, memo TEXT, image VARCHAR(255), alarm VARCHAR(64), visible int(1), id_link int);".format(new_checklist_table_name)
    mycursor.execute(sql)

    mydb.commit()
    print(mycursor.rowcount, "new checklist table was created. ID", new_table_id) 

    return new_table_id

def delete_checklist(user_id, checklist_id):
    if get_user_rights(user_id, checklist_id) in ('creator') or get_user_rank(user_id) >= 9:
        sql = "DROP TABLE IF EXISTS {0}".format("checklist"+str(checklist_id))
        mycursor.execute(sql)    

        sql = "DELETE FROM checklists WHERE id = %s"
        val = (str(checklist_id),)
        mycursor.execute(sql, val)

        mydb.commit()    
        print("Таблица удалена")
        return 1
    else :
        print("пользователь", user_id, "не является создателем таблицы. удаление невозможно.")
        return -1
    print("у пользователя", user_id, "нет прав для удаления этого списка")
    return -1

def checklist_set_visibility(user_id, checklist_id, visible):
    if get_user_rights(user_id, checklist_id) in ('creator'):
        sql = 'UPDATE checklists SET visible = %s WHERE id = %s'
        val = (visible, checklist_id)
        mycursor.execute(sql, val)
        mydb.commit() 
        print('Checklist', checklist_id, ' visibility is now ', visible)

def get_checklists(filter, search, user_id, sort_by = 'lastedit_time'):
    #sort_by = 'lastedit_time'
    sql = "SELECT * FROM checklists WHERE (viewedit_users LIKE %s OR view_users LIKE %s OR creator_user = %s) AND visible = 1 ORDER BY {0} DESC".format(sort_by)
    val = ('%{0}%'.format(str(user_id)), '%{0}%'.format(str(user_id)), str(user_id))
    if filter == "my":
        sql = "SELECT * FROM checklists WHERE creator_user = %s AND visible = 1 ORDER BY {0} DESC".format(sort_by)
        val = (str(user_id),)
    elif filter == "viewable":
        sql = "SELECT * FROM checklists WHERE view_users LIKE %s AND visible = 1 ORDER BY {0} DESC".format(sort_by)
        val = ('%{0}%'.format(str(user_id)),)
    elif filter == "editable":
        sql = "SELECT * FROM checklists WHERE viewedit_users LIKE %s AND visible = 1 ORDER BY {0} DESC".format(sort_by)
        val = ('%{0}%'.format(str(user_id)),)        
    elif filter == "id":
        sql = "SELECT * FROM checklists WHERE id = %s"
        val = (str(search),)
    elif filter == "hashtag":
        print(search)
        #sql = "SELECT * FROM checklists WHERE (hashtags LIKE %s  AND visible = 1) AND (viewedit_users LIKE %s OR view_users LIKE %s OR creator_user = %s) ORDER BY {0} DESC".format(sort_by)
        sql = 'SELECT checklists.* FROM hashtag_mentions JOIN checklists ON checklists.id = hashtag_mentions.id_table WHERE (name_hashtag IN ({0}) AND checklists.visible = 1) AND (checklists.viewedit_users LIKE %s OR checklists.view_users LIKE %s OR checklists.creator_user = %s) GROUP BY id'.format(','.join(['%s'] * len(search)))
        val = tuple(search + ['%{0}%'.format(str(user_id)), '%{0}%'.format(str(user_id)), user_id])
    elif filter == 'allusers':
        sql = "SELECT * FROM checklists WHERE visible = 1 ORDER BY {0} DESC".format(sort_by)
        #val = ('%{0}%'.format(str(user_id)), '%{0}%'.format(str(user_id)), str(user_id))
        val = ()
    elif filter == 'type':
        sql = "SELECT * FROM checklists WHERE list_type LIKE %s AND visible = 1 ORDER BY {0} DESC".format(sort_by)
        #val = ('%{0}%'.format(str(user_id)), '%{0}%'.format(str(user_id)), str(user_id))
        val = ('%{0}%'.format(search),)

    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()

    print(myresult)

    return myresult

def get_checklist(checklist_id):
    sorting = read_from_db('sort_by,sort_order', 'checklists', 'id', [checklist_id,], '', '', 1) or [['id'], ['ASC']]
    checklist = []
    for item in read_from_db('*', 'checklist' + str(checklist_id), '', '', sorting[0][0], sorting[0][1], ''):
        if item[9] == 1:
            checklist.append(item)
    return checklist
    

def get_checklist_item(checklist_id, item_id, user_id):
    return read_from_db('*', 'checklist' + str(checklist_id), 'id', [item_id,], '', '', 1)

def update_checklist_item(checklist_id, item_id, user_id, memo, image_id, item_name, item_cost):
    print('*** Running "update_checklist_item" (checklist' + str(checklist_id) + ')...')
    if table_exists('checklist' + str(checklist_id)):
        if memo:
            sql = 'UPDATE {0} SET memo = %s WHERE id = %s'.format('checklist' + str(checklist_id))
            val = (memo, item_id)
            mycursor.execute(sql, val)
        if image_id:
            sql = 'UPDATE {0} SET image = %s WHERE id = %s'.format('checklist' + str(checklist_id))
            val = (image_id, item_id)
            mycursor.execute(sql, val)
        if item_name:
            sql = 'UPDATE {0} SET item = %s WHERE id = %s'.format('checklist' + str(checklist_id))
            val = (item_name, item_id)
            mycursor.execute(sql, val)
        if item_cost:
            sql = 'UPDATE {0} SET cost = %s WHERE id = %s'.format('checklist' + str(checklist_id))
            val = (item_cost, item_id)
            mycursor.execute(sql, val)
        mydb.commit()
        checklist_update_edit_datetime(checklist_id)
        return 'Successfull checklist item update'
    return 'SQL UPDATE ERROR: Table "checklist' + str(checklist_id) + " doesn't exist."


def set_checklist_sorting(checklist_id, sort_by, sort_order):
    sql = "UPDATE checklists SET sort_by = %s, sort_order = %s WHERE id = %s"
    val = (sort_by, sort_order, checklist_id)
    mycursor.execute(sql, val)
    mydb.commit()
    checklist_update_edit_datetime(checklist_id)
    return 1

def is_checklist_item_toggled(checklist_id, item_id):
    sql = "SELECT checkbox FROM {0} WHERE id = %s".format("checklist"+str(checklist_id))
    val = (item_id,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    if myresult:
        return myresult[0][0]
    else:
        return 0

def checklist_item_set_toggle(checklist_id, item_id, value):
    sql = "UPDATE {0} SET checkbox = %s WHERE id = %s".format("checklist"+str(checklist_id))
    val = (value, item_id)
    mycursor.execute(sql, val)
    mydb.commit()
    checklist_update_edit_datetime(checklist_id)
    return value

def get_checklist_total(checklist_id):
    print('Counting total cost for checklist' + str(checklist_id))
    sql = "SELECT cost FROM {0} WHERE visible = 1".format('checklist'+str(checklist_id))
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    total_price = 0
    total_goods = 0
    total_alerts = 0
    for x in myresult:
        if x[0] and x[0] > 0:
            total_price += x[0]
            total_goods += 1
        else:
            total_alerts += 1
    return [total_goods, total_price, total_alerts]

def change_checklist_users(checklist_id, user_id, command, update_users):
    if update_users:
        table_users = read_from_db('view_users,viewedit_users', 'checklists', 'id', [checklist_id,], '', '', 1)[0]
        view_users = table_users[0].replace(',',' ').strip().split(' ')
        viewedit_users = table_users[1].replace(',',' ').strip().split(' ')
        print(view_users, '\n', viewedit_users)
        for user in update_users:
            if command == 'allowview':
                if not user in view_users:
                    view_users.append(user)
                if user in viewedit_users:
                    viewedit_users.remove(user)
            if command == 'allowedit':
                if not user in viewedit_users:
                    viewedit_users.append(user)
                if user in view_users:
                    view_users.remove(user)
            if command == 'remove':
                if user in viewedit_users:
                    viewedit_users.remove(user)
                if user in view_users:
                    view_users.remove(user)
        sql = "UPDATE checklists SET view_users = %s, viewedit_users = %s WHERE id = %s"
        val = (','.join(view_users), ','.join(viewedit_users), checklist_id)
        mycursor.execute(sql, val)
        mydb.commit()

def change_checklist_hashtags(checklist_id, user_id, command, hashtags_list): #obsolete
    print('Received hashtags list:', hashtags_list)
    if hashtags_list:
        for i in hashtags_list:
            print(i)
            if not i.isalnum():
                hashtags_list.remove(i)
        table_hashtags = read_from_db('hashtags', 'checklists', 'id', [checklist_id,], '', '', 1)[0][0].replace(',',' ').strip().split(' ')
        for hashtag in hashtags_list:
            if command == 'addtag':
                if not hashtag in table_hashtags:
                    table_hashtags.append(hashtag)
            if command == 'deltag':
                if hashtag in table_hashtags:
                    table_hashtags.remove(hashtag)
        sql = "UPDATE checklists SET hashtags = %s WHERE id = %s"
        val = (','.join(table_hashtags), checklist_id)
        mycursor.execute(sql, val)
        mydb.commit()

def get_user_rights(user_id, checklist_id):
    user_id = str(user_id).replace('-', 'Channel')
    sql = "SELECT * FROM checklists WHERE id = %s"
    val = (checklist_id,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()[0]
    if mycursor.rowcount > 0 :
        if str(user_id) in myresult[6]:
            print('Пользователь', str(user_id), ' - автор списка.')
            return 'creator'
        elif str(user_id) in myresult[5]:
            print('Пользователь', str(user_id), ' - редактор списка.')
            return 'editor'
        elif str(user_id) in myresult[4]:
            print('Пользователь', str(user_id), ' - только просмотр.')
            return 'viewer'
        elif myresult[2] == 'pub_add':
            print('Пользователь', str(user_id), ' может добавлять наименования.')
            return 'pub_add'
        else:
            print('Пользователь', str(user_id), 'не имеет доступа к списку.')
            return 'no_rights'
    else:
            print('Пользователь', str(user_id), 'не имеет доступа к списку.')
            return 'no_rights'

def checklist_update_edit_datetime(checklist_id):
    sql = "UPDATE checklists SET lastedit_time = %s WHERE id = %s"
    val = (datetime.datetime.now(), checklist_id,)
    mycursor.execute(sql, val)
    mydb.commit()

def checklist_item_delete_alarm(checklist_id, item_id, alarm_id, user_id):
    if not get_user_rights(user_id, checklist_id) in ('viewer', 'no_rights'):
        sql = 'DELETE FROM alarms WHERE id = %s'
        val = (alarm_id,)
        mycursor.execute(sql, val)
        mydb.commit()
            
        sql = 'SELECT alarm FROM {0} WHERE id = %s'.format('checklist' + str(checklist_id))
        val = (item_id,)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        alarm_ids = str(myresult[0][0]).replace(',', ' ').strip().split(' ')
        if alarm_id in alarm_ids:
            alarm_ids.remove(alarm_id)

        sql = 'UPDATE {0} SET alarm = %s WHERE id = %s'.format('checklist' + str(checklist_id))
        val = (','.join(alarm_ids), item_id)
        mycursor.execute(sql, val)
        mydb.commit()

        print ('alert deletion complete')
    else:
        print('User has no rights to delete alarms in this checklist')

def checklist_item_add_alarm(checklist_id, item_id, note, datetime, user_id):
    if not get_user_rights(user_id, checklist_id) in ('viewer', 'no_rights'):
        sql = 'INSERT INTO alarms (note, datetime, done) VALUES (%s, %s, 0)'
        val = (note, datetime)
        mycursor.execute(sql, val)
        mydb.commit()
        sql = 'SELECT alarm FROM {0} WHERE id = %s'.format('checklist' + str(checklist_id))
        val = (item_id,)
        mycursor.execute(sql, val)
        alarm_ids = str(mycursor.fetchall()[0][0]).replace(',', ' ').strip().split(' ')
        for alarm_id in alarm_ids:
            try:
                int(alarm_id)
            except:
                alarm_ids.remove(alarm_id)
        alarm_ids.append(str(mycursor.lastrowid))
        sql = 'UPDATE {0} SET alarm = %s WHERE id = %s'.format('checklist' + str(checklist_id))
        val = (' '.join(alarm_ids).strip().replace(' ', ','), item_id)
        new_alarm_id = mycursor.lastrowid
        mycursor.execute(sql, val)
        mydb.commit()
        return new_alarm_id
    else:
        print('User has no right to add alarms')
        return -1

def checklist_item_get_alarm(checklist_id, item_id, user_id):
    if not get_user_rights(user_id, checklist_id) in ('viewer', 'no_rights'):
        sql = 'SELECT alarm FROM {0} WHERE id = %s'.format('checklist' + str(checklist_id))
        val = (item_id,)
        mycursor.execute(sql, val)
        alarms = []
        for alarm_id in str(mycursor.fetchall()[0][0]).replace(',', ' ').strip().split(' '):
            try:
                int(alarm_id)
                alarms.append(alarm_id)
            except:
                print(alarm_id, 'is not valid ID')
        if alarms:
            sql = 'SELECT * FROM alarms WHERE id IN {0}'.format('(' + ','.join(alarms) + ')')
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            print('Item alarms:')
            for alarm in myresult:
                print(alarm)
            return myresult
        return []
    return []

def checklist_item_edit_alarm(checklist_id, user_alarm, alarm_id, user_id):
    if not get_user_rights(user_id, checklist_id) in ('viewer', 'no_rights'):
        sql = 'UPDATE alarms SET datetime = %s, note = %s, done = 0 WHERE id = %s'
        val = (user_alarm['datetime'], user_alarm['note'], alarm_id)
        mycursor.execute(sql, val)
        mydb.commit()

def checklist_item_copy(source_checklist_id, source_item_id, destination_checklist_id, user_id):
    sql = 'INSERT INTO {0} (item, cost, checkbox, author, lastedit_time, memo, image, alarm, visible, id_link) ( SELECT * FROM (SELECT item, cost, checkbox, author, lastedit_time, memo, image, alarm, visible, id_link FROM {1} WHERE id = %s) t1)'.format('checklist' + str(destination_checklist_id), 'checklist' + str(source_checklist_id))
    val = (source_item_id,) 
    mycursor.execute(sql, val)
    mydb.commit()
    checklist_update_edit_datetime(destination_checklist_id)

#new wave of organizing
def store_user_mention(mentions_list, user_id):
    #mentions_list, user_id = telegram ids
    #for i in mentions_list:
    #    sql = 'INSERT INTO user_mentions (id_mentioned_user, id_user, date) SELECT ( SELECT id FROM users WHERE tel_id = %s), (SELECT id FROM users WHERE tel_id = %s), %s'
    sql = 'SELECT id FROM users WHERE tel_id = %s'
    mycursor.execute(sql, (user_id,))
    user_table_id = mycursor.fetchall()[0][0]
    sql = 'INSERT INTO user_mentions (id_mentioned_user, id_user, date) SELECT id, %s, %s FROM users WHERE tel_id IN ({0})'.format(','.join(['%s'] * len(mentions_list)))
    val = tuple([user_table_id, datetime.datetime.now()] + mentions_list)
    mycursor.execute(sql, val)
    mydb.commit()

def get_chart(table_name, column, order_by, asc_desc):
    sql = 'SELECT {0}, count(*) as count FROM {1} GROUP BY {0} ORDER BY {2} {3}'.format(column, table_name, order_by, asc_desc)
    mycursor.execute(sql)
    return mycursor.fetchall()

def get_user_mentions_chart(order_by, asc_desc, user_id):
    sql = 'SELECT users.*, count(*) as count FROM user_mentions JOIN users ON user_mentions.id_mentioned_user = users.id WHERE id_user = (SELECT id FROM users WHERE tel_id = %s) GROUP BY tel_id ORDER BY {0} {1}'.format(order_by, asc_desc)
    mycursor.execute(sql, (user_id,))
    return mycursor.fetchall()

def store_hashtag_mention(mentions_list, table_id, user_id):
    for i in mentions_list:
        sql = 'INSERT INTO hashtag_mentions (name_hashtag, id_table, id_user, date) VALUES (%s, %s, (SELECT id FROM users WHERE tel_id = %s), %s)'
        mycursor.execute(sql, (i, int(table_id), int(user_id), datetime.datetime.now()))
    mydb.commit()

def remove_hashtag_mention(mentions_list, table_id, user_id):
    sql = 'DELETE FROM hashtag_mentions WHERE name_hashtag IN ({0}) AND id_table = %s'.format(','.join(['%s'] * len(mentions_list)))
    val = tuple(mentions_list + [table_id])
    mycursor.execute(sql, val)
    mydb.commit()

def get_hashtag_mentions_chart(order_by, asc_desc, user_id):
    sql = 'SELECT *, count(*) as count FROM hashtag_mentions JOIN checklists ON hashtag_mentions.id_table = checklists.id WHERE (checklists.viewedit_users LIKE %s OR checklists.view_users LIKE %s OR checklists.creator_user = %s OR checklists.list_type = "pub") AND visible = 1 GROUP BY name_hashtag ORDER BY {0} {1} LIMIT 20'.format(order_by, asc_desc)
    mycursor.execute(sql, ('%{0}%'.format(str(user_id)), '%{0}%'.format(str(user_id)), str(user_id)))
    result = mycursor.fetchall()
    print(result)
    return result

def get_checklist_hashtags(checklist_id, order_by, asc_desc, user_id):
    sql = 'SELECT *, count(*) as count FROM hashtag_mentions JOIN checklists ON hashtag_mentions.id_table = checklists.id WHERE id_user = (SELECT id FROM users WHERE tel_id = %s) AND id_table = %s AND visible = 1 GROUP BY name_hashtag ORDER BY {0} {1}  LIMIT 20'.format(order_by, asc_desc)
    mycursor.execute(sql, (user_id, checklist_id))
    return mycursor.fetchall()

def checklist_inherit(parent_id, child_id):
    sql = 'update checklists set view_users = ( SELECT * FROM ( SELECT view_users FROM checklists WHERE id = {0} ) t1), viewedit_users = ( SELECT * FROM ( SELECT viewedit_users FROM checklists WHERE id = {0} ) t2) WHERE id = {1}'.format(parent_id, child_id)
    mycursor.execute(sql)
    mydb.commit()

def checklist_get_parent_item(checklist_id, user_id):
    sql = 'SELECT parent FROM checklists WHERE id = %s'
    val = (checklist_id,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()[0][0]
    print('parent is', myresult)
    if myresult != '0':
        return myresult.split('-')
    else:
        return []

def get_old_message_id(chat_id):
    sql = 'SELECT * FROM bot_messageid_log WHERE id_conversation = %s'
    val = (chat_id,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    return myresult

def put_message_to_old(chat_id, message_id):
    sql = 'SELECT * FROM bot_messageid_log WHERE id_conversation = %s'
    val = (chat_id,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    if myresult:
        sql = 'UPDATE bot_messageid_log SET id_message = %s WHERE id_conversation = %s'
        val = (message_id, chat_id)
        mycursor.execute(sql, val)
        mydb.commit()
    else:
        sql = 'INSERT INTO bot_messageid_log (id_conversation, id_message) VALUES (%s, %s)'
        val = (chat_id, message_id)
        mycursor.execute(sql, val)
        mydb.commit()

#database request parsers and misc functions
def parse_columns(string):
    columns = []
    for piece in string.replace(' ', '').split(','):
        if piece.replace('_', '').replace('-', '').isalnum() or piece == '*':
            columns.append(piece)
    if columns == []:
        print('ERROR: "Columns to read" parameter was completely invalid.')
    else:
        print('Valid columns to read:\n' + ', '.join(columns) + ';')
    return ','.join(columns)

def parse_in_values(values):
    clean_values = []
    if not isinstance(values, list):
        values = []
    for i in values:
        if not isinstance(i, int):
            clean_values.append('"' + i + '"')
        else:
            clean_values.append(i)
    if clean_values == []:
        print('Warning: There are no "IN" values.')
        return ''
    else:
        print('Values to check in:\n' + ', '.join(str (value) for value in clean_values) + ';')
        return '(' + ','.join(str (value) for value in clean_values) + ')'

def read_from_db(colsRead, table, colKey, values, colSort, ascDesc, number):
    print('*** Running "read_from_db" (' + table + ')...')
    colsRead = parse_columns(colsRead) #{0}
    if not (table or '').replace('_', '').replace('-', '').isalnum(): #{1}
        table = ''
        print('ERROR: "Table" parameter is invalid.')
    if not (colKey or '').replace('_', '').replace('-', '').isalnum(): #{3}
        WhereFlag = ''
        InFlag = ''
        colKey = ''
        print('Warning: "Column key" parameter is invalid and will be ommited.')
    else:
        WhereFlag = 'WHERE' #{2}
        InFlag = 'IN' #{4}
    values = parse_in_values(values) #{5}
    if not (colSort or '').replace('_', '').replace('-', '').isalnum(): #{7}
        colSort = ''
        OrderByFlag = ''
        print('Warning: "Column to sort by" parameter is invalid and will be ommited.')
    else:
        OrderByFlag = 'ORDER BY' #{6}
    if (ascDesc or '').lower() != 'asc' and (ascDesc or '').lower() != 'desc' and OrderByFlag:
        ascDesc = '' #{8}
        print('Warning: ASC/DESC key was invalid or sorting was ommited. Removed as unnecessary.')
    if not isinstance(number, int): #{10}
        LimitFlag = ''
        number = ''
        print('Warning: LIMIT meaning is invalid and will be ommited.')
    else:
        LimitFlag = 'LIMIT' #{9}
    if colsRead and table:
        try:
            sql = ' '.join("SELECT {0} FROM {1} {2} {3} {4} {5} {6} {7} {8} {9} {10}".format(colsRead, table, WhereFlag, colKey, InFlag, values, OrderByFlag, colSort, ascDesc, LimitFlag, number).split())
            return execute_db_request(sql, '')
        except:
            print('DB REQUEST ERROR: There is a mistake somewhere in SQL injections')
            return [[],]
    else:
        print('DB REQUEST ERROR: One or more arguments are invalid.')
        return [[],]

def execute_db_request(sql, val):
    print('Proceeding a database request:\n"' + sql + '"')
    if val != '':
        print('Injecting values:\n', ', '.join(val))
        mycursor.execute(sql, val)
    else:
        mycursor.execute(sql)
    myresult = mycursor.fetchall()
    print('Database response:\n+------------------------+')
    for i in myresult:
        print(i)
    print('+------------------------+')
    return myresult

def table_exists(table):
    sql = "SHOW TABLES LIKE %s"
    val = (table,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    if mycursor.rowcount > 0:
        print('Running "if_table_exists"... Table "' + table + '" is found.')
        return True
    else:
        print('Running "if_table_exists"... Table "' + table + '" DOES NOT exist.')
        return False

def update_table(table, colSet, valueSet, colKey, valueKey):
    sql = 'UPDATE {0} SET {1} = %s WHERE {2} = %s'.format(table, colSet, colKey)
    val = (valueSet, valueKey)
    mycursor.execute(sql, val)
    mydb.commit()
    print('Table', table, 'has been updated')
    return mycursor