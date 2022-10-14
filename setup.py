"""Setup script.
"""
import os
import setuptools


class Packaging(setuptools.Command):
    """Common PyPI packaging tools.

    """
    user_options = []
    def initialize_options(self):
        """Dummy override.
        """

    def finalize_options(self):
        """Dummy override.
        """

    def run(self): #pylint: disable=no-self-use
        """Clean up temporary package build files.

        """
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')

PROD_PACKAGES = [
    'dagsesh @ git+https://github.com/loum/dagsesh.git@main#egg=dagsesh',
    'diffit @ git+https://github.com/loum/diffit.git@main#egg=diffit',
    'filester',
    'msal',
    'pyspark==3.3.*',
]

DEV_PACKAGES = [
    'Sphinx',
    'apache-airflow==2.4.*',
    'pipdeptree',
    'pylint',
    'pytest',
    'pytest-cov',
    'pytest-sugar',
    'sphinx-adc-theme',
    'twine',
]

PACKAGES = list(PROD_PACKAGES)
if (os.environ.get('APP_ENV') and 'local' in os.environ.get('APP_ENV')):
    PACKAGES.extend(DEV_PACKAGES)

SETUP_KWARGS = {
    'name': 'dagster',
    'version': os.environ.get('MAKESTER__RELEASE_VERSION', '0.1.0'),
    'description': 'Workflow management primer for Apache Airflow',
    'author': 'Lou Markovski',
    'author_email': 'lou.markovski@gmail.com',
    'url': 'https://github.com/loum/dagster',
    'install_requires': PACKAGES,
    'package_dir': {'': 'src'},
    'packages': setuptools.find_namespace_packages(where='src'),
    'package_data': {
        'dagster.config': [
            'connections/*.json',
            'dags/*.j2',
            'tasks/*.j2',
            'templates/*.j2',
            'templates/webserver/*.j2',
        ],
        'dagster.dags': [
            '.airflowignore',
        ],
    },
    'scripts': ['src/bin/airflow-webserver'],
    'include_package_data': True,
    'license': 'MIT',
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    'cmdclass': {'clean': Packaging},
}

setuptools.setup(**SETUP_KWARGS)
