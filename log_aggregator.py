import logging

class LogAggregator(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        self.logs.append(self.format(record))

    def clear(self):
        self.logs = []

    def get_logs(self):
        return "\n".join(self.logs)