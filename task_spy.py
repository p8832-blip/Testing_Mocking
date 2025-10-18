from unittest.mock import MagicMock

class Logger:
    def log_error(self, msg):
        print(msg)

logger = Logger()
spy_logger = MagicMock(wraps=logger)
spy_logger.log_error("Critical error")
spy_logger.log_error.assert_called_with("Critical error")
