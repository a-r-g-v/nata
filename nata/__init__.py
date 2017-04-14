#!/usr/bin/env python2 
import time
import sys
from .config import config
from typing import Any

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
import threading
import logging

# datastore
def create_session(engine):
    # typed: (Any) -> Any
    local = threading.local()

    def get_session():
        # typed: () -> Any
        if hasattr(local, 'session'):
            return local.session
        local.session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=engine))
        return local.session

    return get_session


def init_engine(echo=False):
    # type: (bool) -> Any
    return create_engine(config['schema'], encoding='utf-8', echo=echo)

Session = create_session(init_engine())

# log

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)-4d: %(message)s')

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logger.addHandler(handler)

