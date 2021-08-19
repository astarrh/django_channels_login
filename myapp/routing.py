from django.urls import path

from myapp import consumers


websocket_urlpatterns = [
    path('ws/user/', consumers.UserConsumer.as_asgi()),
]
