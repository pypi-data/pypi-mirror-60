# BaseAPI

Easily create maintainable API clients.

## Rationale

Building other Python based API clients I found that there was a
tendency to end up with a "mega-class", containing most of the
definitions of my API. BaseAPI tries to keep unrelated API concepts
separate, hopefully making for an easier maintenance experience.

## Installation

PyPi is the easiest way to install:

``` bash
pip install base-api
```

## Usage

### Creating a client

Normally the `Client` class is inherited to create your own client
class:

``` python
from baseapi import Client


class MyClient(Client):
    DEFAULT_URL = 'https://my-api.com'
```

Here we've set our default API URL. This can also be set during the
creation of the client:

``` python
client = MyClient(url='https://localhost')
```

### Creating APIs

To populate your client with functions to access your API use
individual API classes. These reflect an isolated part of your overall
API.

As an example, you may have an authorization component to your API. To
add authorization to your client library, you may create a file called
`auth.py`:

``` python
from baseapi.apis import GraphqlApi


class AuthApi(GraphqlApi):
    @GraphqlAPI.expose_method
    def login(self, username, password):
        # TODO
        pass

    @GraphqlAPI.expose_method
    def logout(self):
        # TODO
        pass
```

Once you have this slice of your API ready, you can add it to your
client by specifying it during the client class definition:

``` python
from baseapi import Client


class MyClient(Client):
    DEFAULT_URL = 'https://my-api.com'
    DEFAULT_APIS = (
        'auth',
    )
```

In this case, `auth.py` must be placed in your `PYTHONPATH`, most
likely alongside your client class file.

TODO: More to come...
