import SRDB

B = SRDB.root["B"]
print(B)
# SRDB.root["B"] = 3
SRDB.save_pending()

# s = SRDB.Dict.load('student/email_addr=yianni.mitropoulos@gmail.com')
# s.decr_refcount()
# SRDB.save_pending()