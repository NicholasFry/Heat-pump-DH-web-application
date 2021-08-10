from django.urls import path
from .views import SimParameters

urlpatterns = [
    path('', SimParameters.as_view(), name='home')
]
