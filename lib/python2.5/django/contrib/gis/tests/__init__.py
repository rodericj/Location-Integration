import sys, unittest
from django.utils.importlib import import_module

def geo_suite():
    """
    Builds a test suite for the GIS package.  This is not named
    `suite` so it will not interfere with the Django test suite (since
    spatial database tables are required to execute these tests on
    some backends).
    """
    from django.conf import settings
    from django.contrib.gis.gdal import HAS_GDAL
    from django.contrib.gis.utils import HAS_GEOIP
    from django.contrib.gis.tests.utils import mysql

    # The test suite.
    s = unittest.TestSuite()

    # Tests that require use of a spatial database (e.g., creation of models)
    test_apps = ['geoapp', 'relatedapp']

    # Tests that do not require setting up and tearing down a spatial database.
    test_suite_names = [
        'test_measure',
        ]

    # Tests applications that require a test spatial db.
    if not mysql:
        test_apps.append('distapp')

    if HAS_GDAL:
        # These tests require GDAL.
        test_suite_names.append('test_spatialrefsys')
        test_apps.append('layermap')

        # Adding the GDAL tests.
        from django.contrib.gis.gdal import tests as gdal_tests
        s.addTest(gdal_tests.suite())
    else:
        print >>sys.stderr, "GDAL not available - no tests requiring GDAL will be run."

    if HAS_GEOIP and hasattr(settings, 'GEOIP_PATH'):
        test_suite_names.append('test_geoip')

    # Adding the rest of the suites from the modules specified
    # in the `test_suite_names`.
    for suite_name in test_suite_names:
        tsuite = import_module('django.contrib.gis.tests.' + suite_name)
        s.addTest(tsuite.suite())

    # Adding the GEOS tests _last_.  Doing this because if suite starts
    # immediately with this test while after running syncdb, it will cause a
    # segmentation fault.  My initial guess is that SpatiaLite is still in
    # critical areas of non thread-safe GEOS code when the test suite is run.
    # TODO: Confirm my reasoning. Are there other consequences?
    from django.contrib.gis.geos import tests as geos_tests
    s.addTest(geos_tests.suite())

    return s, test_apps

def run_gis_tests(test_labels, **kwargs):
    """
    Use this routine as the TEST_RUNNER in your settings in order to run the
    GeoDjango test suite.  This must be done as a database superuser for
    PostGIS, so read the docstring in `run_test()` below for more details.
    """
    from django.conf import settings
    from django.db.models import loading
    from django.contrib.gis.tests.utils import mysql

    # Getting initial values.
    old_installed = settings.INSTALLED_APPS
    old_root_urlconf = settings.ROOT_URLCONF

    # Overridding the INSTALLED_APPS with only what we need,
    # to prevent unnecessary database table creation.
    new_installed =  ['django.contrib.sites',
                      'django.contrib.sitemaps',
                      'django.contrib.gis',
                      ]

    # Setting the URLs.
    settings.ROOT_URLCONF = 'django.contrib.gis.tests.urls'

    # Creating the test suite, adding the test models to INSTALLED_APPS, and
    # adding the model test suites to our suite package.
    gis_suite, test_apps = geo_suite()
    for test_model in test_apps:
        module_name = 'django.contrib.gis.tests.%s' % test_model
        if mysql:
            test_module = 'tests_mysql'
        else:
            test_module = 'tests'
        new_installed.append(module_name)

        # Getting the model test suite
        tsuite = import_module(module_name + '.' + test_module)
        gis_suite.addTest(tsuite.suite())

    # Resetting the loaded flag to take into account what we appended to
    # the INSTALLED_APPS (since this routine is invoked through
    # django/core/management, it caches the apps; this ensures that syncdb
    # will see our appended models)
    settings.INSTALLED_APPS = new_installed
    loading.cache.loaded = False

    # Running the tests using the GIS test runner.
    result = run_tests(test_labels, suite=gis_suite, **kwargs)

    # Restoring modified settings.
    settings.INSTALLED_APPS = old_installed
    settings.ROOT_URLCONF = old_root_urlconf

    return result

