# Easy Channels

Lightweight framework for quickly making socket consumers using Django and DjangoChannels.

## Installing

Make sure Django Channels is installed and configured.
You can follow a tutorial for Django Channels <a href="https://channels.readthedocs.io/en/latest/tutorial/part_1.html">here</a>.

```bash
pip install django-easy-channels
```

## Socket Example

### Backend

```python
from easy_channels import JSONConsumer


class ChatConsumer(JSONConsumer):
    # Socket connects
    def on_connect(self):
        # gets name from url
        self.name = self.scope['url_route']['kwargs']['name']

        # Adds socket and consumer to group chatroom
        self.group_add('chatroom')

        # Accepts socket connection
        self.accept()

    # Socket disconnects
    def on_disconnect(self):
        print(f"User {self.name} disconnected")

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
    event: "broadcast_message", // Calls "on_broadcast_message()" function in consumer
    message: "Hello World!", // Can be acessed in bachend using event['message']
  })
);
```

## Adding to Route

This JSONConsumer can be added to Django Channels route in the same way of the original consumers.

```python
from django.urls import re_path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing


from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'^/chat/(?P<name>\w+)/', consumers.ChatConsumer),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

```

## Communicating Between Consumers

Sometimes you want your consumers to talk with each other without sending data to the front end.

For example, we can make a consumer B notify a consumer A that it needs to update its frontend information without this confidental data passing through consumer B.

```python
class ConsumerA(JSONConsumer):
    def on_connect(self):
        self.group_add('groupA')

    def on_notify(self):
        sensitive_data = get_some_data()
        self.group_send(
            'groupA',
            'notify',
            sensitive_data
        )

class ConsumerB(JSONConsumer):
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
from easy_channels.middleware import ConsumerMiddleware

class UserGatherMiddleware(ConsumerMiddleware):

    # Called before the consumer's 'on_connect()'
    def on_connect(self):
        # This middleware has complete access to the consumer in the self.consumer attribute
        self.consumer.name = self.scope['url_route']['kwargs']['name']

    # Called everytime a message is received whatever the event
    def on_receive(self, event):
        print(event['event']) # Prints event name

```

To the middleware to work with the consumer we must pass it.

```python
class ChatConsumer(JSONConsumer):
    middlewares = [UserGatherMiddleware]

    def on_connect(self):
        print(self.name) # Will print the user name
    ...
```
