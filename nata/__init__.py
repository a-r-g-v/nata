#!/usr/bin/env python2 
import time
import sys
from .usecases import DebugUseCase, AppUseCase, ServiceUseCase
from .domains import Spec
from .mappers import init_engine, Base, create_session
from .config import config

Session = create_session(init_engine())

## argv parser


def debug_parser():
    DebugUseCase.do()


def app_parser():
    def print_help():
        print('app help')

    if len(sys.argv) < 3:
        print_help()

    elif sys.argv[2] == 'create':
        AppUseCase.create(Spec(filename=sys.argv[3]))

    elif sys.argv[2] == 'list':
        AppUseCase.list()

    elif sys.argv[2] == 'delete':
        AppUseCase.delete(sys.argv[3])

    else:
        print_help()


def service_parser():
    def print_help():
        print('service help')

    if len(sys.argv) < 3:
        print_help()
    elif sys.argv[2] == 'create':
        ServiceUseCase.create(Spec(filename=sys.argv[3]))

    elif sys.argv[2] == 'list':
        ServiceUseCase.list()

    elif sys.argv[2] == 'delete':
        ServiceUseCase.delete(sys.argv[3])

    elif sys.argv[2] == 'switch':
        ServiceUseCase.switch(sys.argv[3], sys.argv[4])

    else:
        print_help()


def parser():
    def print_notfound(command):
        print("""{name}: '{command}' is not a {name} command.
See '{name} --help'.
        """.format(name=sys.argv[0], command=command))

    def print_help():
        print("""Usage: {name} COMMAND [arg...]

deployment toolkit for google compute engine

Commands:
    app
    service 
        """.format(name=sys.argv[0]))

    if len(sys.argv) < 2:
        print_help()

    elif sys.argv[1] == 'app':
        app_parser()

    elif sys.argv[1] == 'service':
        service_parser()

    elif sys.argv[1] == 'debug':
        debug_parser()

    else:
        print_notfound(sys.argv[1])


def main():
    Base.metadata.create_all(init_engine())

    parser()


if __name__ == '__main__':
    main()
