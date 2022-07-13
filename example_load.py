import SRDB

print(SRDB.root)
SRDB.root["foo"] = 1
SRDB.save_pending()
exit()
SRDB.root["foo"] = {}
print(SRDB.root.refcount)
print(my_dict.refcount)

SRDB.root["bar"] = {}
print(SRDB.root.refcount)
print(my_dict.refcount)

