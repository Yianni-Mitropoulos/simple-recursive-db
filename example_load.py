import SRDB

fst_dict = SRDB.root["fst"]
snd_dict = SRDB.root["snd"]
SRDB.root["snd"] = 3
SRDB.save_pending()