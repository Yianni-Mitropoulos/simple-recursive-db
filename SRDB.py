import secrets
import os
import hashlib
import shutil

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
        stateful.save()

class Stateful:

    def __init__(self):
        self._set_id(generate_random_uuid())
        self.refcount_modified = True
        self.contents_modified = True
        self.contents_loaded   = True
        self.exists_on_disk = False
        self.refcount = 0
        stateful_objects_tracker[self.id] = self

    @classmethod
    def from_id(cls, id):
        if id in stateful_objects_tracker:
            return stateful_objects_tracker[id]
        else:
            retval = cls()
            retval._set_id(id)
            retval.refcount_modified = False
            retval.contents_modified = False
            retval.contents_loaded   = False
            retval.exists_on_disk = True
            with open(retval.file_path, 'r') as file:
                file_data = file.read()
            retval.refcount = int(file_data[0:19])
            retval.assemble_contents_from_data(file_data[20:])
            stateful_objects_tracker[id] = retval
            return retval

    def _set_id(self, id):
        self.id = id
        self.dir_path  = os.path.join(data_path, self.id)
        self.file_path = os.path.join(data_path, f"{self.id}.{type(self).__name__}")
        return self

    def save(self):
        if self.refcount <= 0:
            print(f"Deleting {self.id}")
            # This MUST come first or the code won't work
            for stateful_child in self.stateful_children():
                print(f"Stateful child {stateful_child.id}")
                stateful_child.decr_refcount()
            # This must come second or third
            if os.path.isfile(self.file_path):
                os.remove(self.file_path)
            # This must come second or third
            self.finalize_deletion()
        else:
            data_string = f"{self.refcount:019} {str(self)}"
            # Can't do the above step inside the context manager because str(self) may need to open the file for reading
            # Also note that this code is very wasteful; it rebuilds the entire file, even if only part of it needs changing
            # Future versions of the library should improve on this behaviour
            with open(self.file_path, 'w') as file:
                file.write(data_string)
            self.finalize_save()
        self.refcount_modified = False
        self.contents_modified = False
        self.exists_on_disk = True

    def __repr__(self):
        return f'{type(self).__name__}.from_id("{self.id}")'

    def __hash__(self):
        return int(self.id, base=16)

    def finalize_save(self):
        pass

    def finalize_deletion(self):
        pass

    def incr_refcount(self):
        save_set.add(self)
        self.refcount += 1
        self.refcount_modified = True
    
    def decr_refcount(self):
        save_set.add(self)
        self.refcount -= 1
        self.refcount_modified = True

    def load_contents_if_necessary(self):
        if self.contents_loaded:
            return
        with open(self.file_path, 'r') as file:
            file_data = file.read()
        self.assemble_contents_from_data(file_data[20:])
        self.contents_loaded = True

    def register_change_in_contents(self):
        assert self.contents_loaded
        save_set.add(self)
        self.contents_modified = True

class Dict(Stateful):

    def __init__(self, d=None):
        super().__init__()
        if d is None:
            self.dict = {}
        else:
            self.dict = d
        for stateful_child in self.stateful_children():
            stateful_child.incr_refcount()

    def assemble_contents_from_data(self, data):
        self.dict = eval(data)

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
        self.load_contents_if_necessary()
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

class Table(Dict):

    def __init__(self, d=None):
        super().__init__(d)

    def stateful_nodes(self):
        def new_generator():
            for short_filename in os.listdir(self.dir_path):
                long_filename = os.path.join(self.dir_path, short_filename)
                with open(long_filename) as file:
                    data = file.read()
                    obj = eval(data)
                    if isinstance(obj, Stateful):
                        yield obj
        return new_generator()

    def finalize_save(self):
        print(f"Creating table {self.dir_path}")
        try:
            os.mkdir(self.dir_path)
        except Exception as e:
            print(e)

    def finalize_deletion(self):
        for stateful in self.stateful_nodes():
            stateful.decr_refcount()
        print(self.dir_path)
        shutil.rmtree(self.dir_path)

    def get_value(self, key):
        assert isinstance(key, str)
        hex_digest = compute_uuid(key)
        try:
            with open(os.path.join(self.dir_path, hex_digest)) as file:
                data = file.read()
        except Exception:
            raise KeyError
        else:
            return eval(data)

    def set_value(self, key, value):
        assert isinstance(key, str)
        save_pending()
        # Deal with old value
        try:
            old_value = self.get_value(key)
        except KeyError:
            pass
        else:
            if isinstance(old_value, Stateful):
                old_value.decr_refcount()
        # Deal with new value
        hex_digest = compute_uuid(key)
        with open(os.path.join(self.dir_path, hex_digest), "w") as file:
            file.write(repr(value))
        if isinstance(value, Stateful):
            value.incr_refcount()
        save_pending()

save_set = set()
stateful_objects_tracker = dict()
data_path = os.path.join(os.getcwd(), "SRDB_statefuls")

# Ensure there's a folder to store our data in
try:
    os.mkdir(data_path)
except FileExistsError:
    pass

# Create an object for the root directory
try:
    root = Dict.from_id(ZERO_ID)
except Exception as e:
    root = Dict()._set_id(ZERO_ID)
    root.incr_refcount()