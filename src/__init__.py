from exceptions import NoConfigFoundError
import logging,os
from handlers import CachedHandler


__version__ = "0.0.1"

formatter = logging.Formatter(
	'%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
handler = CachedHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.DEBUG)

from configuration import Configuration,DefaultConfiguration

try:
    settings = Configuration()
except NoConfigFoundError:
    settings = DefaultConfiguration()

def db_table_exists(table, cursor=None):
    try:
        if not cursor:
            from django.db import connection
            cursor = connection.cursor()
        if not cursor:
            raise Exception
        table_names = connection.introspection.get_table_list(cursor)
    except:
        raise Exception("unable to determine if the table '%s' exists" % table)
    else:
        return table in table_names

if not db_table_exists('bilbo_core_file'):
    print "Bilbo's database appears to be uninitialised. We will need to create some tables before we can run anything"
    from django.core.management.commands import syncdb
    syncdb.Command().run_from_argv(['bilbo','syncdb'])
