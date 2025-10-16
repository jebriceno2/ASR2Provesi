from django.db import models

class Pedido(models.Model):
    class Estado(models.TextChoices):
        CREADO="CREADO"; PAGADO="PAGADO"; DESPACHADO="DESPACHADO"; ENTREGADO="ENTREGADO"; CANCELADO="CANCELADO"
    pedido_id = models.CharField(max_length=64, unique=True, db_index=True)
    idempotency_key = models.CharField(max_length=64, unique=True, null=True, blank=True)
    estado = models.CharField(max_length=16, choices=Estado.choices, default=Estado.CREADO)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: db_table = "pedidos"

class Inventario(models.Model):
    sku = models.CharField(max_length=64, unique=True, db_index=True)
    disponible = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: db_table = "inventario"

class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    sku = models.CharField(max_length=64)
    cantidad = models.IntegerField()
    class Meta: db_table = "pedido_items"
