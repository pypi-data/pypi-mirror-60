import json

import requests

url = "http://localhost:5000/"
data = dict(num_rows=1000, headers=list("abcdefghijklmnopqrstuvwxyz"))
payload = dict(task_type="write-pandas-df", json_data=json.dumps(data))
r = requests.post(url, data=payload)