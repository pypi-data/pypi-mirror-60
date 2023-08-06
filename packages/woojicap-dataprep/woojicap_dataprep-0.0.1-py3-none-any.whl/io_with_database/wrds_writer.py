from wooji_database.interfaces.stock import StockData, StockProfile, StockUniverse

from io_with_database.database_writer import WoojiCapDB


class WRDSWriter(WoojiCapDB):
    def __init__(self, **kwargs):
        super(WRDSWriter, self).__init__(**kwargs)

    def write_to_db(self, input_stream):
        # TODO: extract info from input_stream to construct corresponding Stock* objects
        print(StockProfile.symbol)
        print(StockData.symbol)
        print(StockUniverse.name)

    def read_from_db(self, which_data):
        pass
