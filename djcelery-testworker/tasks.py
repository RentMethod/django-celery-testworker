import celery

@celery.task
def multiply(a, b):
    """
    Simple celery task for testing.
    """
    return a*b