# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_edelweiss_data',
 'django_edelweiss_data.project',
 'django_edelweiss_data.project.settings',
 'django_edelweiss_data.usermanager']

package_data = \
{'': ['*']}

install_requires = \
['Django>=2.2,<4.0']

setup_kwargs = {
    'name': 'django-edelweiss-data-usermanager',
    'version': '0.0.3',
    'description': 'User management django application for Edelweiss Data',
    'long_description': "## django-edelweiss-data-usermanager\n\nThis is a django appliation to help manage users and user groups for an\n[EdelweissData](https://www.edelweissconnect.com/portfolio/edelweissdata) installation. It provides\nan admin dashboard creating and editing entites directly into the EdelweissData database.\n\nIt is assumed you already have a Edelweiss Data database. The django app will not try to create the\nEdelweissData core database tables.\n\n### Installation into your django project\n\nAdd this app to your installed apps in your settings.py file:\n\n    INSTALLED_APPS = [\n        ....\n        'django_edelweiss_data.usermanager',\n    ]\n\nYou probably want to keep your EdelweissData core tables in a different schema from your django\napplication files. You might even choose to use a different database. Add a router in your\nsettings.py file so that django knows to look for the EdelweissData tables in a different location:\n\n        DATABASE_ROUTERS = ['django_edelweiss_data.usermanager.router.Router']\n\nThen configure your DATABASES section with `default` and `edelweiss_datasets` sections. In the\nfollowing example, all tables are in the edelweiss database. The EdelweissData core tables are in\nthe `datasets` schema and the django application tables are in the `django` schema.\n\n    DATABASES = {\n        'default': {\n            'ENGINE': 'django.db.backends.postgresql',\n            'OPTIONS': {\n                'options': '-c search_path=django',\n            },\n            'NAME': 'edelweiss',\n        },\n        'edelweiss_datasets': {\n            'ENGINE': 'django.db.backends.postgresql',\n            'OPTIONS': {\n                'options': '-c search_path=datasets',\n            },\n            'NAME': 'edelweiss',\n        }\n    }\n\nConnect to your database and create the django schema:\n\n    CREATE SCHEMA IF NOT EXISTS django;\n\nAnd then run migrations:\n\n    python manager.py migrate usermanager\n",
    'author': 'Edelweiss Connect',
    'author_email': 'info@edelweissconnect.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
