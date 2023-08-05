import pickle
import json
from abc import ABC, abstractclassmethod, abstractmethod
from typing import Callable, Dict, Iterable, Optional, Type
from uuid import uuid1

from flask import make_response, Response
from flask_apispec import marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from marshmallow import fields

from .schema import JobSchema


class ModelABC(object):
    @abstractclassmethod
    def create(cls, **kwargs) -> Response:
        raise NotImplementedError

    @abstractmethod
    def save(self):
        raise NotImplementedError

    @marshal_with(JobSchema)
    def update(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)

        self.save()
        return self


    @abstractclassmethod
    def get(cls) -> Iterable:
        raise NotImplementedError

    @abstractclassmethod
    def get_by_id(cls, uuid: str):
        raise NotImplementedError

    @abstractclassmethod
    def delete(cls, uuid: str):
        raise NotImplementedError


Model = Type[ModelABC]


class TaskLoggerABC(object):
    @abstractclassmethod
    def save_job(cls, job_data):
        raise NotImplementedError


TaskLogger = Type[TaskLoggerABC]


class TaskManagerABC(object):
    def _create_task(self, uuid, binary_data, handler_uri):
        raise NotImplementedError

    def _enqueue(self, task):
        raise NotImplementedError


TaskManager = Type[TaskManagerABC]


class ResourceABC(MethodResource):
    _default_serializer: Callable = pickle.dumps
    _model: Model = ModelABC
    _task_manager: TaskManager = TaskManagerABC
    _task_router: Dict = dict()

    def _create_task(self, binary_data: bytes, handler_uri: str):
        return self._task_manager._create_task(binary_data, handler_uri)

    def _enqueue(self, task: Dict):
        return self._task_manager._enqueue(task)

    @classmethod
    def register_to_blueprint(cls, blueprint):
        return blueprint.add_url_rule(cls.url, view_func=cls.as_view(cls.endpoint_name))


class JobListResourceABC(ResourceABC):
    url = "/"
    endpoint_name = "joblist_resource_api"

    @marshal_with(JobSchema(many=True))
    def get(self):
        return self._model.get()

    @marshal_with(JobSchema)
    @use_kwargs({"task_type": fields.Str(), "json_data": fields.Str()})
    def post(self, task_type, json_data):
        uuid = uuid1().hex
        serializer = self._task_router.get("serializer") or self._default_serializer
        data = json.loads(json_data)
        data["uuid"] = uuid
        binary_data = serializer(data)
        task = self._create_task(binary_data, self._task_router.get(task_type))
        response = self._enqueue(task)
        job_data = dict(
            task_id=response.name,
            task_type=task_type,
            status="waiting",
            result_path=None,
            uuid=uuid,
        )
        job = self._model.create(**job_data)

        return job, 201


class JobResourceABC(ResourceABC):
    url = "/<uuid>/"
    endpoint_name = "job_resource_api"

    def _get(self, uuid):
        return self._model.get_by_id(uuid)

    @marshal_with(JobSchema)
    def get(self, uuid):
        return self._get(uuid)

    @marshal_with(JobSchema)
    @use_kwargs(JobSchema)
    def put(self, uuid, **kwargs):
        job = self._get(uuid)
        if job is None:
            self._model.create(uuid=uuid, **kwargs)

        else:
            job.update(**kwargs)

        return job, 201

    def delete(self, uuid):
        job = self._get(uuid)
        job.delete()
        return {}, 204
