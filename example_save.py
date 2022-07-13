import SRDB

my_dict = SRDB.Dict({
    "x": 1,
    "y": 2
})

SRDB.root['foo'] = SRDB.Dict({'a': 1, 'b': 2})
SRDB.root['bar'] = SRDB.root['foo']

'''
A = SRDB.Dict()
A["x"] = 1
A["y"] = 2

B = SRDB.Dict()
B["foo"] = 3
B["bar"] = A

SRDB.root["my_big_dict"] = SRDB.Dict()
SRDB.root["my_big_dict"]["A"] = A
SRDB.root["my_big_dict"]["B"] = B
'''

SRDB.save_pending()