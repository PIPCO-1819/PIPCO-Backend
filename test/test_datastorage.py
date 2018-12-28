import unittest
from DataStorage import *

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestDataStorage(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

    def setUp(self):
        self.data = PipcoDaten.get_instance()
        self.data._PipcoDaten__m_settings = Settings(max_logs=5)
        self.data._PipcoDaten__m_log.clear()
        self.data._PipcoDaten__m_emails.clear()
        for i in range(4):
            self.data._PipcoDaten__m_log.append(Log())
        for i in range(4):
            self.data._PipcoDaten__m_emails.append(Mail(str(i) + "@test.de"))

    def test_toggle_mail(self):
        self.data.toggle_mail_notify(0)
        self.assertEqual(self.data._PipcoDaten__m_emails[0].notify, False)

    def test_toggle_mail_index_oor(self):
        with self.assertRaises(KeyError):
            self.data.toggle_mail_notify(4)

    def test_add_email(self):
        self.data.add_mail("bla@bla")
        self.assertEqual(self.data._PipcoDaten__m_emails[4].address, "bla@bla")

    def test_add_same_email_twice(self):
        self.data.add_mail("bla@bla")
        self.assertEqual(self.data.add_mail("bla@bla"), -1)

    def test_remove_mail(self):
        self.data.remove_mail(0)
        with self.assertRaises(KeyError):
            mail = self.data._PipcoDaten__m_emails[0]

    def test_remove_not_existing_mail(self):
        with self.assertRaises(KeyError):
            self.data.remove_mail(4)

    def test_get_mails(self):
        mails = self.data.get_mails()
        self.assertEqual(len(mails), 4)

    def test_copy_of_mails(self):
        mails = self.data.get_mails()
        mails[0].address = "test"
        self.assertNotEqual(self.data.get_mails()[0].address, mails[0].address)

    def test_get_settings(self):
        self.data._PipcoDaten__m_settings.brightness = 0.83
        self.assertEqual(self.data.get_settings().brightness, 0.83)

    def test_copy_of_settings(self):
        self.data._PipcoDaten__m_settings.contrast = 0.1
        settings = self.data.get_settings()
        settings.contrast = 0.2
        self.assertNotEqual(self.data.get_settings().contrast, settings.contrast)

    def test_change_settings(self):
        self.data.change_settings(sensitivity=0.123, brightness=0.123, contrast=0.123,
                                  streamaddress="test_change_settings", global_notify=False,
                                  log_enabled=False, cliplength=123, max_logs=123, max_storage=123 )
        self.assertEqual(self.data.get_settings().sensitivity, 0.123)
        self.assertEqual(self.data.get_settings().brightness, 0.123)
        self.assertEqual(self.data.get_settings().contrast, 0.123)
        self.assertEqual(self.data.get_settings().streamaddress, "test_change_settings")
        self.assertEqual(self.data.get_settings().global_notify, False)
        self.assertEqual(self.data.get_settings().log_enabled, False)
        self.assertEqual(self.data.get_settings().cliplength, 123)
        self.assertEqual(self.data.get_settings().max_logs, 123)
        self.assertEqual(self.data.get_settings().max_storage, 123)

    def test_get_log_page(self):
        first_page = self.data.get_log_page(0,2)
        second_page = self.data.get_log_page(1,2)
        self.assertEqual(first_page[3].id, 3)
        self.assertEqual(first_page[2].id, 2)
        self.assertEqual(second_page[1].id, 1)
        self.assertEqual(second_page[0].id, 0)

    def test_get_log_page_not_existing(self):
        self.assertEqual(len(self.data.get_log_page(3,2)), 0)

    def test_get_free_index(self):
        self.data.get_free_index()
        self.assertEqual(self.data.get_free_index(), 4)

    def test_add_log(self):
        self.data.add_log()
        self.assertEqual(len(self.data._PipcoDaten__m_log), 5)

    def test_add_log_exceed_limit(self):
        self.data.add_log()
        self.data.add_log()
        self.assertEqual(len(self.data._PipcoDaten__m_log), 5)
        self.assertIsNone(self.data._PipcoDaten__m_log.get(0))

    def test_check_login_correct(self):
        self.assertTrue(self.data.check_login("user", "geheim"))

    def test_check_login_wrong(self):
        self.assertFalse(self.data.check_login("user", "asd"))

    def test_remove_log(self):
        self.assertEqual(self.data.remove_log(0), 0)
        self.assertIsNone(self.data.get_log_page(0,5).get(0))

    def test_remove_log_not_existing(self):
        with self.assertRaises(KeyError):
            self.data.remove_log(4)


    @classmethod
    def tearDownClass(self):
        pass


if __name__ == '__main__':
  unittest.main()