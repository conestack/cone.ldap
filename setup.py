from setuptools import find_packages
from setuptools import setup
import os


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


version = '0.1'
shortdesc = 'LDAP integration for cone.app'
longdesc = '\n\n'.join([read_file(name) for name in [
    'README.rst',
    'CHANGES.rst',
    'LICENSE.rst'
]])


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
    author='Robert Niederreiter',
    author_email='dev@bluedynamics.com',
    url=u'http://github.com/bluedynamics/cone.ldap',
    license='Simplified BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['cone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'node.ext.ldap',
        'cone.ugm',
        'yafowil.widget.array',
        'yafowil.widget.dict',
        'yafowil.yaml'
    ],
    extras_require=dict(
        test=[
            'cone.app[test]',
            'cone.ugm[test]'
        ]
    )
)
