from django.core.management.base import BaseCommand, CommandError
from django.core.management import execute_from_command_line

from djcelery.management.base import CeleryCommand
    
class Command(CeleryCommand):
    args = ''
    help = 'Runs a celery worker acting on the test database. Assumes test database to exist. Useful to run in background in tests.'

    def switch_to_test_db(self, conn):
        from django.conf import settings

        """
        Assumes a test database to exist and switches to use it.
        """
        test_database_name = conn.creation._get_test_db_name()

        conn.close()
        settings.DATABASES[conn.alias]["NAME"] = test_database_name
        conn.settings_dict["NAME"] = test_database_name

        # Get a cursor (even though we don't need one yet). This has
        # the side effect of initializing the test database.
        try:
            conn.cursor()
        except:
            raise Exception("Not implemented yet: './manage.py celerytestworker' expects the test database to be present.")
            
        return test_database_name

    def run_from_argv(self, argv):
        from django.db import connections

        for alias in connections:
            conn = connections[alias]
            self.switch_to_test_db(conn)

        execute_from_command_line(argv[:1] + ['celery', 'worker'] + argv[2:])