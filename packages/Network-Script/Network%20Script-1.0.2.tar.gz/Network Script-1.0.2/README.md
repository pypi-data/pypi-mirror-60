# Installing
To install use the command `python -m pip install Network-Script`.
# Basic Tutorial
## Server
To start off import the `Server` class:
``` python
from netsc import Server
```
Then create a subclass of the `Server` class, defining `bind_addr` and possibly `sock_family`, `sock_type`, and `sock_proto`:
``` python
class MyServer(Server):
    bind_addr = ('', 1920)
```
Then create an instance, define the object it wraps, and accept a connection:
``` python
server = MyServer(wrapped_obj)
server.accept()
```
## Client
To start off import the `Client` class:
``` python
from netsc import Client
```
Then create a subclass of the `Client` class, possibly defining `sock_family`, `sock_type`, and `sock_proto`:
``` python
class MyClient(Client):
    pass
```
Then create an instance, define the object it wraps, and connect to a server:
``` python
client = MyClient(wrapped_obj)
client.connect(('localhost', 1920))
```
## From then
From now on one end can call the `poll` method, and the other end can then call any method and get any attribute of the wrapped class. Note concerning attributes: to get an attribute the attribute must be listed in the `attrs` attribute of the end initiating the attribute get.