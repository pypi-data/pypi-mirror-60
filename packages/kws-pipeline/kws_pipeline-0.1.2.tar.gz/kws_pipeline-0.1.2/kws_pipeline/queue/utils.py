from flask import Flask

from kws_pipeline.queue.abc import JobResourceABC, JobListResourceABC

def register_resources(app, model, task_manager, task_router):
    class JobListResource(JobListResourceABC):
        _model = model
        _task_manager = task_manager
        _task_router = task_router

    class JobResource(JobResourceABC):
        _model = model
        _task_manager = task_manager
        _task_router = task_router

    JobListResource.register_to_blueprint(app)
    JobResource.register_to_blueprint(app)
    return app


def apply_middlewares(app, *middlewares):
    for middleware in middlewares:
        app.wsgi_app = middleware(app.wsgi_app)

    return app

def create_app(job_model, task_manager, task_router, middlewares=tuple()):
    app = Flask(__name__)
    app = register_resources(app, job_model, task_manager, task_router)
    app = apply_middlewares(app, *middlewares)
    return app
