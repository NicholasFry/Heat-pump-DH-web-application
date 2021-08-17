from django.urls import path
from .views import *


# router = DefaultRouter()
# router.register('runsimulation', APIView, basename='runsimulation')

# urlpatterns = router.urls
urlpatterns = [
    path('<int:pk>/', RunSimulation.as_view(), name='home')
]
