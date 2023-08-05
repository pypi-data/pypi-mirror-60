from dataclasses import asdict, dataclass
import functools, requests
from typing import Sequence

@dataclass
class ProgressRow:
  num: int = 0
  denom: int = 0
  sort: int = 0
  forecast: str = "" # go server prefers empty to null
  supports: Sequence[str] = ()

def ok_json(inner):
  "decorator to raise_for_status and return ret.json() if not"
  @functools.wraps(inner)
  def outer(*args, **kwargs):
    ret = inner(*args, **kwargs)
    ret.raise_for_status()
    return ret.json()
  return outer

@dataclass
class RestClient:
  "Wrapper for cloudprogress json/rest API"

  svc_acct_key: str
  task_id: str = ""
  addr: str = 'https://cloudprogress.io'
  # note: task_id is empty string rather than null because golang server hates null

  def url(self, tail: str):
    "return a full-resolved URL by attaching a suffix to self.addr"
    return self.addr + tail

  def auth_body(self):
    "common auth / ID fields in all messages"
    return {
      "svc_acct_key": self.svc_acct_key,
      "task_id": self.task_id,
    }

  def create_task(self, meta: dict = {}):
    "Sets self.task_id from response if not already set"
    ret = requests.post(
      self.url("/task/create"),
      json={'meta': meta, **self.auth_body()}
    )
    ret.raise_for_status()
    body = ret.json()
    if not self.task_id:
      self.task_id = body['task_id']
    return body

  @ok_json
  def set_path(self, path: str, patch: ProgressRow):
    return requests.post(
      self.url("/task/merge/task_id"), # note: task_id is taken from body now, not URL, so not formatting here
      json={"path": path, "patch": asdict(patch), **self.auth_body()}
    )

  @ok_json
  def finish(self, active: bool = False):
    return requests.post(
      self.url("/task/finish/task_id"), # task_id param in URI not used
      json={"active": active, **self.auth_body()}
    )
