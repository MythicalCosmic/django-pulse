from django.urls import re_path

from .consumers.telescope_consumer import TelescopeConsumer

websocket_urlpatterns = [
    re_path(r"ws/telescope/$", TelescopeConsumer.as_asgi()),
]
