try:
    from setuptools import setup
    import sys
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Corridor Game Libraries',
    'author': 'Anthony LaRocca',
    'url': 'https://github.com/amlarocca/corridor',
    'author_email': 'zensky@gmail.com',
    'version': '0.1',
    #'install_requires': ['apxapi>=1.0'] + ['pyreadline'] if 'win32' in sys.platform else ['readline'],
    'packages': ['Corridor'],
    'name': 'Corridor'
    #'entry_points': {'console_scripts': ['project-management=customer_management.prj_mgmnt:main', 'user-management=customer_management.user_mgmnt:main']}
}

setup(**config)
