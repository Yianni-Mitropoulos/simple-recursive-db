import SRDB

s = SRDB.Dict.load('student/email_addr=yianni.mitropoulos@gmail.com')
print(s)
print(s['target'])