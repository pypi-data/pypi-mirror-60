# dbreak-redis
A plugin for [dbreak](https://github.com/jrhege/dbreak) that allows it to work with [Redis](https://pypi.org/project/redis) objects.

## Installation
Install from PyPi using pip:

```
pip install dbreak-redis
```

## Usage
There's no need to import the plugin separately, just pass a [Redis](https://pypi.org/project/redis) object to dbreak.show_console().

```
import redis
import dbreak

# Set up a localhost Redis connection
# This assumes you've got a Redis database running
connection = redis.Redis()

# Pause execution and enter the console
dbreak.start_console(connection)
```

You can use most valid Redis commands:

```
db[0]> set mykey myvalue

True

db[0]> get mykey

b'myvalue'
```

Use single or double quotes if you need to set a value with whitespace:

```
db[0]> set mykey "This is my value"

True

db[0]> get mykey

b'This is my value'
```