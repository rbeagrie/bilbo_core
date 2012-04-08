import logging
import logging.handlers

class CachedHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.records = []
        self.cache = True

    def flush_records(self):
        logging.debug('Flushing cached logging records')
        self.cache = False
        root = logging.getLogger()
        for rec in self.records:
            root.handle(rec)
        self.records = []

    def emit(self, record):
        # add message to history queue
        if self.cache:
            self.records.append(record)
        else:
            logging.StreamHandler.emit(self,record)
