import pickle
import inspect
from urllib.parse import urljoin
from functools import wraps

import requests
from flask import Blueprint, request, jsonify
from slugify import slugify


class QueueManager:
    def __init__(self, queue_manager_url):
        self.queue_manager_url = queue_manager_url

    def set_status(self, uuid, **kwargs):
        url = urljoin(self.queue_manager_url, str(uuid))
        r = requests.put(url, data=kwargs)
        return r


class StorageManagerABC:
    def write_to_file(self, uuid, result):
        raise NotImplementedError


class Worker(object):
    def __init__(
        self, worker_prefix="worker", queue_manager=None, storage_manager=None
    ):
        self.worker_prefix = worker_prefix
        self.storage_manager: StorageManagerABC = storage_manager
        self.queue_manager: QueueManager = queue_manager
        self.blueprint = Blueprint("worker", "worker", url_prefix=f"/{worker_prefix}/")
        self.capabilities = set()

    def register_slug(self, name):
        slug = slugify(name)
        self.capabilities.add(slug)
        return f"/{slug}/"

    def build_documentation(self, func):
        sig = inspect.signature(func)
        doc = {"docstring": func.__doc__, "parameters": []}
        params = doc["parameters"]
        for name, param in sig.parameters.items():
            param_doc = {}
            if param.annotation is not param.empty:
                param_doc["type"] = str(param.annotation)
            if param.default is not param.empty:
                param_doc["default"] = param.default
            params.append({name: param_doc})

        return doc

    def init_task(self, status="pending"):
        payload = pickle.loads(request.get_data())
        uuid = payload.pop("uuid")
        resp = self.queue_manager.set_status(uuid, status=status)
        return uuid, payload

    def post_task(self, uuid, result, status="done"):
        result_path = self.storage_manager.write_to_file(uuid, result)
        resp = self.queue_manager.set_status(
            uuid, result_path=result_path, status=status
        )
        return result_path

    def capability(self, func):
        slug = slugify(func.__name__)
        route = self.register_slug(func.__name__)

        def wrapped_function():
            uuid, payload = self.init_task()
            result = func(**payload)
            result_path = self.post_task(uuid, result)
            return jsonify({"result_path": result_path}), 200

        def wrapped_doc():
            doc = self.build_documentation(func)
            return jsonify(doc), 200

        wrapped_function.__name__ = f"{slug}_worker"
        wrapped_doc.__name__ = f"{slug}_doc"
        self.blueprint.route(route, methods=("POST",))(wrapped_function)
        self.blueprint.route(route, methods=("GET",))(wrapped_doc)
        return func

    def pipeline(self, pipeline_name, *funcs):
        slug = slugify(pipeline_name)
        route = self.register_slug(pipeline_name)

        def unrolled(*args, **kwargs):
            func = funcs[0]
            result = func(*args, **kwargs)
            for func in funcs[1:]:
                result = func(result)

            return result

        def wrapped_pipeline():
            pending_template = "pending: %s"
            func = funcs[0]
            uuid, payload = self.init_task(status=pending_template % func.__name__)
            result = func(**payload)
            for func in funcs[1:]:
                self.queue_manager.set_status(
                    uuid, status=pending_template % func.__name__
                )
                result = func(result)

            result_path = self.post_task(uuid, result)
            return jsonify({"result_path": result_path}), 200

        def wrapped_doc():
            docs = [self.build_documentation(func) for func in funcs]
            return jsonify(docs), 200

        wrapped_pipeline.__name__ = f"{slug}-worker"
        wrapped_doc.__name__ = f"{slug}-doc"

        self.blueprint.route(route, methods=("POST",))(wrapped_pipeline)
        self.blueprint.route(route, methods=("GET",))(wrapped_doc)

        return unrolled

    def register(self, app):
        app.register_blueprint(self.blueprint)

    def build_router(self):
        router = dict()
        for capability in self.capabilities:
            router[capability] = f"/{self.worker_prefix}/{capability}"

        return router
