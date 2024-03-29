import SRDB

# Phase 1
def f1():
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
    SRDB.root['my_table'] = SRDB.Table()
    SRDB.save_pending()

def f2():
    SRDB.root['my_table'].set_value('hello', SRDB.root['fst'])

def f3():
    SRDB.root['my_table'].set_value('hello', [3, 4, 5])

def f4():
    SRDB.root['my_table'].set_value('world', [1, 2])
    SRDB.root['my_table'].set_value('lol', SRDB.Dict({'y': 1, 'z': 8}))

def f5():
    x = SRDB.root['my_table'].get_value('hello')
    print(x, type(x))

# f1()
# f2()
# f3()
# f1()

f1()
f2()
f3()
f1()

# SRDB.root['my_table'].SET('hello', None)