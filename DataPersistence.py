import DataStorage
import json
import zipfile
import os
import time

BACKUP_OUTDATED_MINUTES = 2

class DataPersistence:

    def __init__(self, data):
        self.data = data
        if not os.path.exists(DataStorage.RECORDINGS_PATH):
            os.makedirs(DataStorage.RECORDINGS_PATH)
        if not os.path.exists(DataStorage.THUMBNAIL_PATH):
            os.makedirs(DataStorage.THUMBNAIL_PATH)

    def save_settings(self,settings):
        self.save("data/settings.json", json.dumps(settings, cls=SaveEncoder))

    def save_emails(self, emails):
        self.save("data/emails.json", json.dumps(list(emails.values()), cls=SaveEncoder))

    def save_logs(self, logs):
        self.save("data/logs.json", json.dumps(list(logs.values()), cls=SaveEncoder))

    def save(self, filename, text):
        with open(filename, 'w') as out:
            out.write(text)

    def read(self, filename):
        with open(filename, 'r') as read:
            data = read.read()
        return data

    def from_json(self, json_object):
        error_message = 'Wrong format of {}. Please delete file or add missing attributes.'
        if 'message' in json_object:
            if len(vars(DataStorage.Log())) != len(json_object):
                raise AttributeError(error_message.format('logs.json'))
            return DataStorage.Log(json_object['id'], json_object['timestamp'], json_object['message'])
        elif 'sensitivity' in json_object:
            if len(vars(DataStorage.Settings())) != len(json_object):
                raise AttributeError(error_message.format('settings.json'))
            return DataStorage.Settings(json_object['sensitivity'], json_object['brightness'], json_object['contrast'],
                                        json_object['streamaddress'], json_object['global_notify'], json_object['log_enabled'],
                                        json_object['cliplength'], json_object['max_logs'],json_object['max_storage'])
        elif 'address' in json_object:
            if len(vars(DataStorage.Mail(""))) != len(json_object):
                raise AttributeError(error_message.format('emails.json'))
            return DataStorage.Mail(json_object['address'], json_object['id'], bool(json_object['notify']))

    def load_settings(self):
        try:
            file = self.read("data/settings.json")
            return json.JSONDecoder(object_hook=self.from_json).decode(file)
        except FileNotFoundError:
            return

    def load_emails(self):
        try:
            file = self.read("data/emails.json")
            ret = json.JSONDecoder(object_hook=self.from_json).decode(file)
            ret = DataStorage.AutoIdDict(ret)
            return ret
        except FileNotFoundError:
            return

    def load_logs(self):
        try:
            file = self.read("data/logs.json")
            ret = json.JSONDecoder(object_hook=self.from_json).decode(file)
            ret = DataStorage.AutoIdDict(ret)
            return ret
        except FileNotFoundError:
            return
    @staticmethod
    def get_size_of_folder(start_path):
        total_size = 0
        for path, dirs, files in os.walk(start_path):
            for f in files:
                fp = os.path.join(path, f)
                total_size += os.path.getsize(fp)
        return total_size

    @staticmethod
    def zip_current_data():
        filename = "backup.zip"
        def zipdir(path, ziph):
            for root, dirs, files in os.walk(path):
                for file in files:
                    ziph.write(os.path.join(root, file))
        if (os.path.isfile(filename) and (((time.time() - os.path.getctime(filename)) / 60) > BACKUP_OUTDATED_MINUTES)) or \
                not os.path.isfile(filename):
            zipf = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
            zipdir('data/', zipf)
            zipf.close()
            return True
        return False


class SaveEncoder(json.JSONEncoder):
    def default(self, o):
            return o.__dict__
