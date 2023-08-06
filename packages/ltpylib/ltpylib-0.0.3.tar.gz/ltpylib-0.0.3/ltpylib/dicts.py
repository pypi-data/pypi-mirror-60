#!/usr/bin/env python3
# pylint: disable=C0111
from typing import List


def find(key: str, obj: dict) -> List[dict]:
  if isinstance(obj, dict):
    for k, v in obj.items():
      if k == key:
        yield v
      else:
        for res in find(key, v):
          yield res
  elif isinstance(obj, list):
    for d in obj:
      for res in find(key, d):
        yield res

  # for k, v in obj.items():
  #   if k == key:
  #     yield v
  #   elif isinstance(v, dict):
  #     for res in find(key, v):
  #       yield res
  #   elif isinstance(v, list):
  #     for d in v:
  #       for res in find(key, d):
  #         yield res


if __name__ == "__main__":
  import sys

  result = globals()[sys.argv[1]](*sys.argv[2:])
  if result is not None:
    print(result)
