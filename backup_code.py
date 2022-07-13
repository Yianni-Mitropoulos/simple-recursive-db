import shutil

class Table(Dict):

    def __init__(self, id=None):
        super().__init__(id)
        if id is None:
            try:
                os.mkdir(self.dir_path)
            except Exception:
                print(f"Directory already exists ({self.id}, {self.dir_path})")

    def stateful_children(self):
        def new_generator():
            for short_filename in os.listdir(self.dir_path):
                long_filename = os.path.join(self.dir_path, short_filename)
                with open(long_filename) as file:
                    data = file.readline().strip()
                    yield eval(data)
        return new_generator()

    def finalize_save(self):
        shutil.rmtree(self.dir_path)

    '''
    def set_type(self, t):
        if not isinstance(t, str):
            t = t.__name__
        super().__setitem__("type", t)
    '''

    def __getitem__(self, key):
        assert isinstance(key, str)
        hex_digest = compute_uuid(key)
        try:
            with open(os.path.join(self.dir_path, hex_digest)) as file:
                data = file.readline().strip()
        except Exception:
            raise KeyError
        else:
            return eval(data)
            '''
            return eval(f"{super().__getitem__('type')}('{data}')")
            '''

    def __setitem__(self, key, value):
        assert isinstance(key, str)
        ''' assert type(value).__name__ == super().__getitem__('type') '''
        # Deal with old value
        try:
            old_value = self[key]
        except KeyError:
            pass
        else:
            old_value.decr_refcount()
        # Deal with new value
        hex_digest = compute_uuid(key)
        with open(os.path.join(self.dir_path, hex_digest), "w") as file:
            file.write(repr(value))
        value.incr_refcount()