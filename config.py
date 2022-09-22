from os import path, environ
import os
from dotenv import load_dotenv

## Init the logging object.
import logging
from datetime import datetime, timedelta
import sys

# Courtesy of: https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout
class LogFormatter(logging.Formatter):

    COLOR_CODES = {
        logging.CRITICAL: "\033[1;35m", # bright/bold magenta
        logging.ERROR:    "\033[1;31m", # bright/bold red
        logging.WARNING:  "\033[1;33m", # bright/bold yellow
        logging.INFO:     "\033[0;37m", # white / light gray
        logging.DEBUG:    "\033[1;30m"  # bright/bold black / dark gray
    }

    RESET_CODE = "\033[0m"

    def __init__(self, color, *args, **kwargs):
        super(LogFormatter, self).__init__(*args, **kwargs)
        self.color = color

    def format(self, record, *args, **kwargs):
        if (self.color is True and record.levelno in self.COLOR_CODES):
            record.color_on  = self.COLOR_CODES[record.levelno]
            record.color_off = self.RESET_CODE
        else:
            record.color_on  = ""
            record.color_off = ""
        return super(LogFormatter, self).format(record, *args, **kwargs)

# Courtesy of: https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout
def setup_logging(console_log_output, console_log_level, console_log_color, logfile_file, logfile_log_level, logfile_log_color, log_line_template):

    # Create logger
    # For simplicity, we use the root logger, i.e. call 'logging.getLogger()'
    # without name argument. This way we can simply use module methods for
    # for logging throughout the script. An alternative would be exporting
    # the logger, i.e. 'global logger; logger = logging.getLogger("<name>")'
    logger = logging.getLogger()

    # Set global log level to 'debug' (required for handler levels to work)
    logger.setLevel(logging.DEBUG)

    # Create console handler
    console_log_output = console_log_output.lower()
    if (console_log_output == "stdout"):
        console_log_output = sys.stdout
    elif (console_log_output == "stderr"):
        console_log_output = sys.stderr
    else:
        print("Failed to set console output: invalid output: '%s'" % console_log_output)
        return False
    console_handler = logging.StreamHandler(console_log_output)

    # Set console log level
    try:
        console_handler.setLevel(console_log_level.upper()) # only accepts uppercase level names
    except:
        print("Failed to set console log level: invalid level: '%s'" % console_log_level)
        return False

    # Create and set formatter, add console handler to logger
    console_formatter = LogFormatter(fmt=log_line_template, color=console_log_color)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Create log file handler
    try:
        # Check ../logs folder.
        if not path.isdir('../logs/'):
            print('Successfully set up logs folder.')
            os.mkdir('../logs/')

        logfile_handler = logging.FileHandler(logfile_file)
    except Exception as exception:
        print("Failed to set up log file: %s" % str(exception))
        return False

    # Set log file log level
    try:
        logfile_handler.setLevel(logfile_log_level.upper()) # only accepts uppercase level names
    except Exception as e:
        print("Failed to set log file log level: invalid level: '%s'" % logfile_log_level, e)
        return False

    # Create and set formatter, add log file handler to logger
    logfile_formatter = LogFormatter(fmt=log_line_template, color=logfile_log_color)
    logfile_handler.setFormatter(logfile_formatter)
    logger.addHandler(logfile_handler)

    # Success
    return True

# Courtesy of: https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout
setup_logging(console_log_output="stdout", console_log_level="debug", console_log_color=True,
                        logfile_file='../logs/{:%Y-%m-%d}.log'.format(datetime.now()), logfile_log_level="debug", logfile_log_color=False,
                        log_line_template="%(color_on)s[%(asctime)s] [%(threadName)s] [%(levelname)-8s] %(message)s%(color_off)s")

# Load the .env file from this directory.
load_dotenv(path.join(path.dirname(__file__), '.env'))

def load_secret_key(PATH: str) -> str:
    '''
    Loads the secret key from the path specified.
    
    NOTE: This file should have read-only access.
    '''
    try:
        f = open(PATH, 'rb')
    except (OSError, IOError, FileNotFoundError) as e:
        raise e

    with f:
        return f.readline().decode('utf-8')

def load_email_password(PATH: str) -> str:
    '''
    Loads the email password from the path specified.
    
    NOTE: This file should have read-only access.
    '''
    try:
        f = open(PATH, 'rb')
    except (OSError, IOError, FileNotFoundError) as e:
        raise e

    with f:
        return f.readline().decode('utf-8')
        
class Config():
    '''
    Base Config object, which sets the secret key and email password.
    '''
    
    # Get the secret key, reporting any errors.
    try:
        SECRET_KEY_PATH = environ.get('SECRET_KEY_PATH')
        SECRET_KEY = load_secret_key(SECRET_KEY_PATH)
    except (OSError, IOError, FileNotFoundError) as e:
        logging.critical(f'Unable to load key file from location: {SECRET_KEY_PATH}')
        print('Unable to load key file. Please check the location specified in the .env file and that the file has read access.')
        raise SystemExit()

    # Get the email password, reporting any errors. 
    try:
        EMAIL_PASS_PATH = environ.get('EMAIL_PASSWORD_PATH')
        EMAIL_PASSWORD = load_email_password(EMAIL_PASS_PATH)
    except (OSError, IOError, FileNotFoundError) as e:
        logging.critical(f'Unable to load email password file from location: {EMAIL_PASS_PATH}')
        print('Unable to load email password file. Please check the location specified in the .env file and that the file has read access.')
        raise SystemExit()

    EMAIL_USERNAME = environ.get('EMAIL_ADDRESS')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=5)
    SESSION_FILE_DIR= '../cookies'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProdConfig(Config):
    '''
    Production config class. Sets the appropriate Debugging and Testing settings.
    '''
    ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + environ.get('PROD_DATABASE_PATH')

class DevConfig(Config):
    '''
    Development config class. Sets the appropriate Debugging and Testing settings.
    '''
    ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + environ.get('DEV_DATABASE_PATH')