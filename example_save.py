import SRDB

A = SRDB.Dict()
A["x"] = 1
A["y"] = 2

B = SRDB.Dict()
B["foo"] = 3
B["bar"] = A

SRDB.root["my_small_dict"] = B
SRDB.root["my_big_dict"] = SRDB.Bigd()
SRDB.root["my_big_dict"].set_type("Dict")
SRDB.root["my_big_dict"]["foo"] = B

SRDB.save_pending()