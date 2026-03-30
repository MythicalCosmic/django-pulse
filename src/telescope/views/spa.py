from django.shortcuts import render
from django.views import View

from ..settings import get_config


class TelescopeSpaView(View):
    """Serves the Vue SPA shell."""

    def get(self, request, path=""):
        auth_callback = get_config("AUTHORIZATION")
        if auth_callback and callable(auth_callback):
            if not auth_callback(request):
                from django.http import HttpResponseForbidden

                return HttpResponseForbidden("Unauthorized")
        else:
            from django.conf import settings

            if not getattr(settings, "DEBUG", False):
                from django.http import HttpResponseForbidden

                return HttpResponseForbidden("Telescope is only available in DEBUG mode")

        return render(request, "telescope/index.html", {
            "telescope_path": get_config("PATH"),
        })
