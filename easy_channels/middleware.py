class ConsumerMiddleware(object):
    def __init__(self, consumer):
        self.consumer = consumer

    async def on_connect(self):
        pass

    async def on_receive(self, json):
        pass
