from configparser import ConfigParser

_CFG_FILENAME = 'capstone.ini'

_DB_SECTION = 'database'
_DB_HOST_OPT = 'host'
_DB_PORT_OPT = 'port'
_DB_NAME_OPT = 'database'
_DB_USERNAME_OPT = 'user'
_DB_PASSWORD_OPT = 'password'

DB_HOST = None
DB_PORT = None
DB_NAME = None
DB_USERNAME = None
DB_PASSWORD = None

_AV_SECTION = 'alphavantage'
_AV_APIKEY_OPT = 'apikey'

AV_APIKEY = None


def load_config():

    global DB_HOST
    global DB_PORT
    global DB_NAME
    global DB_USERNAME
    global DB_PASSWORD

    global AV_APIKEY

    parser = ConfigParser()

    parser.read(_CFG_FILENAME)

    DB_HOST = parser.get(_DB_SECTION, _DB_HOST_OPT)
    DB_PORT = parser.get(_DB_SECTION, _DB_PORT_OPT)
    DB_NAME = parser.get(_DB_SECTION, _DB_NAME_OPT)
    DB_USERNAME = parser.get(_DB_SECTION, _DB_USERNAME_OPT)
    DB_PASSWORD = parser.get(_DB_SECTION, _DB_PASSWORD_OPT)

    AV_APIKEY = parser.get(_AV_SECTION, _AV_APIKEY_OPT)


def get_database_items():

    return {
        _DB_HOST_OPT: DB_HOST,
        _DB_PORT_OPT: DB_PORT,
        _DB_NAME_OPT: DB_NAME,
        _DB_USERNAME_OPT: DB_USERNAME,
        _DB_PASSWORD_OPT: DB_PASSWORD
    }


load_config()

