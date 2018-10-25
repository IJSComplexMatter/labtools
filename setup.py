#import distribute_setup
#distribute_setup.use_setuptools()

# Setuptools Must be installed from Canopy and not by ez_setup...

#import ez_setup
#ez_setup.use_setuptools() 

from setuptools import setup, find_packages

#from distutils.core import setup

#def find_packages():
#    return []
    
import platform
import labtools
import glob,os

packages = find_packages()

docdir = 'doc/build/html'
datafiles = []
for root, dirnames, filenames in os.walk(docdir):
    datafiles.append((root.replace('/build/html', ''),glob.glob(root + "/*.*")))
EXCLUDE_PACKAGES = ['labtools.pixelink']



for p in EXCLUDE_PACKAGES:
    packages.remove(p)

if platform.system() == 'Windows':
    SCRIPTS = ['scripts/labtools_install.py',]#,'scripts/experiment.py']
else:
    SCRIPTS = ['scripts/labtools_install.py',]

setup(name = 'labtools',
      version = labtools.__version__,
      description = 'Labtools is a collection of tools and programs for experimental studies.',
      author = 'Andrej Petelin',
      author_email = 'andrej.petelin@gmail.com',
      #install_requires = ["pyserial",'numpy','matplotlib'],

      packages = packages,
      scripts = SCRIPTS,
      
      entry_points = {
        'console_scripts': [
            'stress-strain = labtools.experiment.stretcher_main:main',
            'pypi_cli = labtools.main:pi_main'
        ],
        'gui_scripts': [
            'pystretch = labtools.experiment.stretcher_app:gui',
            'pysmc = labtools.app:smc_gui',
            'pydsc = labtools.app:dsc_gui',
            'dls = labtools.app:dls_gui',
            'labtools = labtools.app:labtools_gui',
            'pykeithley = labtools.app:keithley_gui',
            'pyrotator = labtools.app:rotator_gui',
            'pyalv = labtools.app:alv_gui',
            'pypi = labtools.app:pi_gui',
            'pypmeter = labtools.app:pmeter_gui'
        ]
    },
      package_data={'labtools.experiment': ['icons/*.*'], 'labtools' : ['dls-splash.png','labtools-splash.png', 'testdata/*.*']},

      data_files=datafiles

      )
