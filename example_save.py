import SRDB

A = SRDB.Dict()
A["x"] = 1
A["y"] = 2

B = SRDB.Dict()
B["foo"] = 3
B["bar"] = A

SRDB.root["my_big_dict"] = SRDB.Table()
SRDB.root["my_big_dict"].set_type("Dict")
SRDB.root["my_big_dict"]["foo"] = A
SRDB.root["my_big_dict"]["bar"] = B

SRDB.save_pending()