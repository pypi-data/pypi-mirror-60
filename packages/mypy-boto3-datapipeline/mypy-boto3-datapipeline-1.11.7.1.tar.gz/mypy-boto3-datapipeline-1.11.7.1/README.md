# mypy-boto3-datapipeline

[![PyPI - mypy-boto3](https://img.shields.io/pypi/v/mypy-boto3.svg?color=blue&style=for-the-badge)](https://pypi.org/project/mypy-boto3)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mypy-boto3.svg?color=blue&style=for-the-badge)](https://pypi.org/project/mypy-boto3)
[![Docs](https://img.shields.io/readthedocs/mypy-boto3.svg?color=blue&style=for-the-badge)](https://mypy-boto3.readthedocs.io/)
[![Coverage](https://img.shields.io/codecov/c/github/vemel/mypy_boto3?style=for-the-badge)](https://codecov.io/gh/vemel/mypy_boto3)

Type annotations for
[boto3.DataPipeline 1.11.7](https://boto3.amazonaws.com/v1/documentation/api/1.11.7/reference/services/datapipeline.html#DataPipeline) service
compatible with [mypy](https://github.com/python/mypy), [VSCode](https://code.visualstudio.com/),
[PyCharm](https://www.jetbrains.com/pycharm/) and other tools.

More information can be found [here](https://vemel.github.io/mypy_boto3/).

- [mypy-boto3-datapipeline](#mypy-boto3-datapipeline)
  - [How to use](#how-to-use)
    - [Type checking](#type-checking)
    - [Code auto-complete](#code-auto-complete)
  - [How it works](#how-it-works)

## How to use

### Type checking

Make sure you have [mypy](https://github.com/python/mypy) installed and activated in your IDE.

Install `boto3-stubs` for `DataPipeline` service.

```bash
python -m pip install boto3-stubs[mypy-boto3-datapipeline]
```

Use `boto3` with `mypy_boto3` in your project and enjoy type checking and auto-complete.

```python
import boto3

from mypy_boto3 import datapipeline
# alternative import if you do not want to install mypy_boto3 package
# import mypy_boto3_datapipeline as datapipeline

# Use this client as usual, now mypy can check if your code is valid.
# Check if your IDE supports function overloads,
# you probably do not need explicit type annotations
# client = boto3.client("datapipeline")
client: datapipeline.DataPipelineClient = boto3.client("datapipeline")

# works for session as well
session = boto3.session.Session(region="us-west-1")
session_client: datapipeline.DataPipelineClient = session.client("datapipeline")


# Paginators need type annotation on creation
describe_objects_paginator: datapipeline.DescribeObjectsPaginator = client.get_paginator("describe_objects")
list_pipelines_paginator: datapipeline.ListPipelinesPaginator = client.get_paginator("list_pipelines")
query_objects_paginator: datapipeline.QueryObjectsPaginator = client.get_paginator("query_objects")
```

## How it works

Fully automated [builder](https://github.com/vemel/mypy_boto3) carefully generates
type annotations for each service, patiently waiting for `boto3` updates. It delivers
a drop-in type annotations for you and makes sure that:

- All available `boto3` services are covered.
- Each public class and method of every `boto3` service gets valid type annotations
  extracted from the documentation (blame `botocore` docs if types are incorrect).
- Type annotations include up-to-date documentation.
- Link to documentation is provided for every method.
- Code is processed by [black](https://github.com/psf/black) for readability.