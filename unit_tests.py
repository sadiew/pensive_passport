import unittest
from server import *

class ServerTestCase(unittest.TestCase):

  def setUp(self):
    self.place = Place(google_place_id='xyz', lat=2, lon=3)


  def test_distance_from_city_center_valid_args(self):

    self.assertEqual(distance_from_city_center('1,2', self.place), 2)
    self.assertEqual(distance_from_city_center('-1,-2', self.place), 8)


  def test_distance_from_city_center_incorrect_num_args(self):
    self.invalid_distance_from_city_center('1', ValueError)
    self.invalid_distance_from_city_center('1,2,3', ValueError)
    self.invalid_distance_from_city_center(',', ValueError)


  def invalid_distance_from_city_center(self, test_input, exception_type):

    try:
      distance_from_city_center(test_input, self.place)
      self.assertTrue(False)

    except exception_type:
      self.assertTrue(True)

if __name__ == "__main__":
  unittest.main()