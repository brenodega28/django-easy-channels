# Django Easy Channels

Simple framework for making socket consumers using Django Channels.

It's made to work a little like SocketIO using events.

## Installing

```bash
pip install django-easy-channels
```

## Socket Example

### Backend

```python
from easy_channels import JSONWebSocket


class ChatConsumer(JSONWebSocket):
    # Socket connects
    def on_connect(self):
        # gets name from url
        self.name = self.scope['url_route']['kwargs']['name']

        # Adds socket and consumer to group chatroom
        self.group_add('chatroom')

        # Accepts socket connection
        self.accept()

    # Called when consumer receives a message with the event broadcast_message
    def on_broadcast_message(self, event):
        payload = {
            'message': event['message'],
            'from': self.name
        }

        # Sends this message to all connected sockets in the 'chatroom' group (not consumers)
        await self.group_send(
            'chatroom', # group
            'message', # event name
            payload # data
        )
```

### Frontend

```js
const messages = [];
const socket = new WebSocket("wss://YOUR_URL/chat/joselito");

// Called when socket receives a message
socket.onmessage = function (message) {
  switch (message.event) {
    case "message":
      messages.push({
        message: message.message,
        from: message.from,
      });
  }
};

socket.send(
  JSON.stringify({
    event: "broadcast_message", // Calls "on_broadcast()" function in consumer
    message: "Hello World!", // Can be acessed in bachend using event['message']
  })
);
```

## Adding to Route

This JSONWebSocket can be added to Django Channels route in the same way of the original consumers.

```python
from django.urls import re_path

from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<name>\w+)/', consumers.ChatConsumer),
]

```

## Communicating Between Consumers

Sometimes you want your consumers to talk with each other without sending data to the front end.

For example, we can make a consumer A notify a consumer B that it needs to update its frontend information without this confidental data passing through consumer A.

```python
class ConsumerA(JSONWebSocket):
    def on_connect(self):
        self.group_add('groupA')

    def on_notify(self):
        sensitive_data = get_some_data()
        self.group_send(
            'groupA',
            'notify',
            sensitive_data
        )

class ConsumerB(JSONWebSocket):
    def on_connect(self):
        self.group_add('groupB')

    def on_some_event(self):
        # Calls 'on_notify()' in all consumers added to groupA
        self.group_call_event(
            'groupA',
            'notify'
        )
```

## Middleware Example

You can create custom middlewares that will be run before the on_connect function or whenever a message is received.

The code below will automatically gather the chat user name from url.

```python
from easy_channels import SocketMiddleware

class UserGatherMiddleware(SocketMiddleware):

    # Called before the consumer's 'on_connect()'
    def on_connect(self):
        # This middleware has complete access to the consumer in the self.consumer attribute
        self.consumer.name = self.scope['url_route']['kwargs']['name']
```

To the middleware to work with the consumer we must pass it.

```python
class ChatConsumer(JSONWebSocket):
    middlewares = [UserGatherMiddleware]

    def on_connect(self):
        print(self.name) # Will print the user name
    ...
```
