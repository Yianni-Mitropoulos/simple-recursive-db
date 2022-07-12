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

def save_pending():
    while save_set:
        stateful = save_set.pop()
        print(f"Saving {repr(stateful)} == {stateful}")
        stateful.save()

class Stateful:

    def __init__(self, id=None):
        if id is None:
            self.refcounts_modified = True
            self.contents_modified  = True
            self.contents_loaded    = True
            self.refcount = 0
            self.dict = {}
        else:
            self._set_id(id)
            self.refcount_modified = False
            self.contents_modified = False
            self.contents_loaded   = False
            with open(self.file_path) as file:
                self.refcount = int(file.read(19))

    def _set_id(self, id):
        self.id = id
        self.file_path = os.path.join(data_path, self.id)
        return self

    def set_id_random(self):
        id = generate_random_uuid()
        self._set_id(id)
        return self

    def set_id_computed(self, input_str):
        id = compute_uuid(input_str)
        self._set_id(id)
        return self

    def incr_refcount(self):
        save_set.add(self)
        self.refcount_modified = True
        self.refcount += 1
    
    def decr_refcount(self):
        save_set.add(self)
        self.refcount_modified = True
        self.refcount -= 1

    '''
    @classmethod
    def load(cls, query):
        return cls(compute_uuid(query))
    '''

    def save(self):
        if self.refcount <= 0:
            if os.path.isfile(self.file_path):
                os.remove(self.file_path)
            for stateful_child in self.stateful_children():
                stateful_child.decr_refcount()
        else:
            # Kludgy solution to seek() being restricted to return values of tell()
            if self.contents_modified:
                self.refcount_modified = True
            with open(self.file_path, 'w') as file:
                if self.refcount_modified:
                    file.write(f"{self.refcount:019} ")
                if self.contents_modified:
                    file.write(str(self))
        self.refcount_modified = False
        self.contents_modified = False

    def __repr__(self):
        return f'{type(self).__name__}("{self.id}")'

    def __hash__(self):
        return int(self.id, base=16)

    def load_contents_if_necessary(self):
        if self.contents_loaded:
            return
        with open(self.file_path) as file:
            self.load_from_file(file)
        self.contents_loaded = True
        print(f"Loaded {repr(self)} == {self}")

    def register_change_in_contents(self):
        self.load_contents_if_necessary()
        self.contents_modified = True
        save_set.add(self)

class Dict(Stateful):

    '''
    def __init__(self, id=None):
        super().__init__(id)
    '''

    def load_from_file(self, file):
        file.seek(20)
        line = next(file)
        self.dict = eval(line)

    def stateful_children(self):
        self.load_contents_if_necessary()
        return (value for value in self.dict.values() if isinstance(value, Stateful))

    def __str__(self):
        self.load_contents_if_necessary()
        return repr(self.dict)

    def __getitem__(self, key):
        self.load_contents_if_necessary()
        return self.dict[key]

    def __setitem__(self, key, value):
        self.register_change_in_contents()
        # Deal with the old value for that key (if it exists)
        try:
            old_value = self.dict[key]
        except KeyError:
            pass
        else:
            if isinstance(old_value, Stateful):
                old_value.decr_refcount()
        # Deal with the new value for that key
        if isinstance(value, Stateful):
            value.incr_refcount()
        # And finally, insert the value
        self.dict[key] = value

save_set = set()
data_path = os.path.join(os.getcwd(), "SRDB_statefuls")

try:
    root = Dict(ZERO_ID)
except Exception as e:
    root = Dict()._set_id(ZERO_ID)
    root.incr_refcount()

try:
    os.mkdir(data_path)
except FileExistsError:
    pass