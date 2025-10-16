from django.shortcuts import render

import json, uuid
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.db import transaction
from django.db.models import F
from .models import Pedido, PedidoItem, Inventario

def estado(request, pedido_id:str):
    try:
        p = Pedido.objects.only("pedido_id","estado","updated_at").get(pedido_id=pedido_id)
    except Pedido.DoesNotExist:
        return HttpResponseNotFound()
    return JsonResponse({"pedidoId":p.pedido_id,"estado":p.estado,"ultimaActualizacion":p.updated_at.isoformat()}, status=200)

@csrf_exempt
def crear_orden(request):
    if request.method != "POST": return HttpResponseBadRequest("POST only")
    idem = request.headers.get("Idempotency-Key")
    if not idem: return HttpResponseBadRequest("Missing Idempotency-Key")
    try:
        p = Pedido.objects.get(idempotency_key=idem)
        return JsonResponse({"pedidoId":p.pedido_id,"estado":p.estado}, status=200)
    except Pedido.DoesNotExist:
        pass
    try:
        body = json.loads(request.body or "{}")
        items = body.get("items", [])
        if not items: return HttpResponseBadRequest("Missing items")
        skus = [it["sku"] for it in items]
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")
    with transaction.atomic():
        inv = {r.sku:r for r in Inventario.objects.select_for_update().filter(sku__in=skus)}
        for it in items:
            sku, qty = it["sku"], int(it["cantidad"])
            if sku not in inv: return JsonResponse({"error":f"SKU {sku} no existe"}, status=409)
            if inv[sku].disponible < qty: return JsonResponse({"error":f"Sin stock para {sku}"}, status=409)
        for it in items:
            Inventario.objects.filter(sku=it["sku"]).update(disponible=F("disponible")-int(it["cantidad"]))
        p = Pedido.objects.create(pedido_id=str(uuid.uuid4()), idempotency_key=idem)
        for it in items:
            PedidoItem.objects.create(pedido=p, sku=it["sku"], cantidad=int(it["cantidad"]))
    return JsonResponse({"pedidoId":p.pedido_id,"estado":p.estado}, status=201)