def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[], suite=None):
    """
    This module allows users to run tests for GIS apps that require the creation
    of a spatial database.  Currently, this is only required for PostgreSQL as
    PostGIS needs extra overhead in test database creation.

    In order to create a PostGIS database, the DATABASE_USER (or
    TEST_DATABASE_USER, if defined) will require superuser priviliges.

    To accomplish this outside the `postgres` user, you have a few options:
      (A) Make your user a super user:
        This may be done at the time the user is created, for example:
        $ createuser --superuser <user_name>

        Or you may alter the user's role from the SQL shell (assuming this
        is done from an existing superuser role):
        postgres# ALTER ROLE <user_name> SUPERUSER;

      (B) Create your own PostgreSQL database as a local user:
        1. Initialize database: `initdb -D /path/to/user/db`
        2. If there's already a Postgres instance on the machine, it will need
           to use a different TCP port than 5432. Edit postgresql.conf (in
           /path/to/user/db) to change the database port (e.g. `port = 5433`).
        3. Start this database `pg_ctl -D /path/to/user/db start`

      (C) On Windows platforms the pgAdmin III utility may also be used as
        a simple way to add superuser privileges to your database user.

    The TEST_RUNNER needs to be set in your settings like so:

      TEST_RUNNER='django.contrib.gis.tests.run_tests'

    Note: This test runner assumes that the PostGIS SQL files ('lwpostgis.sql'
    and 'spatial_ref_sys.sql') are installed in the directory specified by
    `pg_config --sharedir` (and defaults to /usr/local/share if that fails).
    This behavior is overridden if POSTGIS_SQL_PATH is set in your settings.

    Windows users should set POSTGIS_SQL_PATH manually because the output
    of `pg_config` uses paths like 'C:/PROGRA~1/POSTGR~1/..'.

    Finally, the tests may be run by invoking `./manage.py test`.
    """
    from django.conf import settings
    from django.db import connection
    from django.db.models import get_app, get_apps
    from django.test.simple import build_suite, build_test
    from django.test.utils import setup_test_environment, teardown_test_environment

    # The `create_test_spatial_db` routine abstracts away all the steps needed
    # to properly construct a spatial database for the backend.
    from django.contrib.gis.db.backend import create_test_spatial_db

    # Setting up for testing.
    setup_test_environment()
    settings.DEBUG = False
    old_name = settings.DATABASE_NAME

    # Creating the test spatial database.
    create_test_spatial_db(verbosity=verbosity)

    # The suite may be passed in manually, e.g., when we run the GeoDjango test,
    # we want to build it and pass it in due to some customizations.  Otherwise,
    # the normal test suite creation process from `django.test.simple.run_tests`
    # is used to create the test suite.
    if suite is None:
        suite = unittest.TestSuite()
        if test_labels:
            for label in test_labels:
                if '.' in label:
                    suite.addTest(build_test(label))
                else:
                    app = get_app(label)
                    suite.addTest(build_suite(app))
        else:
            for app in get_apps():
                suite.addTest(build_suite(app))

        for test in extra_tests:
            suite.addTest(test)

    # Executing the tests (including the model tests), and destorying the
    # test database after the tests have completed.
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    connection.creation.destroy_test_db(old_name, verbosity)
    teardown_test_environment()

    # Returning the total failures and errors
    return len(result.failures) + len(result.errors)

# Class for creating a fake module with a run method.  This is for the
# GEOS and GDAL tests that were moved to their respective modules.
class _DeprecatedTestModule(object):
    def __init__(self, mod_name):
        self.mod_name = mod_name

    def run(self):
        from warnings import warn
        warn('This test module is deprecated because it has moved to ' \
             '`django.contrib.gis.%s.tests` and will disappear in 1.2.' %
             self.mod_name, DeprecationWarning)
        tests = import_module('django.contrib.gis.%s.tests' % self.mod_name)
        tests.run()

test_geos = _DeprecatedTestModule('geos')
test_gdal = _DeprecatedTestModule('gdal')
