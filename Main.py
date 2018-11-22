from ImageProcessing import ImageProcessing
from Webserver import Webserver

__DEBUG__ = True


class Main:

    @staticmethod
    def main():
        image_processing = ImageProcessing(__DEBUG__)
        image_processing.start()
        my_webserver = Webserver()
        my_webserver.app.run(port=8002, host='127.0.0.1', debug=False, threaded=True)
        image_processing.stop()
        image_processing.join()

if __name__ == "__main__":
    Main.main()
