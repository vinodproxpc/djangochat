from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
import datetime
from .models import Message, UserChannel
from django.contrib.auth.models import User

class ChatConsumer(WebsocketConsumer):
    
    def connect(self):
        print("accepting connection")
        self.accept()
        self.person_id = self.scope.get("url_route").get("kwargs").get("id")
        # saving user channels
        try:
            userchannel = UserChannel.objects.get(user=self.scope.get("user"))
            userchannel.channel_name = self.channel_name
            userchannel.save()
        except UserChannel.DoesNotExist:
            UserChannel.objects.create(user=self.scope.get("user"),channel_name=self.channel_name)
       
    def receive(self, text_data=None, bytes_data=None):
        print("Received message:", text_data)
        text_message = json.loads(text_data)
        message_type = text_message.get("type")
        print(message_type)
        other_user = User.objects.get(id=self.person_id)
        if message_type == "text_message":
            message = text_message.get("message")
            date_time = datetime.datetime.now()
            current_date = date_time.date()
            current_time = date_time.time()
            message_data = {
                "from_who" :self.scope.get("user"),
                "to_who" : other_user,
                "message": message,
                "date" : current_date,
                "time" : current_time,
                }
            Message.objects.create(**message_data)
            try:
                other_user_channel = UserChannel.objects.get(user=other_user)
                data = {
                    "type": "receiver_function","message_type":"text","message":message
                }
                async_to_sync(self.channel_layer.send)(other_user_channel.channel_name, data)
            except:
                pass

        elif message_type == "has_been_seen":
            try:
                user_channel = UserChannel.objects.get(user=other_user)
                data = {
                    "type": "receiver_function","message_type":"has_been_seen_by_other_person"
                }
                async_to_sync(self.channel_layer.send)(user_channel.channel_name, data)
                message_have_not_been_seen = Message.objects.filter(from_who=other_user,to_who=self.scope.get("user"),has_been_seen=False)
                message_have_not_been_seen.update(has_been_seen=True)
            except:
                pass

        
        

    def disconnect(self, code):
        print("Disconnected with code:", code)

    def receiver_function(self, event):
        print("receiver event",event)
        data = json.dumps(event)
        self.send(data)
