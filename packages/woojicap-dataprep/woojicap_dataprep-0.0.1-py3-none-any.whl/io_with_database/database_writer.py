class WoojiCapDB(object):
    def __init__(self, db, username, password):
        self.db = db
        self.username = username
        self.password = password

    def write_to_db(self, input_stream):
        raise NotImplementedError

    def read_from_db(self, which_data):
        raise NotImplementedError
