
# Create a database called DATABASE in your ACCOUNT.cloudant.com and make it world-writeable
import ConfigParser

def getconfig():

    Config = ConfigParser.ConfigParser()
    Config.read('config.cfg')
    USERNAME = Config.get('Database_info', 'USERNAME')
    PASSWORD= Config.get('Database_info', 'PASSWORD')
    URL= Config.get('Database_info', 'URL')
    DATABASE_NAME= Config.get('Database_info', 'DB_NAME')
    return USERNAME,PASSWORD,URL,DATABASE_NAME







