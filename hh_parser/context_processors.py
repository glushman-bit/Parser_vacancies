from django.conf import settings


def build_number(request):
    return {
        "BUILD_NUMBER": settings.BUILD_NUMBER,
    }