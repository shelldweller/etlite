#!/usr/bin/env python

import unittest
try:
    # python 2
    from StringIO import StringIO
except ImportError:
    # python 3
    from io import StringIO

from etlite import delim_reader, TransformationError

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


class TestException(unittest.TestCase):
    def setUp(self):
        self.saw_error = False

    def test_unhandled_transformation_exception(self):
        rules = [ {"from": "num", "to": "num", "via": int} ]
        stream = StringIO("num\none")
        with self.assertRaises(TransformationError) as err:
            list(delim_reader(stream, rules))
        self.assertEqual(err.exception.args[0], "ValueError: invalid literal for int() with base 10: 'one', in line 2")
        self.assertEqual(err.exception.record, {"num": "one"})

    def test_handled_trnsformation_exception(self):
        rules = [{"from": "num", "to": "num", "via": int}]
        stream = StringIO("num\none\n1")

        def error_handler(e):
            self.saw_error = True

        reader = delim_reader(stream, rules, on_error=error_handler)
        result = [row for row in reader]

        self.assertTrue(self.saw_error)
        self.assertEqual(result, [{'num': 1}])


if __name__ == '__main__':
    unittest.main()
