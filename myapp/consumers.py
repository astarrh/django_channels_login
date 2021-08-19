import json
from asgiref.sync import async_to_sync
from channels.auth import login
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password


class UserConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['message_type']
        if message_type == 'login':
            username = text_data_json['data']['username']
            password = text_data_json['data']['password']
            user = get_user_model().objects.filter(username=username).first()

            message_data = {
                'message_type': 'login_result',
                'success': False,
            }
            if user and check_password(password, user.password):
                async_to_sync(login)(self.scope, user)
                self.scope["session"].save()

                message_data['success'] = True
                message_data['username'] = user.username

            self.send(text_data=json.dumps(message_data))
