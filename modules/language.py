from random import randint
import modules.db

bonding_strength = 0.01

def db_init_tables():
    sql = 'CREATE TABLE IF NOT EXISTS alpha_bondings ( \
    id_bonding int(11) NOT NULL AUTO_INCREMENT, \
    id_emitter int(11) NULL, \
    id_collector int(11) NULL, \
    weight float(3), \
    PRIMARY KEY (id_bonding) \
    )'
    modules.db.mycursor.execute(sql)

    sql = 'CREATE TABLE IF NOT EXISTS alpha_data ( \
    id_data int(11) NOT NULL AUTO_INCREMENT, \
    string text NULL, \
    PRIMARY KEY (id_data) \
    )'
    modules.db.mycursor.execute(sql)
    modules.db.mymodules.db.commit()

def db_store_bonding(emitter, collector):
    id_emitter = db_get_data_id(emitter)
    id_collector = db_get_data_id(collector)
    new_bonding_strength = db_update_bonding(id_emitter, id_collector, bonding_strength)
    print('[', emitter, ']', '===' + str(new_bonding_strength) + '==>', '[', collector, ']')
    
def db_update_bonding(id_emitter, id_collector, strength):
    sql = 'SELECT id_bonding, weight FROM alpha_bondings WHERE id_emitter = %s AND id_collector = %s'
    val = (id_emitter, id_collector)
    modules.db.mycursor.execute(sql, val)
    result = modules.db.mycursor.fetchall()
    if result:
        id_bonding = result[0][0]
        weight = result[0][1]
        sql = 'UPDATE alpha_bondings SET weight = %s WHERE id_bonding = %s'
        val = (weight + bonding_strength, id_bonding)
        modules.db.mycursor.execute(sql, val)
        modules.db.mymodules.db.commit()
        return weight + bonding_strength
    else:
        sql = 'INSERT INTO alpha_bondings (id_emitter, id_collector, weight) VALUES (%s, %s, %s)'
        val = (id_emitter, id_collector, bonding_strength)
        modules.db.mycursor.execute(sql, val)
        modules.db.mymodules.db.commit()
        return bonding_strength

def db_get_data_id(string):
    sql = 'SELECT id_data FROM alpha_data WHERE string = %s'
    val = (string,)
    modules.db.mycursor.execute(sql, val)
    result = modules.db.mycursor.fetchall()
    if result:
        id_data = result[0][0]
    else:
        sql = 'INSERT INTO alpha_data (string) VALUES (%s)'
        val = (string,)
        modules.db.mycursor.execute(sql, val)
        modules.db.mymodules.db.commit()
        id_data = modules.db.mycursor.lastrowid
    return id_data

def receive_knowledge():
    knowledge = input('Waiting for input...')
    return knowledge

def analyse_text_sequence(phrase_list):
    for i in phrase_list:
        for j in range(len(i) - 1):
            db_store_bonding(i[j], i[j+1])
        db_store_bonding(i[-1], '.')

def format_text(string):
    ignore_symbols = '—©–-=+*&%$#№@~`<>,[]\{\}\n'
    phrase_separators = '\/|.;()":?!«»'
    for i in ignore_symbols:
        string = string.replace(i, '')
    for i in phrase_separators:
        string = string.replace(i, '.')
    clean_string = string.lower()

    phrase_list = clean_string.split('.')
    print('Formatted text:')
    for i in range(len(phrase_list)):
        phrase_list[i] = phrase_list[i].strip('').split(' ')
        print(' '.join(phrase_list[i]))
    return phrase_list

def synthesize_text(emitter, number_of_words):
    phrase_list = []
    string_list = []
    phrase_list.append(emitter)
    while emitter != '.':
        collector = db_get_collector(emitter)
        phrase_list.append(collector)
        emitter = collector
        number_of_words -= 1
    string_list.append(phrase_list[:])
    phrase_list.clear()
    for i in string_list:
        print(' '.join(i).replace(' .', '.\n').capitalize())
    return string_list

def db_get_collector(emitter):
    sql = 'SELECT string FROM alpha_data JOIN alpha_bondings ON alpha_data.id_data = alpha_bondings.id_collector WHERE id_emitter = (SELECT id_data FROM alpha_data WHERE string = %s)'
    val = (emitter,)
    modules.db.mycursor.execute(sql, val)
    result = modules.db.mycursor.fetchall()
    if result:
        return result[randint(0, len(result) - 1)][0]
    else:
        return '.'

def db_get_random_emitter():
    sql = 'SELECT string FROM alpha_data WHERE id_data = 900'
    modules.db.mycursor.execute(sql)
    result = modules.db.mycursor.fetchall()
    if result:
        return result[0][0]
    else:
        return '.'

def db_get_weight(string, limit, ascDesc):
    sql = 'SELECT weight FROM alpha_bondings JOIN alpha_data ON alpha_bondings.id_emitter = alpha_data.id_data WHERE string = %s ORDER BY weight {0} LIMIT %s'.format(ascDesc)
    val = (string, limit)
    modules.db.mycursor.execute(sql, val)
    result = modules.db.mycursor.fetchall()
    return result

def analyse(knowledge):
    analyse_text_sequence(format_text(knowledge))
    
def synthesize(seed):
    input_text_table = format_text(seed)
    keyword = ''
    keyweight = 0
    for i in input_text_table:
        for j in i:
            j_weight = db_get_weight(j, 1, 'DESC')
            if j_weight > keyweight:
                keyword = j
                keyweight = j_weight
    seed = db_get_collector(keyword)
    return synthesize_text(seed, len(seed) * 2)

db_init_tables()