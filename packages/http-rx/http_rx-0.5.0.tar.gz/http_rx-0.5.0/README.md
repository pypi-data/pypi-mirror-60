# HTTP Rx - Your HTTP Doctor

**HTTP Rx** is a simple site/http monitor for your websites and HTTP endpoints. The tool monitors a given list of endpoint configurations and logs errors if the expected health check does not pass.

---

## Installing

This package is available on the Python Package Index (PyPi) and can be installed with pip:  

```
pip install --upgrade http-rx
```

Alternatively, you may clone this repository and install from the source code:  

```
python setup.py install
```

---

## Configuration

HTTP Rx is very dynamic and configurable, inspired by the Java Spring framework, the health checker looks for a `config.json` file in your current directory, or if you specify the `RX_CONFIG` environment variable you can change the path to your config file. 

This JSON config file is structured like so:  

```json
{
  "logLevel": "INFO",
  "report": {
    "interval": 5.0
  },
  "requests": [
    {
      "name": "GitHub Profile",
      "url": "https://github.com/zcking",
      "method": "GET",
      "intervalSeconds": 2.0,
      "checks": [
        {
          "type": "rx.check.StatusCodeCheck",
          "expected": 201
        },
        {
          "type": "rx.check.HeaderCheck",
          "headers": {
            "Content-Type": "text/html"
          }
        }
      ]
    }
  ]
}
```

The `requests` key is a list of http targets to check,
each of which has the following settings:  

* `url`     - the HTTP(s) target to request
* `method`  - the HTTP verb to request with; defaults to `"GET"` 
* `name`    - human-friendly label for the request; defaults to `{method}:{url}`
* `data`    - request body to send; defaults to `None`
* `headers` - request headers to send; defaults to `[]`
* `checks`  - list of health check configurations to perform on the HTTP response

For the check configurations, you must specify the following configuration(s):  

* `type`   - fully qualified Python class; must be a derivative of the `rx.check.Check` base class. Defaults to the `rx.check.StatusCodeCheck` class

The `type` configuration is how you may specify your own custom health check classes when extending http-rx. See the next section on doing just this.

**Note:** the entire check configuration object is passed to the check class's `__init__` method for arbitrary custom configuration. See the built-in health checks in this repository for examples.


---

## Extending

HTTP Rx is setup in a framework manner, allowing you to easily extend it with your own 
custom health checks, written in Python. 

For example:

Create a fresh virtual environment to install the `http-rx` package:  

```
python3 -m virtualenv venv
source venv/bin/activate
pip install http-rx
```

Then simply create your own custom health check that extends HTTP Rx's `Check` base class:  

```python
"""
content.py
"""

import rx
from rx import check


class CheckContentType(check.Check):
    def __init__(self, conf):
        super().__init__(conf)
        self.expected_content_type = conf.get('expected', 'text/html')
    
    def result(self, resp):
        content_type = resp.headers.get('content-type', None)
        healthy = content_type == self.expected_content_type
        return check.Result(
            resp=resp, 
            is_healthy=healthy, 
            fail_reason=f'expected content type of {self.expected_content_type} but received {content_type}'
        )


if __name__ == '__main__':
    rx.run()

```

And your config file to go along with it:  

```json
{
  "report": {
    "interval": 2.0
  },
  "requests": [
    {
      "name": "GitHub Profile",
      "url": "https://github.com/zcking",
      "method": "GET",
      "intervalSeconds": 0,
      "checks": [
        {
          "type": "__main__.CheckContentType",
          "expected": "application/json"
        }
      ]
    }
  ]
}
```

Notice in this simple example that the module name is `__main__` because we're executing it as a script. If you were to write your own Python package with submodules etc. this may not be the case.