from dataclasses import dataclass
import logging
from typing import Optional, Sequence
from .rest import ProgressRow, RestClient

@dataclass
class Looper:
  "iteration wrapper"
  client: RestClient
  path: str
  # Actual or best-estimate size of the lop
  denom: int
  # Write every N. Default (i.e. 0) means N = max(1, denom / 10)
  interval: Optional[int] = None
  i: int = 0
  supports: Sequence[str] = ()
  forecast: str = ""
  sort: int = 0

  def __post_init__(self):
    if self.interval is None:
      self.interval = max(1, self.denom // 10)

  def row(self) -> ProgressRow:
    return ProgressRow(self.i, self.denom, self.sort, self.forecast, self.supports)

  def send(self):
    return self.client.set_path(self.path, self.row())

  def __call__(self, iterable):
    "iteration wrapper, see pizza.py for examples"
    self.send()
    for item in iterable:
      # todo: yield instruction as well
      yield item
      # note: this increments *after* so that the last write is len(iterable), not last index
      self.i += 1
      if self.i % self.interval == 0:
        # todo: also add some kind of time-based debouncing
        self.send()
    if self.i != self.denom:
      logging.warning("i != denom after loop for path %s: %d != %d", self.path, self.i, self.denom)
    self.send()
