from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.track_price_view, name='track_price'),
] 