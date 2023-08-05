[![pipeline status](https://gitlab.com/pydd/pydd/badges/master/pipeline.svg)](https://gitlab.com/pydd/pydd/commits/master) [![coverage report](https://gitlab.com/pydd/pydd/badges/master/coverage.svg)](https://gitlab.com/pydd/pydd/commits/master) [![PyPI version](https://badge.fury.io/py/MicroPyDD.svg)](https://badge.fury.io/py/MicroPyDD)


# MicroPyDD

MicroPyDD is a simple framework that has the intention of providing a modularized set of preconfigured components that helps you to build microservices in python. PyDD Commons offers basic microservice configuration so you do not need to start everything from scratch. This modules preconfigures:

* Configuration
* Logging
* Module system

## Installing

Install using pip:

```pip install micropydd```

## A Simple Example

```python
from micropydd.module import init

init({}, modules_init_functions=[
    # list additional modules
])
```

