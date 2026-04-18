from channels.generic.websocket import AsyncWebsocketConsumer
import json

class PredictionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = f"user_{self.scope['user'].id}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
    
    async def receive(self, text_data):
        pass
    
    async def prediction_update(self, event):
        await self.send(text_data=json.dumps(event['data']))