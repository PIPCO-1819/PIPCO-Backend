import unittest
import numpy as np
import cv2
from ImageProcessing import *

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


# noinspection PyArgumentList
class TestImageProc(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

    def setUp(self):
        self.ImageProc = ImageProcessing(False)

    def test_get_contours_no_diff(self):
        array = np.zeros([100, 100], dtype=np.uint8)
        contours = self.ImageProc.get_contours_of_moved_objects(array)
        print(len(contours))
        self.assertEqual(len(contours), 0)

    def test_get_contours_diff(self):
        contours = self.ImageProc.get_contours_of_moved_objects(np.zeros([100, 100], dtype=np.uint8))
        img = np.zeros([100, 100], dtype=np.uint8)
        img[:] = 255
        contours = self.ImageProc.get_contours_of_moved_objects(img)
        self.assertGreater(len(contours), 0)

    def test_get_median(self):
        self.ImageProc.get_contours_of_moved_objects(np.zeros([100, 100], dtype=np.uint8))
        self.ImageProc.get_contours_of_moved_objects(np.zeros([100, 100], dtype=np.uint8))
        img = np.zeros([100, 100], dtype=np.uint8)
        img[:] = 255
        self.ImageProc.get_contours_of_moved_objects(img)
        old_image = self.ImageProc.get_median()
        self.assertEqual(old_image[0][0], 0)


    @classmethod
    def tearDownClass(self):
        pass


if __name__ == '__main__':
  unittest.main()
