### Dependency 

```fluent-logger```

### Environment variables

```
APP_NAME = os.getenv('APP_NAME', 'applogger')
ENVIRONMENT = os.getenv('ENVIRONMENT') if os.getenv('ENVIRONMENT') is not None else os.getenv('ENV', 'LOCAL')
REGION = os.getenv('REGION', 'MEX')
TARGET = os.getenv('TARGET')
```

```LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_INFO_FILE = os.getenv('LOG_INFO_FILE') else APP_NAME_info_+TARGET.log , example filename.log
LOG_ERROR_FILE = os.getenv('LOG_ERROR_FILE') else APP_NAME_error+TARGET.log, example filname.log
LOG_HANDLERS = os.getenv('LOG_HANDLERS', 'console, info_file_handler, error_file_handler,fluent_async_handler')
pass a string each handler is separted by ,
```
for local do use 
```
LOG_HANDLERS = os.getenv('LOG_HANDLERS', 'console, info_file_handler, error_file_handler')
```
### Use 

Only once in the any application
```
from bylogger import applogger
applogger.create_logger()
```

When you need logger
```
logger = applogger.get_logger()

```

Logging message , exactly same as logging module of python
```
logger.info()
logger.warning()
```

