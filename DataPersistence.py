import DataStorage
import json
import collections

class DataPersistence:

    def __init__(self, data):
        self.data = data

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
        if 'message' in json_object:
            return DataStorage.Log(json_object['id'], json_object['timestamp'], json_object['message'])
        elif 'sensitivity' in json_object:
            return DataStorage.Settings(json_object['sensitivity'], json_object['brightness'], json_object['contrast'], json_object['streamaddress'])
        elif 'address' in json_object:
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


class SaveEncoder(json.JSONEncoder):
    def default(self, o):
            return o.__dict__
