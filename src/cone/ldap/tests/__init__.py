import sys
import unittest


def test_suite():
    from cone.ldap.tests import test_ldap
    from cone.ldap.tests import test_settings

    from cone.ldap.tests import test_browser_settings

    suite = unittest.TestSuite()

    suite.addTest(unittest.findTestCases(test_ldap))
    suite.addTest(unittest.findTestCases(test_settings))

    suite.addTest(unittest.findTestCases(test_browser_settings))

    return suite


def run_tests():
    from zope.testrunner.runner import Runner

    runner = Runner(found_suites=[test_suite()])
    runner.run()
    sys.exit(int(runner.failed))


if __name__ == '__main__':
    run_tests()
