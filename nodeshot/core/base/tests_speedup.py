import sys

# disable logging during tests
if 'test' in sys.argv:
    import logging
    logging.disable(logging.CRITICAL)

# add support for --time option to measure the time needed to execute each Test Class
if 'test' in sys.argv and '--time' in sys.argv:
    sys.argv.remove('--time')
    import time
    from unittest import TestCase

    @classmethod
    def setUpClass(cls):
        print("\n\033[95m%s.%s started\033[0m" % (cls.__module__, cls.__name__))
        cls.class_start_time = time.time()

    @classmethod
    def tearDownClass(cls):
        print("\n\033[94m%s.%s finished in %.3f seconds\033[0m" % (cls.__module__, cls.__name__, time.time() - cls.class_start_time))

    TestCase.setUpClass = setUpClass
    TestCase.tearDownClass = tearDownClass

    # add support for --detailed option to measure the time needed to execute each test
    if '--detailed' in sys.argv:
        sys.argv.remove('--detailed')

        def setUp(self):
            self.method_start_time = time.time()

        def tearDown(self):
            execution_time = time.time() - self.method_start_time
            if execution_time < 1.5:
                color = "\033[92m"
            elif execution_time < 3.5:
                color = "\033[93m"
            else:
                color = "\033[91m"
            print("\n%s%s executed in %.3f seconds\033[0m" % (color, self._testMethodName, execution_time))

        TestCase.setUp = setUp
        TestCase.tearDown = tearDown
