#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'cfn-sphere',
        version = '1.0.6',
        description = 'cfn-sphere AWS CloudFormation management cli',
        long_description = 'cfn-sphere - A CLI tool intended to simplify AWS CloudFormation handling.',
        author = 'Marco Hoyer',
        author_email = 'marco_hoyer@gmx.de',
        license = 'APACHE LICENSE, VERSION 2.0',
        url = 'https://github.com/cfn-sphere/cfn-sphere',
        scripts = ['scripts/cf'],
        packages = [
            'cfn_sphere',
            'cfn_sphere.stack_configuration',
            'cfn_sphere.aws',
            'cfn_sphere.template'
        ],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Topic :: System :: Systems Administration'
        ],
        entry_points = {
            'console_scripts': ['cf=cfn_sphere.cli:main']
        },
        data_files = [],
        package_data = {},
        install_requires = [
            'boto3>=1.4.1',
            'click',
            'gitpython',
            'jinja2',
            'jmespath',
            'networkx',
            'prettytable',
            'pyyaml',
            'six'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
