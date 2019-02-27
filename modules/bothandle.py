import requests  
import datetime
import urllib.request
import random
import json
import pathlib
import modules.db

class BotHandle:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
        self.file_api_url = "https://api.telegram.org/file/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=15):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def download_file(self, file, ext, user):
        print("Attempting to download file from", self.file_api_url + file)
        if 'avatars' in user.split('/'):
            print('File is avatar (', user, ')')
            dir_path = './media/' + "/".join(user.split('/')[0:2])
            pathlib.Path(dir_path + '/').mkdir(parents=True, exist_ok=True)
            print('Save to ' + './media/' + user + ext)
            urllib.request.urlretrieve(self.file_api_url + file, './media/' + user + ext)
        else:
            dir_path = './media/' + user.split('/')[0]
            pathlib.Path(dir_path + '/').mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(self.file_api_url + file, dir_path + '/' + str(random.randint(100000000000, 999999999999)) + ext)

    def send_message(self, chat_id, text, buttons = '{}'):
        #{"inline_keyboard": [[{"text": "TEST", "callback_data": "/TEST"}, {"text": "TEST2", "callback_data": "/TEST2"}]]}
        params = {'chat_id': chat_id, 'text': text, 'reply_markup': buttons}
        method = 'sendMessage'  
        resp = requests.post(self.api_url + method, params)
        print('------------------------------------------------------------|', datetime.datetime.now())
        result = resp.json()
        print('sendMessage response:\n',result)
        if buttons != '{}':
            old_message = modules.db.get_old_message_id(chat_id)
            if old_message:
                self.delete_message(old_message[0][1], old_message[0][2])
            modules.db.put_message_to_old(result['result']['chat']['id'], result['result']['message_id'])
        return resp
    
    def edit_message(self, message_id, chat_id, text, buttons = '{}'):
        params = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'reply_markup': buttons}
        method = 'editMessageText'  
        print('------------------------------------------------------------|', datetime.datetime.now())
        resp = requests.post(self.api_url + method, params)
        print(resp.text)
        result = resp.json()
        print(result)
        #old_message = modules.db.get_old_message_id(chat_id)
        #if old_message:
        #    self.delete_message(old_message[0][1], old_message[0][2])
        return resp

    def delete_message(self, chat_id, message_id):
        params = {'chat_id': chat_id, 'message_id': message_id}
        method = 'deleteMessage'
        resp = requests.post(self.api_url + method, params)
        print(resp)
        return resp

    def send_photo(self, chat_id, file_id, caption = '', buttons = '{}'):
        params = {'chat_id': chat_id, 'photo': file_id, 'caption': caption, 'reply_markup': buttons}
        method = 'sendPhoto'  
        resp = requests.post(self.api_url + method, params)
        print(resp)
        result = resp.json()
        #old_message = modules.db.get_old_message_id(chat_id)
        #if old_message:
        #    self.delete_message(old_message[0][1], old_message[0][2])
        return resp

    def send_media(self, chat_id, media, caption = '', buttons = '{}'):
        params = {'chat_id': chat_id, 'media': json.dumps(media)}
        method = 'sendMediaGroup'
        resp = requests.post(self.api_url + method, params)
        result = resp.json()
        print(result)

    def send_voice(self, chat_id, file_id, caption):
        params = {'chat_id': chat_id, 'voice': file_id, 'caption': caption}
        method = 'sendVoice'  
        resp = requests.post(self.api_url + method, params)
        print(resp)
        return resp

    def download_photo(self, file_id, user):
        params = {'file_id': file_id}
        method = 'getFile'
        resp = requests.post(self.api_url + method, params)
        result_json = resp.json()['result']
        self.download_file(result_json['file_path'], '.jpg', user)

    def download_voice(self, file_id, user):
        params = {'file_id': file_id}
        method = 'getFile'
        resp = requests.post(self.api_url + method, params)
        result_json = resp.json()['result']
        self.download_file(result_json['file_path'], '.oga', user)

    def download_animation(self, file_id, user):
        params = {'file_id': file_id}
        method = 'getFile'
        resp = requests.post(self.api_url + method, params)
        result_json = resp.json()['result']
        self.download_file(result_json['file_path'], '.mp4', user)

    def download_video(self, file_id, user):
        params = {'file_id': file_id}
        method = 'getFile'
        resp = requests.post(self.api_url + method, params)
        result_json = resp.json()['result']
        self.download_file(result_json['file_path'], '.mp4', user)

    def download_music(self, file_id, user):
        params = {'file_id': file_id}
        method = 'getFile'
        resp = requests.post(self.api_url + method, params)
        result_json = resp.json()['result']
        self.download_file(result_json['file_path'], '.mp3', user)

    def get_user_avatar(self, user_id, offset, limit):
        params = {'user_id': user_id, 'offset': offset, 'limit': limit}
        method = 'getUserProfilePhotos'
        resp = requests.post(self.api_url + method, params)
        result_json = resp.json()['result']
        #print(result_json)
        #for i in result_json['photos']:
        #    path_to_file = './media/' + user + '/avatars/' + i[-1]['file_id'] + '.jpg'
        #    if not pathlib.Path(path_to_file).is_file():
        #        self.download_photo(i[-1]['file_id'], user + '/avatars/' + i[-1]['file_id'])
        print(result_json)
        avatars_list = []
        for i in result_json['photos']:
            image_id = i[-1]['file_id']
            avatars_list.append(image_id)
        modules.db.store_user_avatars(avatars_list, user_id)
        