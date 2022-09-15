# Logging

This application uses the standard [Python logging library](https://docs.python.org/3/library/logging.config.html) with a few configurational updates in order to be easier to work with.

## Configurations
Log configurations can be found in [logging/__init__.py](/app/api/logging/__init__.py). Sevaral `loggers` are defined which adjust the log level of various libraries we depend on.

### Formatting
We have two separate ways of formatting the logs which are controlled by the `LOG_FORMAT` environment variable.

`json` (default) -> Produces JSON formatted logs which are machine-readable.
```json
{
    "name":"api.route.eligibility",
    "levelname":"INFO",
    "funcName":"eligibility_screener_post",
    "created":"1663187165.382641",
    "thread":"275144058624",
    "threadName":"Thread-2 (process_request_thread)",
    "process":"36",
    "user_id":"69d08484-9693-44cb-bccc-9eb887aff975",
    "eligibility_screener_id":"c3b86cda-7621-4606-a983-bebd99e7252b",
    "message":"Successfully submitted eligibility screener",
    "request.method":"POST",
    "request.path":"/v1/eligibility-screener",
    "request.url_rule":"/v1/eligibility-screener",
    "request_id":"",
    "current_user.user_id":"69d08484-9693-44cb-bccc-9eb887aff975"
}
```

`human-readable` -> Produces log messages with color formatting that are easier to parse.
![Human readable formatting](/docs/app/images/human-readable-logs.png)