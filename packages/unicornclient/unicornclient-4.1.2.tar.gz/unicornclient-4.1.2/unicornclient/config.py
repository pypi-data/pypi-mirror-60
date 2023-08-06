import os
import logging

ENV = os.getenv('PYTHONENV', 'prod')

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

HOST = 'localhost'
PORT = 8080

SSL_VERIFY = False

DEFAULT_ROUTINES = ['auth', 'ping', 'status', 'system']

SECRET_PATH = '/tmp/unicornclient/secret'

if ENV == 'prod':
    LOG_LEVEL = logging.INFO
    HOST = 'unicorn.amnt.fr'
    SSL_VERIFY = True
    SECRET_PATH = '/etc/unicornclient/secret'

PROC_PATH = os.getenv('PROC_PATH', '/proc')
SYS_PATH = os.getenv('SYS_PATH', '/sys')
