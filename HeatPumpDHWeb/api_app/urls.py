from django.urls import path
from django.views.generic.base import TemplateView
from .views import *


# router = DefaultRouter()
# router.register('runsimulation', APIView, basename='runsimulation')

# urlpatterns = router.urls
urlpatterns = [
    path('<int:pk>/', RunSimulation.as_view(), name='home'),
    path('create/', RunSimulation.as_view(), name='create'),
    # path('runsim/', RunSimulation.as_view(), name='runsim'),
]
