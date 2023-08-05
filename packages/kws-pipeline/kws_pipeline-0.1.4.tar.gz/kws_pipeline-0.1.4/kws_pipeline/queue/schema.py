from marshmallow import Schema, fields

class JobSchema(Schema):
    task_id = fields.Str()
    uuid = fields.Str()
    status = fields.Str()
    result_path = fields.Str()