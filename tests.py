#!/usr/bin/env python

import unittest
try:
    # python 2
    from StringIO import StringIO
except ImportError:
    # python 3
    from io import StringIO

from etlite import delim_reader

class TestTransformations(unittest.TestCase):
    def setUp(self):
        self.transformations = [
            {
                "from": "Dissemination area",
                "to": "id",
            },
            {
                "from": "Male",
                "to": "population.male",
                "via": int
            },
            {
                "from": "Female",
                "to": "population.female",
                "via": int
            },
            {
                "from": "Area",
                "to": "area",
                "via": float
            },
            {
                "to": "population.total",
                "via": lambda x: x['population']['male'] + x['population']['female']
            },
            {
                "to": 'population.density',
                "via": lambda x: round(x['population']['total'] / x['area']),
            }
        ]

        self.expected = [
            {
                'id': '12345',
                'area': 0.25,
                'population': {
                    'male': 34,
                    'female': 45,
                    'total': 79,
                    'density': 316
                }
            },
            {
                'id': '12346',
                'area': 0.32,
                'population': {
                    'male': 108,
                    'female': 99,
                    'total': 207,
                    'density': 647
                }
            }
        ]

    def test_delim_parser_csv(self):
        csvfile = StringIO(
            "Dissemination area,Male,Female,Area\n" \
            "12345,34,45,0.25\n" \
            "12346,108,99,0.32\n"
        )
        reader = delim_reader(csvfile, self.transformations)
        actual = [row for row in reader]
        self.assertListEqual(actual, self.expected)

    def test_delim_parser_tab(self):
        tabfile = StringIO(
            "Dissemination area\tMale\tFemale\tArea\n" \
            "12345\t34\t45\t0.25\n" \
            "12346\t108\t99\t0.32\n"
        )
        reader = delim_reader(tabfile, self.transformations, delimiter="\t")
        actual = [row for row in reader]
        self.assertListEqual(actual, self.expected)


if __name__ == '__main__':
    unittest.main()
