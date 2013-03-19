from testcase import CeleryWorkerTestCase
from tasks import multiply
from random import randrange

import celery
import time

class WorkerRunsTestCase(CeleryWorkerTestCase):

    def test_single_task(self):
        """
        This test requires celery to be running to succeed
        """
        a = randrange(1,10)
        b = randrange(1,10)

        task = multiply.delay(a, b)
        self.assertEqual(task.state, "PENDING")

        assert_eventually_true(lambda: task.state == "SUCCESS", timeout=1)
        self.assertEqual(task.result, a*b)

    def test_multiple_tasks(self):
        expected = []
        tasks = []

        for x in range(10):
            a = randrange(1,10)
            b = randrange(1,10)
            expected.append(a*b)
            tasks.append(multiply.subtask((a,b)))

        group = celery.group(tasks).apply_async()
        assert_eventually_true(lambda: group.completed_count() == 10, timeout=5)

        results = group.join()
        self.assertEqual(results, expected)
        

def assert_eventually_true(eval, timeout=None, delay=0.01):
    """
    Checks if the passed function evaluates to true within the time limit specified by timeout
    """
    t0 = time.time()

    while (True):
        if eval():
            break

        time.sleep(delay)

        if timeout and time.time() - t0 > timeout:
            assert False, "%s still evaluated to false after %f seconds" % (repr(eval), timeout)