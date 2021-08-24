import json
import time

from asgiref.sync import async_to_sync
from channels.auth import login
from django.conf import settings
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from django.utils.http import http_date


class UserConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def get_cookie_value(self):
        session = self.scope['session']
        max_age = session.get_expiry_age()
        expires_time = time.time() + max_age
        expires = http_date(expires_time)

        response = HttpResponse()
        response.set_cookie(
            settings.SESSION_COOKIE_NAME,
            session.session_key,
            max_age=max_age,
            expires=expires,
            domain=settings.SESSION_COOKIE_DOMAIN,
            path=settings.SESSION_COOKIE_PATH,
            secure=settings.SESSION_COOKIE_SECURE or None,
            httponly=settings.SESSION_COOKIE_HTTPONLY or None,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )
        c = response.cookies['sessionid']
        cookie_text = c.output(header="").strip()
        return cookie_text

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
                message_data['sessionid'] = self.scope["session"].session_key
                message_data['session_cookie'] = self.get_cookie_value()

            self.send(text_data=json.dumps(message_data))
