# Datak E-commerce Backend

Backend API para e-commerce multi-comercio (multi-tenant por comercio) construido con Django + Django REST Framework.

## Que hace este proyecto

- Expone una API REST para operar varios comercios en una misma base de codigo.
- Maneja catalogo, categorias, clientes, pedidos, cupones y suscripciones.
- Soporta variaciones de producto mediante atributos, opciones y valores (por ejemplo talla/color con stock por combinacion).
- Incluye flujo de pago con MercadoPago y flujo de integracion con Addi (creacion de solicitud y callback/webhook).

## Multi-tenant (varios comercios)

El aislamiento entre comercios se maneja con relacion a `Commerce` en los modelos de dominio (por ejemplo productos, categorias, pedidos, clientes).

Ademas, los viewsets base aplican filtro por comercio usando:

- Header `X-Commerce-Id`, o
- Query param `commerce`

Esto permite operar multiples tiendas desde el mismo backend.

## Variaciones de producto

El modelo de variaciones esta basado en:

- `ProductAttribute` (atributo, ej: Talla)
- `AttributeOption` (opcion, ej: M)
- `AttributeValue` (combinacion para un producto, con stock)

Tambien se almacena informacion de variante seleccionada en items de pedido.

## Pagos: Addi

### Addi

La integracion con Addi esta implementada en endpoints publicos para:

- Crear pago Addi (llamado a autenticacion + online application)
- Recibir callback/webhook de Addi

Variables de entorno asociadas:

- `ADDI_AUTH_API`
- `ADDI_PAYMENT_API`
- `ADDI_WEBHOOK_USERNAME`
- `ADDI_WEBHOOK_PASSWORD`

## Google Cloud App Engine (diseno principal)

El proyecto esta pensado para App Engine:

- Existe `app.yaml` para despliegue en App Engine Standard.
- `main.py` usa `google.appengine.api.wrap_wsgi_app`.
- Dependencia `appengine-python-standard` incluida.

Aun asi, se puede adaptar facilmente a otros entornos (por ejemplo Cloud Run, VM o contenedores) usando la app WSGI/ASGI de Django y ajustando configuracion de entorno.

## Archivos y media (Google Cloud Storage)

La gestion de archivos esta orientada a Google Cloud Storage mediante `django-storages` y backend GCS.

Variables relacionadas:

- `GS_PROJECT_ID`
- `GS_BUCKET_NAME`

Tambien es facil de cambiar: basta ajustar `STORAGES` para usar otro backend de almacenamiento (local, S3 compatible, etc.).

## Variables de entorno principales

Usa archivos de ejemplo como referencia y coloca valores reales solo en secretos locales/CI:

- `DJANGO_SECRET_KEY`
- `DATABASE_URL`
- `ENV`
- `APPENGINE_URL`
- `FRONTEND_URL`
- `GS_PROJECT_ID`
- `GS_BUCKET_NAME`
- `ADDI_AUTH_API`
- `ADDI_PAYMENT_API`
- `ADDI_WEBHOOK_USERNAME`
- `ADDI_WEBHOOK_PASSWORD`

## Desarrollo local rapido

1. Crear entorno virtual e instalar dependencias.
2. Definir variables en `.env`.
3. Ejecutar migraciones.
4. Levantar servidor Django.

Comandos sugeridos:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API docs

La API expone esquema/documentacion Swagger en rutas raiz del servicio:

- `/` (UI)
- `/openapi` (schema)
