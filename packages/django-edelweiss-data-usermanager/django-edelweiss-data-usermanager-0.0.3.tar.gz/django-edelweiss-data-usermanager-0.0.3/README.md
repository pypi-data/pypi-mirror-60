## django-edelweiss-data-usermanager

This is a django appliation to help manage users and user groups for an
[EdelweissData](https://www.edelweissconnect.com/portfolio/edelweissdata) installation. It provides
an admin dashboard creating and editing entites directly into the EdelweissData database.

It is assumed you already have a Edelweiss Data database. The django app will not try to create the
EdelweissData core database tables.

### Installation into your django project

Add this app to your installed apps in your settings.py file:

    INSTALLED_APPS = [
        ....
        'django_edelweiss_data.usermanager',
    ]

You probably want to keep your EdelweissData core tables in a different schema from your django
application files. You might even choose to use a different database. Add a router in your
settings.py file so that django knows to look for the EdelweissData tables in a different location:

        DATABASE_ROUTERS = ['django_edelweiss_data.usermanager.router.Router']

Then configure your DATABASES section with `default` and `edelweiss_datasets` sections. In the
following example, all tables are in the edelweiss database. The EdelweissData core tables are in
the `datasets` schema and the django application tables are in the `django` schema.

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'OPTIONS': {
                'options': '-c search_path=django',
            },
            'NAME': 'edelweiss',
        },
        'edelweiss_datasets': {
            'ENGINE': 'django.db.backends.postgresql',
            'OPTIONS': {
                'options': '-c search_path=datasets',
            },
            'NAME': 'edelweiss',
        }
    }

Connect to your database and create the django schema:

    CREATE SCHEMA IF NOT EXISTS django;

And then run migrations:

    python manager.py migrate usermanager
