# configuration file
import os

telbot_config = {
    'bot_token': os.environ['TEL_BOT_TOKEN'],
    'db_host': 'localhost',
    'db_user': os.environ['MYSQL_USER'],
    'db_password': os.environ['MYSQL_PASSWORD'],
    'db_name': os.environ['MYSQL_DATABASE'],
    'db_charset': 'utf8mb4'
}