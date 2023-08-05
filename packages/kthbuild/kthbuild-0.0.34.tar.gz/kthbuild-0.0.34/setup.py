#!/usr/bin/env python

# 
# Copyright (c) 2020 Fernando Pelliccioni
# 

from setuptools import setup
from setuptools.command.install import install
import subprocess

__title__ = "kthbuild"
__summary__ = "Knuth node build tools"
__uri__ = "https://github.com/k-nuth/kthbuild"
__version__ = "0.0.34"
__author__ = "Fernando Pelliccioni"
__email__ = "fpelliccioni@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2020 Fernando Pelliccioni"


install_requires = [
    "conan >= 1.21.1",
    "cpuid >= 0.0.9",
]

class PostInstallCommand(install):
    """Override Install
    """

    user_options = install.user_options + [
        ('no-remotes=', None, 'Do not add conan remotes')
    ]

    def initialize_options(self):
        install.initialize_options(self)
        self.no_remotes = False

    def finalize_options(self):
        print('no-remotes option: ', self.no_remotes)
        install.finalize_options(self)

    def run(self):
        """If necessary, create plugin directory, install and change file owner
        :return: None
        """
        install.run(self)
        if not self.no_remotes:
            self.__setup_conan_remote("kthbuild_kth_temp_",     'https://api.bintray.com/conan/k-nuth/kth')
            self.__setup_conan_remote("kthbuild_bitprim_temp_", 'https://api.bintray.com/conan/bitprim/bitprim')
        
    def __setup_conan_remote(self, remote_alias, remote_url):
        try:
            # remote_alias = "kthbuild_kth_temp_"
            # remote_url = 'https://api.bintray.com/conan/k-nuth/kth'
            params = ["conan", "remote", "add", remote_alias, remote_url]
            res = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = res.communicate()
            if output:
                if res.returncode == 0:
                    # return output.decode("utf-8")
                    print("OK in __setup_conan_remote")

            print("Error in __setup_conan_remote 0")
            # return default
        except OSError: # as e:
            print("Error in __setup_conan_remote 1")
            # return default
        except:
            print("Error in __setup_conan_remote 2")
            # return default

setup(
    name = __title__,
    version = __version__,
    description = __summary__,
    long_description=open("./README.rst").read(),
    license = __license__,
    url = __uri__,
    author = __author__,
    author_email = __email__,

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
    ],    

    # What does your project relate to?
    keywords='knuth kth crypto bitcoin btc bch cash build tool',

    py_modules=["kthbuild"],

    install_requires=install_requires,
    # setup_requires=setup_requires,
    

    dependency_links=[
        'https://testpypi.python.org/pypi',
        # 'https://testpypi.python.org/pypi/cpuid-native/',
    ],

    cmdclass={'install': PostInstallCommand},

    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },
)

