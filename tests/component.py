import requests
import unittest
import json

cars_url = 'http://localhost:8080'
parts_url = 'http://localhost:8081'
add_cars_url = f'{cars_url}/cars'
get_cars_by_id_url = f'{cars_url}/cars'
get_cars_url = f'{cars_url}/cars'


class TestComponent(unittest.TestCase):

    def add_cars(self):
        car = {
            "id": 10,
            "name": "BMW"

        }
        res = requests.post(add_cars_url, json=car)
        self.assertEqual(res, "Success")

    def test_cars_get(self):
        res = requests.get(f"{get_cars_by_id_url}/0").json()
        self.assertEqual(res['name'], "test")


    def fetch_cars(self):
        res = requests.get(get_cars_url)
        self.assertTrue(res != "Cant access database!")


if __name__ == '__main__':
    unittest.main()