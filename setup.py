from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test
import os


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


version = '0.3'
shortdesc = 'LDAP integration for cone.app'
longdesc = '\n\n'.join([read_file(name) for name in [
    'README.rst',
    'CHANGES.rst',
    'LICENSE.rst'
]])


class Test(test):

    def run_tests(self):
        from cone.ldap import tests
        tests.run_tests()


setup(
    name='cone.ldap',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)'
    ],
    keywords='',
    author='Cone Contributors',
    author_email='dev@conestack.org',
    url='http://github.com/conestack/cone.ldap',
    license='Simplified BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['cone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'node.ext.ldap<2.0.0',
        'cone.ugm<1.1.0',
        'yafowil.widget.array<2.0.0',
        'yafowil.widget.dict<2.0.0',
        'yafowil.yaml<3.0.0'
    ],
    extras_require=dict(
        test=[
            'lxml',
            'yafowil.yaml<3.0.0',
            'zope.testrunner'
        ]
    ),
    tests_require=[
        'lxml',
        'yafowil.yaml<3.0.0',
        'zope.testrunner'
    ],
    cmdclass=dict(test=Test)
)
