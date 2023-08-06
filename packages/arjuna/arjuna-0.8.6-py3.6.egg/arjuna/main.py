import os
import sys
import time

def main(*args):
    print("Executing Arjuna command line with args: {}".format(*args))
    try:
        import signal
        import sys
        def signal_handler(sig, frame):
                print('Exiting...')
                sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)
        from arjuna import ArjunFacade
        facade = ArjunFacade()
        facade.launch(args and args or sys.argv)
    except Exception as e:
        # The following sleep is to accommodate a common IDE issue of
        # interspersing main exception with console output.
        time.sleep(0.5)
        msg = '''
    {0}
    Sorry. Looks like this is an error Arjuna couldn't handle.
    Create a bug report on GitHub: https://github.com/rahul-verma/arjuna
    {0}

    Message: {1}
        '''.format("-" * 70, str(e))
        print(msg)
        import traceback
        print(traceback.format_exc())
