import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
  "dashboard.log",
  maxBytes = 1_000_000,
  backupCount=5
)

formatter = logging.Formatter(
  "%(asctime)s %(levelname)s %(message)s"
)

handler.setFormatter(formatter)

logger= logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)




















