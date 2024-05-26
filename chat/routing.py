from django.urls import path
from .consumers import ChatConsumer

asgi_urlpatterns = [
    path("websocket/<int:id>/", ChatConsumer.as_asgi()),
]
