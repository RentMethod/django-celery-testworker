django-celery-testworker - Testing with Django and Celery
=========================================================
Writing tests for Django projects that depend on Celery tasks is problematic. The test that queues the task typically operates on the test database (by virtue of Django's test framework), whereas the Celery worker, using the <a href="https://github.com/celery/django-celery">django-celery</a> integration, operates on the main database. When using the database backend for Celery, tasks will not even get picked up by the worker to begin with.

A celery worker that operates on the test database is needed. This app runs such a worker automatically in the background while running the test suite.

Using django-celery-testworker
==============================

To enable ``django-celery-testworker`` for your project you need to add ``djcelery-testworker`` to ``INSTALLED_APPS``:

    INSTALLED_APPS += ("djcelery-testworker", )

To run a Celery worker that operates on your test databases, run with Django's management command:

    ./manage.py celerytestworker

To create a unit test that depends on a Celery task, use the ``CeleryWorkerTestCase`` class. A worker will then automatically be started for this test. 

```
from testcase import CeleryWorkerTestCase
import time

class SomeTestCase(CeleryWorkerTestCase):
    def test_something(self):
        task = some_task.delay()
        time.sleep(1)
        self.assertEqual(task.state, "SUCCESS")
```

Technically, tests that depend on a celery worker running are not real unit tests, though, and should be implemented as integration tests.

To automatically launch a worker in the background while running an integration test suite, use the ``run_celery_test_worker`` function. For example, you could use it with lettuce by including it in ``terrain.py``:

```
# terrain.py
from django.test.simple import DjangoTestSuiteRunner
from django.test.utils import setup_test_environment, teardown_test_environment
from lettuce import *
from splinter.browser import Browser
from djcelery_testworker import run_celery_test_worker

@before.harvest
def initial_setup(server):
    setup_test_environment()
    
    # set up the test databases using DjangoTestSuiteRunner
    world.django_suite = DjangoTestSuiteRunner()
    world.django_suite.old_config = world.django_suite.setup_databases()

    # run a celery worker
    print "Starting Celery worker..."
    world.celeryd = run_celery_test_worker()

    # run browser for selenium tests
    world.browser = Browser()

@after.harvest
def cleanup(server):
    # quit the browser
    world.browser.quit()

    # terminate the celery worker
    try:
        print "Terminating Celery worker..."
        if world.celeryd.returncode is None:
            world.celeryd.kill()
        world.celeryd.wait()
    except:
        raise
    
    # destroy the test database using the DjangoTestSuiteRunner
    world.django_suite.teardown_databases(world.django_suite.old_config)

    # teardown
    teardown_test_environment()
```

Installation
=============

Clone the latest version of ``django-celery-testworker`` from GitHub:

    $ git clone git://github.com/RentMethod/django-celery-testworker.git

You can install it by doing the following,:

    $ tar xvfz django-celery-testworker-0.0.0.tar.gz
    $ cd django-celery-testworker-0.0.0
    # python setup.py install # as root
