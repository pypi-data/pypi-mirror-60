import unittest


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    return obj


def json_dict_comparator(dict1, dict2):
    return ordered(dict1) == ordered(dict2)


class TestJsonDictAnyOrderEqual(unittest.TestCase):

    def test_two_simple_dicts_are_equal(self):
        d1 = {'error': 'a', 'data': 'b'}
        d2 = {'error': 'a', 'data': 'b'}
        self.assertTrue(json_dict_comparator(d1, d2))

    def test_two_simple_dicts_are_not_equal(self):
        d1 = {'error': 'a', 'data': 'b'}
        d2 = {'error': 'as', 'data': 'b'}
        self.assertFalse(json_dict_comparator(d1, d2))

    def test_two_nested_dicts_with_list_in_different_order_are_equal(self):
        d1 = {
            'error': [
                {
                    'b': 1,
                    'c': 2,
                    'd': 3
                }, {
                    'x': 1,
                    'q': 2,
                    'w': 3
                }, {
                    'j': 1,
                    'k': 2,
                    'n': 3
                }
            ],
            'data': 'b'
        }
        d2 = {
            'error': [
                {
                    'x': 1,
                    'q': 2,
                    'w': 3
                }, {
                    'b': 1,
                    'c': 2,
                    'd': 3
                }, {
                    'j': 1,
                    'k': 2,
                    'n': 3
                }
            ],
            'data': 'b'
        }
        self.assertTrue(json_dict_comparator(d1, d2))

    def test_two_nested_dicts_with_list_in_different_order_are_not_equal(self):
        d1 = {
            'error': [
                {
                    'b': 1,
                    'c': 2,
                    'd': 3
                }, {
                    'x': 1,
                    'q': 2,
                    'w': 3
                }, {
                    'j': 1,
                    'k': 2,
                    'n': 33 # difference
                }
            ],
            'data': 'b'
        }
        d2 = {
            'error': [
                {
                    'x': 1,
                    'q': 2,
                    'w': 3
                }, {
                    'b': 1,
                    'c': 2,
                    'd': 3
                }, {
                    'j': 1,
                    'k': 2,
                    'n': 3
                }
            ],
            'data': 'b'
        }
        self.assertFalse(json_dict_comparator(d1, d2))

    def test_two_more_nested_dicts_with_lists_in_different_order_are_equal(self):
        d1 = {
            'error': [
                {
                    'z': [
                            {
                                'fdsa': 10
                            }, {
                                'zxcv': 4
                            }
                    ]
                }, {
                    'b': 1,
                    'c': 2,
                    'd': 3
                }, {
                    'x': 1,
                    'q': 2,
                    'w': 3
                }
            ],
            'data': 'b'
        }
        d2 = {
            'error': [
                {
                    'x': 1,
                    'q': 2,
                    'w': 3
                }, {
                    'b': 1,
                    'c': 2,
                    'd': 3
                }, {
                    'z': [
                        {
                            'zxcv': 4
                        }, {
                            'fdsa': 10
                        }
                    ]
                }
            ],
            'data': 'b'
        }
        self.assertTrue(json_dict_comparator(d1, d2))

    def test_two_more_nested_dicts_with_lists_in_different_order_are_not_equal(self):
        d1 = {
            'error': [
                {
                    'z': [
                            {
                                'fdsa': 10
                            }, {
                                'zxcv': 4
                            }
                    ]
                }, {
                    'b': 1,
                    'c': 2,
                    'd': 3
                }, {
                    'x': 1,
                    'q': 2,
                    'w': 3
                }
            ],
            'data': 'b'
        }
        d2 = {
            'error': [
                {
                    'x': 1,
                    'q': 2,
                    'w': 3
                }, {
                    'b': 1,
                    'c': 2,
                    'd': 3
                }, {
                    'z': [
                        {
                            'zxcv': 44 # difference
                        }, {
                            'fdsa': 10
                        }
                    ]
                }
            ],
            'data': 'b'
        }
        self.assertFalse(json_dict_comparator(d1, d2))


if __name__ == '__main__':
    unittest.main()
