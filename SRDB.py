import secrets
import os
import hashlib

# id sizes
ID_SIZE_IN_BITS  = 128
ID_SIZE_IN_CHARS = ID_SIZE_IN_BITS//4 # i.e. hexadecimal characters
ID_SIZE_IN_BYTES = ID_SIZE_IN_BITS//8

# zero id
ZERO_ID = '0' * ID_SIZE_IN_CHARS

def generate_random_uuid():
    L = []
    for _ in range(ID_SIZE_IN_CHARS):
        random_int = secrets.randbits(4)
        if random_int < 10:
            random_char = chr(random_int + 48)
        else:
            random_char = chr(random_int + 87)
        L.append(random_char)
    return "".join(L)

def compute_uuid(input_str):
    return hashlib.blake2b(
        input_str.encode(encoding = 'UTF-8', errors = 'strict'),
        digest_size=ID_SIZE_IN_BYTES
    ).hexdigest()

class Stateful:

    def __init__(self, id=None):
        self.savelist = []
        if id is None:
            self.refcount = 0
            self.dict = {}
            self.new = True
        else:
            self.id = id
            self.file_path = os.path.join(data_path, self.id)
            self.new = False

    def __set_id(self, id):
        self.id = id
        self.file_path = os.path.join(data_path, self.id)

    def set_id_random(self):
        id = generate_random_uuid()
        self.__set_id(id)
        return self

    def set_id_computed(self, input_str):
        id = compute_uuid(input_str)
        self.__set_id(id)
        return self

    @classmethod
    def load(cls, query):
        return cls(compute_uuid(query))

    def save(self):
        for stateful in self.savelist:
            stateful.save()
        with open(self.file_path, 'w') as file:
            file.write(f"{self.refcount:019} ")
            file.write(str(self))

    def __repr__(self):
        return f'{type(self).__name__}("{self.id}")'

class Dict(Stateful):

    def __init__(self, id=None):
        super().__init__(id)
        if not self.new:
            with open(self.file_path) as file:
                self.refcount = int(file.read(19))
                file.seek(20)
                line = next(file)
                self.dict = eval(line)

    def __str__(self):
        return repr(self.dict)

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, value):
        try:
            old_value = self.dict[key]
            old_value.refcount -= 1
            self.savelist.append(old_value)
        except:
            pass
        try:
            value.refcount += 1
            self.savelist.append(value)
        except:
            pass
        self.dict[key] = value

data_path = os.path.join(os.getcwd(), "SRDB_statefuls")

try:
    os.mkdir(data_path)
except FileExistsError:
    pass