from flask import Flask, Response
from ImageProcessing import ImageProcessing
from DataStorage import PipcoDaten
import json

# https://github.com/desertfury/flask-opencv-streaming
class Main:

    __DEBUG__ = True

    def __init__(self):
        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'video', self.video_feed)
        self.image_processing = ImageProcessing(Main.__DEBUG__)
        self.data = PipcoDaten.getInstance()

    def gen(self):
        old = self.data.get_image().tobytes()
        while True:
            if old != self.data.get_image().tobytes:
                old = self.data.get_image().tobytes
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + self.data.get_image().tobytes() + b'\r\n\r\n')

    def logs(self):
        return json.dumps(self.data.m_log)

    def video_feed(self):
        if self.data.get_image() is not None:
            print("return")
            return Response(self.gen(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')
        return "no images available"


if __name__ == "__main__":
    main = Main()
    main.image_processing.start()
    main.app.run(port=8002, host='0.0.0.0', debug=False, threaded=True)
