from flask import Flask, Response, request, jsonify, abort
from DataStorage import PipcoDaten

# https://github.com/desertfury/flask-opencv-streaming


class Webserver:

    ERROR = 'something went wrong.', 403

    def __init__(self):
        self.app = Flask(__name__)
        self.app.add_url_rule('/videostream', 'video_feed', self.video_feed, methods=["GET"])
        self.app.add_url_rule('/logs/<page_no>/<batch_size>', 'get_logs', self.get_logs, methods=["GET"])
        self.app.add_url_rule('/log/<log_id>', 'delete_log', self.delete_log, methods=["DELETE"])
        self.app.add_url_rule('/mail', 'add_mail', self.add_mail, methods=["POST"])
        self.app.add_url_rule('/mails', 'get_mails', self.get_mails, methods=["GET"])
        self.app.add_url_rule('/mail/<mail_id>', 'delete_mail', self.delete_mail, methods=["DELETE"])
        self.app.add_url_rule('/login', 'check_login', self.check_login, methods=["POST"])

        self.data = PipcoDaten.getInstance()

    def gen(self):
        old = self.data.get_image().tobytes()
        while True:
            if old != self.data.get_image().tobytes:
                old = self.data.get_image().tobytes
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + self.data.get_image().tobytes() + b'\r\n\r\n')

    def get_mails(self):
        return jsonify(self.data.getMails())

    def delete_mail(self, mail_id):
        try:
            self.data.removeMail(int(mail_id))
            return "success"
        except Exception:
            return Webserver.ERROR

    def add_mail(self):
        self.data.addLog()
        try:
            mailaddress = request.values.get('mail')
            if mailaddress:
                if self.data.addMail(mailaddress):
                    return "success"
            return Webserver.ERROR
        except Exception:
            return Webserver.ERROR

    def check_login(self):
        try:
            user = request.values.get('user')
            password = request.values.get('password')
            if self.data.check_login(user, password):
                return "success"
            return Webserver.ERROR
        except Exception:
            return Webserver.ERROR

    def delete_log(self, log_id):
        try:
            self.data.removeLog(int(log_id))
            return "success"
        except Exception:
            return Webserver.ERROR

    def get_logs(self,page_no, batch_size):
        return jsonify(self.data.get_log_page(page_no,batch_size))

    def video_feed(self):
        if self.data.get_image() is not None:
            print("return")
            return Response(self.gen(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')
        return "no images available"
