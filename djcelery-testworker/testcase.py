import os
import threading

from django.test import TransactionTestCase
from . import run_celery_test_worker

class CeleryWorkerThread(threading.Thread):
    """
    Thread for running a live celery worker in the background
    """

    def __init__(self):
        self.error = None
        self.is_ready = threading.Event()
        
        super(CeleryWorkerThread, self).__init__()

    def run(self):
        """
        Sets up the celery worker
        """
        try:
            # Start the worker
            self.process = run_celery_test_worker()
            
        except Exception as e:
            # Set the error and fire signal
            import traceback
            traceback.print_exc()
            self.error = e

        # Signal ready and wait for worker process to terminate
        self.is_ready.set()
        self.process.wait()

    def join(self, timeout=None):
        """
        Quits the celery worker
        """
        if hasattr(self, 'process'):
            try:
                self.process.kill()
            except OSError:
                pass

        # Join with main thread
        super(CeleryWorkerThread, self).join(timeout)



class CeleryWorkerTestCase(TransactionTestCase):
    """
    Does basically the same as TransactionTestCase but also launches a live
    celery worker in a separate thread so that we can run feature tests that
    depend on a celery worker being run. 

    Note that it inherits from TransactionTestCase instead of TestCase because
    the threads do not share the same transactions (unless if using in-memory
    sqlite) and each thread needs to commit all their transactions so that the
    other thread can see the changes.
    """

    @classmethod
    def setUpClass(cls):
        cls.worker_thread = CeleryWorkerThread()
        cls.worker_thread.daemon = True
        cls.worker_thread.start()

        # Wait for the worker to be ready
        cls.worker_thread.is_ready.wait()
        if cls.worker_thread.error:
            raise cls.worker_thread.error
        
        super(CeleryWorkerTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        # There may not be a 'server_thread' attribute if setUpClass() for some
        # reasons has raised an exception.
        if hasattr(cls, 'worker_thread'):
            # Terminate the worker's thread
            cls.worker_thread.join(5)

        super(CeleryWorkerTestCase, cls).tearDownClass()