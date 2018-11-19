from flask import Flask, Response, request, send_from_directory
from DataStorage import *
import json
import base64
from flask_cors import CORS

# https://github.com/desertfury/flask-opencv-streaming

class Webserver:

    ERROR = 'ERROR', 403

    def __init__(self):
        self.app = Flask(__name__, static_url_path='')
        self.app.add_url_rule('/videostream', 'video_feed', self.video_feed, methods=["GET"])
        self.app.add_url_rule('/logs/<page_no>/<batch_size>', 'get_logs', self.get_logs, methods=["GET"])
        self.app.add_url_rule('/log/<log_id>', 'delete_log', self.delete_log, methods=["DELETE"])
        self.app.add_url_rule('/mail', 'add_mail', self.add_mail, methods=["POST"])
        self.app.add_url_rule('/mails', 'get_mails', self.get_mails, methods=["GET"])
        self.app.add_url_rule('/mail/<mail_id>', 'delete_mail', self.delete_change_mail, methods=["DELETE", "PUT"])
        self.app.add_url_rule('/login', 'check_login', self.check_login, methods=["POST"])
        self.app.add_url_rule('/config', 'change_get_config', self.change_get_config, methods=["POST", "GET"])
        self.app.add_url_rule('/recording/<path:filename>', 'recording', self.get_recording, methods=["GET"])
        CORS(self.app)
        self.data = PipcoDaten.get_instance()

    def gen(self):
        old = self.data.get_image().tobytes()
        while True:
            if old != self.data.get_image().tobytes:
                old = self.data.get_image().tobytes
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + self.data.get_image().tobytes() + b'\r\n\r\n')

    def get_recording(self, filename):
        return send_from_directory("data/recordings/", filename)


    def get_mails(self):
        return json.dumps(list(self.data.get_mails().values()), cls=MessageEncoder)

    def change_get_config(self):
        try:
            if request.method == 'POST':
                sensitivity = request.values.get('sensitivity')
                streamaddress = request.values.get('streamaddress')
                brightness = request.values.get('brightness')
                contrast = request.values.get('contrast')
                return json.dumps(self.data.change_settings(sensitivity, brightness, contrast, streamaddress))
            else:
                return json.dumps(self.data.get_settings(), cls=MessageEncoder)
        except Exception:
            return Webserver.ERROR

    def delete_change_mail(self, mail_id):
        try:
            if request.method == 'DELETE':
                return Response("{\"mail_id\": \"" + self.data.remove_mail(int(mail_id)) + "\"}", status=200, mimetype='application/json')
            else:
                return Response("{\"notify\": \"" + str(self.data.toggle_mail_notify(mail_id)) + "\"}", status=200, mimetype='application/json')
        except Exception:
            return Webserver.ERROR

    def add_mail(self):
        try:
            mailaddress = request.values.get('mail')
            if mailaddress:
                ret = self.data.add_mail(mailaddress)
                if ret != -1:
                    return str(ret)
            return Webserver.ERROR
        except Exception:
            return Webserver.ERROR

    def check_login(self):
        try:
            user = json.loads(request.data)['user']
            password = json.loads(request.data)['password']
            if self.data.check_login(user, password):
                return Response("{\"status\": \"OK\"}", status=200, mimetype='application/json')
            return Webserver.ERROR
        except Exception:
            return Webserver.ERROR

    def delete_log(self, log_id):
        try:
            self.data.remove_log(int(log_id))
            return log_id
        except Exception:
            return Webserver.ERROR

    def get_logs(self,page_no, batch_size):
        return json.dumps(list(self.data.get_log_page(page_no,batch_size).values()), cls=MessageEncoder)

    def video_feed(self):
        if self.data.get_image() is not None:
            print("return")
            return Response(self.gen(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')
        return "no images available"


class MessageEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, Log):
            thumbnail = THUMBNAIL_PATH + str(o.id) + ".jpg"

            try:
                with open(thumbnail, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            except Exception:
                encoded_string = ""
            return {"id": o.id,
                    "message": o.message,
                    "timestamp": o.timestamp,
                    "thumbnail": encoded_string}
        else:
            return o.__dict__
