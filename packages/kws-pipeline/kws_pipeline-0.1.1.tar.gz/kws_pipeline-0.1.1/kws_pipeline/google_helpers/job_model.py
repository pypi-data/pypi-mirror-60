from google.cloud import ndb
from flask import make_response

from ..queue.abc import ModelABC


class Job(ModelABC, ndb.Model):
    task_id = ndb.StringProperty()
    task_type = ndb.StringProperty()
    uuid = ndb.StringProperty()
    status = ndb.StringProperty()
    result_path = ndb.StringProperty()

    def save(self):
        super().put()

    @classmethod
    def create(cls, **kwargs):
        job = cls(**kwargs)
        job.put()
        return job

    @classmethod
    def get(cls):
        r = make_response({"name": "coucou"}, 201)
        return [j for j in cls.query()]

    @classmethod
    def get_by_id(cls, uuid):
        return cls.query().filter(cls.uuid == uuid).get()
