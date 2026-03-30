from django.http import JsonResponse
from django.urls import include, path


def sample_view(request):
    return JsonResponse({"message": "ok"})


def error_view(request):
    raise ValueError("Test error")


urlpatterns = [
    path("telescope/", include("telescope.urls")),
    path("test/", sample_view, name="test"),
    path("error/", error_view, name="error"),
]
