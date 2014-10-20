# coding:utf8
class PeonyRouter(object):
    def __init__(self):
        self.APP_LABEL = ['order', ]
        self.DB = 'peony_db'

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.APP_LABEL:
            return self.DB
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.APP_LABEL:
            return self.DB
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label in self.APP_LABEL or \
           obj2._meta.app_label in self.APP_LABEL:
           return True
        return None

    def allow_syncdb(self, db, model):
        if db == self.DB:
            return model._meta.app_label in self.APP_LABEL
        elif model._meta.app_label in self.APP_LABEL:
            return False
        return None


