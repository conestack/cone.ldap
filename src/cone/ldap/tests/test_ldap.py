from cone.ldap.testing import ldap_layer
import doctest
import interlude
import pprint
import unittest


DOCFILES = [
    'model/settings.rst',
    'model/utils.rst',
    'browser/__init__.rst',
    'browser/utils.rst',
    'browser/settings.rst'
]


optionflags = (
    doctest.NORMALIZE_WHITESPACE |
    doctest.ELLIPSIS |
    doctest.REPORT_ONLY_FIRST_FAILURE
)


print """
*******************************************************************************
If testing while development fails, please check if memcached is installed and
stop it if running.
*******************************************************************************
"""


def test_suite():
    suite = unittest.TestSuite()
    suite.layer = ldap_layer
    globs = {
        'interact': interlude.interact,
        'pprint': pprint.pprint,
        'pp': pprint.pprint,
        'layer': ldap_layer
    }
    suite.addTests([
        doctest.DocFileSuite(
            docfile,
            globs=globs,
            optionflags=optionflags
        )
        for docfile in DOCFILES
    ])
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
