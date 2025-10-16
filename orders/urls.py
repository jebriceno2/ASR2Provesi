from django.urls import path
from .views import estado, crear_orden
urlpatterns = [
  path("estado/<str:pedido_id>/", estado),
  path("ordenes", crear_orden),  # POST
]
