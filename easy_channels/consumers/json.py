import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from oauth2_provider.models import AccessToken


class JSONConsumer(AsyncWebsocketConsumer):
    middlewares = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.middlewares = [middleware(self)
                            for middleware in self.middlewares]

    async def connect(self):
        for middleware in self.middlewares:
            try:
                await middleware.on_connect()
            except Exception as e:
                print("ERROR ON MIDDLEWARE (" + str(middleware) + ") " + str(e))

        try:
            await self.on_connect()
        except Exception as e:
            print("CONNECT ERROR: " + str(e))

    async def disconnect(self, *args, **kwargs):
        if hasattr(self, 'on_disconnect'):
            await self.on_disconnect()

    async def group_add(self, group_name):
        try:
            await self.channel_layer.group_add(
                group_name,
                self.channel_name
            )
        except Exception as e:
            print("GROUP ADD ERROR: " + str(e))

    async def group_call_event(self, group, event, payload={}):
        obj = {"type": "on_" + event}
        obj.update(payload)

        try:
            await self.channel_layer.group_send(group, obj)
        except Exception as e:
            print("ERROR CALLING: " + str(e))

    async def group_send(self, group, event, payload={}):
        obj = {"type": "websocket__call"}
        obj.update(payload)
        obj['event'] = event

        try:
            await self.channel_layer.group_send(group, obj)
        except Exception as e:
            print("ERROR BEFORE SENDING: " + str(e))

    async def websocket__call(self, event):
        try:
            await self.send(text_data=json.dumps(event))
        except Exception as e:
            print("ERROR SENDING: " + str(e))

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        func_name = "on_" + data_json['event']

        for middleware in self.middlewares:
            try:
                await middleware.on_receive(data_json)
            except Exception as e:
                print("ERROR ON MIDDLEWARE (" + str(middleware) + ") " + str(e))

        data_json.pop('event')

        try:
            if hasattr(self, func_name):
                await getattr(self, func_name)(data_json)
        except Exception as e:
            print("ERROR CALLING " + func_name + " " + str(e))
