import SRDB

# Phase 1
fst_dict = SRDB.Dict({
    "x": 1,
    "y": 2
})
snd_dict = SRDB.Dict({
    "A": 3,
    "B": fst_dict
})
SRDB.root['fst'] = fst_dict
SRDB.root['snd'] = snd_dict
SRDB.save_pending()

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

