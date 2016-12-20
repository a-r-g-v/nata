
import os

os.environ['NATA_SCHEMA'] = 'sqlite://'

from nata.config import config
from nata.mappers import init_engine

engine = init_engine()
