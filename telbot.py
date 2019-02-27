#Главный скрипт.
import config
import modules.bothandle        
import modules.comprehend
import alarms
from apscheduler.schedulers.background import BackgroundScheduler

ALARMS_CHECK_INTERVAL = 60 #second
scheduler = BackgroundScheduler()
scheduler.start()

the_bot = modules.bothandle.BotHandle(config.telbot_config['bot_token'])   
now = modules.bothandle.datetime.datetime.now()

def check_alarms():
    alarms.run_alarms_check();

def main():  
    new_offset = None
    today = now.day
    hour = now.hour

    scheduler.add_job(check_alarms, 'interval', seconds = ALARMS_CHECK_INTERVAL)

    #Бесконечный цикл
    while True:
        last_updates = the_bot.get_updates(new_offset)

        for last_update in last_updates:

            if last_update != -1 :
                
                last_update_id = last_update['update_id']
                
                print(last_update)
                #Передача апдейта модулю распознания команд
                modules.comprehend.comprehend(the_bot, last_update)

                new_offset = last_update_id + 1

if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()