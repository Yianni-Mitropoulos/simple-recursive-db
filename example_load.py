import SRDB

my_small_dict = SRDB.root["my_small_dict"]
print(my_small_dict.id)

my_big_dict = SRDB.root["my_big_dict"]
print(my_big_dict.id)
print(my_big_dict["my_small_dict"])

# SRDB.root["B"] = 3
SRDB.save_pending()

# s = SRDB.Dict.load('student/email_addr=yianni.mitropoulos@gmail.com')
# s.decr_refcount()
# SRDB.save_pending()