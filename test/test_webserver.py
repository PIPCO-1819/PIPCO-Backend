import unittest
import Webserver
from DataStorage import *

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestWebserver(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        TestWebserver.server = Webserver.Webserver()
        TestWebserver.app = TestWebserver.server.app.test_client()
        TestWebserver.app.testing = True

    def setUp(self):
        TestWebserver.server.data._PipcoDaten__m_log.clear()
        TestWebserver.server.data._PipcoDaten__m_emails.clear()
        for i in range(4):
            TestWebserver.server.data._PipcoDaten__m_log.append(Log())
        for i in range(4):
            TestWebserver.server.data._PipcoDaten__m_emails.append(Mail(str(i)+"@test.de"))


    def test_login_wrong(self):
        result = TestWebserver.app.post("/login", json={"user": "user", "password": "bla"})
        self.assertEqual(result.status_code, 403)

    def test_login_wrong_empty(self):
        result = TestWebserver.app.post("/login", json={})
        self.assertEqual(result.status_code, 403)

    def test_login_correct(self):
        result = TestWebserver.app.post("/login", json={"user": "user", "password": "geheim"})
        self.assertEqual(result.status_code, 200)

    def test_videostream_available(self):
        result = TestWebserver.app.get("/videostream")
        self.assertEqual(result.status_code, 200)

    def test_logs_length(self):
        result = TestWebserver.app.get("/logs/0/5")
        self.assertEqual(len(result.get_json()), 4)

    def test_logs_take_batch(self):
        result = TestWebserver.app.get("/logs/1/2")
        self.assertEqual(result.get_json()[0]["id"], 1)
        self.assertEqual(result.get_json()[1]["id"], 0)

    def test_logs_take_not_existing_batch(self):
        result = TestWebserver.app.get("/logs/2/2")
        self.assertEqual(len(result.get_json()), 0)

    def test_log_delete_successful(self):
        result = TestWebserver.app.delete("/log/2")
        self.assertEqual(result.get_json()["log_id"], 2)

    def test_log_delete_not_existing(self):
        result = TestWebserver.app.delete("/log/4")
        self.assertEqual(result.status_code, 403)

    def test_mail_add_successful(self):
        result = TestWebserver.app.post("/mail", json={"mail": "bla@bla"})
        self.assertEqual(result.get_json()["mail_id"], 4)

    def test_mail_add_already_existing(self):
        TestWebserver.app.post("/mail", json={"mail": "bla@bla"})
        result = TestWebserver.app.post("/mail", json={"mail": "bla@bla"})
        self.assertEqual(result.status_code, 403)

    def test_mail_delete_successful(self):
        result = TestWebserver.app.delete("/mail/2")
        self.assertEqual(result.get_json()["mail_id"], 2)

    def test_mail_delete_not_existing(self):
        result = TestWebserver.app.delete("/mail/4")
        self.assertEqual(result.status_code, 403)

    def test_mail_toggle_notify(self):
        result = TestWebserver.app.put("/mail/2")
        self.assertEqual(result.get_json()["notify"], False)

    def test_mails_length(self):
        result = TestWebserver.app.get("/mails")
        self.assertEqual(len(result.get_json()), 4)

    def test_change_config_all(self):
        result = TestWebserver.app.post("/config", json={"sensitivity": 0.5, "streamaddress": "blablubb", "brightness": 0.0, "contrast": 0.5, "global_notify": True, "log_enabled": True, "cliplength": 30, "max_logs": 5, "max_storage": 340})
        self.assertEqual(len(result.get_json()), 9)

    def test_change_config_specific(self):
        result = TestWebserver.app.post("/config", json={"sensitivity": 0.5, "streamaddress": "blablubb", "brightness": 0.0, "contrast": 0.5})
        self.assertEqual(len(result.get_json()), 4)

    def test_get_recording_successful(self):
        result = TestWebserver.app.get("/recording/test.mp4")
        self.assertEqual(int(result.headers["Content-Length"]), 2107114)

    def test_get_recording_not_existing(self):
        result = TestWebserver.app.get("/recording/bla.mp4")
        self.assertEqual(result.status_code, 404)

    def test_get_backup_successful(self):
        result = TestWebserver.app.get("/backup")
        self.assertEqual(result.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
  unittest.main()