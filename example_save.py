import SRDB

A = SRDB.Dict().set_id_random()
A["x"] = 1
A["y"] = 2
B = SRDB.Dict().set_id_random()
B["foo"] = 3
B["bar"] = A
access_point = SRDB.Dict().set_id_computed('student/email_addr=yianni.mitropoulos@gmail.com')
access_point["target"] = B
access_point.refcount = 1
SRDB.save_pending()