import SRDB

s = SRDB.Dict.load('student/email_addr=yianni.mitropoulos@gmail.com')
s.decr_refcount()
SRDB.save_pending()