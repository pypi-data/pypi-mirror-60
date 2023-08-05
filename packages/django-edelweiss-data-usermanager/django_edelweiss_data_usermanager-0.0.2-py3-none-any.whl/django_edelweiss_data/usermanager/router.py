class Router(object):
    """Keeps our domain models in a different schema from django's internal tables"""

    def db_for_read(self, model, **hints):
        if model.__module__ == "django_edelweiss_data.usermanager.models":
            return 'edelweiss_datasets'
        return None

    def db_for_write(self, model, **hints):
        if model.__module__ == "django_edelweiss_data.usermanager.models":
            return 'edelweiss_datasets'
        return None
