from ImageProcessing import ImageProcessing
from Webserver import Webserver

class Main:

    @staticmethod
    def main():
        image_processing = ImageProcessing()
        image_processing.start()
        my_webserver = Webserver()
        my_webserver.app.run(port=8002, host='0.0.0.0', debug=False, threaded=True)
        image_processing.stop()
        image_processing.join()


if __name__ == "__main__":
    Main.main()
