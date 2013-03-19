import os
import subprocess

def run_celery_test_worker(options=[]):
    """
    Starts a celery worker that operates on the test database in the background and 
    waits for it to be ready. Returns process handle.
    """
    import pty, sys
    
    execv_argv = [os.path.abspath(sys.argv[0]), "celerytestworker"] # celerytestworker command defined by celerytests

    # python buffers stdout normally, use pty instead
    master, slave = pty.openpty()
    process = subprocess.Popen(execv_argv + options, stdin=subprocess.PIPE, stdout=slave, stderr=slave, close_fds=True)

    stdout = os.fdopen(master)

    # Wait for the daemon to be ready (it'll print a line with a broker url to stdout)
    # TODO: monitor output of process to detect failure
    output = []
    while process.returncode is None:
        line = stdout.readline()
        output.append(line)

        if "broker" in line: # ready!
            break

    if process.returncode is not None:
        print output
        raise Exception("Celery worker failed to start")


    return process
