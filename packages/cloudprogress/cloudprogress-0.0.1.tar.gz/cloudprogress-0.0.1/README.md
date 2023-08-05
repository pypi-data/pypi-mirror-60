# cpr-py

This is the python client for the Cloud Progress rest API. [Cloud Progress](https://cloudprogress.io) is a hosted developer tool that provides progress bars with ETA for structured tasks.

The swagger / openapi spec for this api is hosted [as a browseable redoc page](https://cloudprogress.io/static/redoc.htm) and in our API repo https://github.com/cloudprogress/cpr-api. The API repo has links to clients in other languages.

This package targets python 3.7+ to get dataclass support -- if your app targets an older version, post a github issue and we'll make it happen.

## Installation

```sh
pip install ...
# or if you like to live on the edge:
pip install https://github.com/cloudprogress/cpr-py/archive/master.zip
```

## Example

Check out [pizza.py](pizza.py) in this repo 🍕 (it's even runnable).

## Ops concerns

### Timeouts

### Error handling
