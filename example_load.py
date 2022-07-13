import SRDB

my_big_dict = SRDB.root["my_big_dict"]
print(my_big_dict["foo"])
print(my_big_dict["bar"])

# SRDB.save_pending()