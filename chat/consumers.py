# import json

# from channels.generic.websocket import WebsocketConsumer


# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()

#     def disconnect(self, close_code):
#         self.disconnect()

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]
#         print(text_data)
#         self.send(text_data=json.dumps({"message": message}))
# import json

# from asgiref.sync import async_to_sync
# from channels.generic.websocket import WebsocketConsumer


# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         print(11111111111)
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = f"chat_{self.room_name}"
#         print("Group name ", self.room_name)

#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name, self.channel_name
#         )

#         self.accept()

#     def disconnect(self, close_code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name, self.channel_name
#         )

#     # Receive message from WebSocket
#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         # Send message to room group
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name, {"type": "chat.message", "message": message}
#         )

#     # Receive message from room group
#     def chat_message(self, event):
#         message = event["message"]

#         # Send message to WebSocket
#         self.send(text_data=json.dumps({"message": message}))
import json
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, Group
import random

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope['user'].is_authenticated:
            # If user is not authenticated, close the connection or redirect to login page
            # Close the connection
            await self.close()

            # Or Redirect to login page
            # login_url = reverse('login')  # Change 'login' to your actual login url name
            # return HttpResponse(status=302, headers={'Location': login_url})

        else:
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            self.room_group_name = f"chat_{self.room_name}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            self.username = await self.get_name()
            self.scope["session"]["seed"] = random.randint(1, 1000)
            self.user = self.scope['user']
            print(str(self.user))
            await self.accept()

    @database_sync_to_async
    def get_name(self):
        user = User.objects.all()[0]
        user.first_name = "admin1"
        user.save()
        return user.first_name

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("1111111", self.room_name)
        message = text_data_json["message"]
        
        group = await self.get_group(self.room_name)
        await self.save_chat_message(message, group)
        
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    @database_sync_to_async
    def get_group(self, room_name):
        return Group.objects.get(name=room_name)

    @database_sync_to_async
    def save_chat_message(self, message, group):
        chat = Chat(content=message, group=group)
        chat.save()

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
