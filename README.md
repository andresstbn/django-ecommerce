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
- `main.py` expone la app WSGI de Django (sin APIs propietarias de App Engine; el correo va por SMTP).

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
- `EMAIL_HOST_PASSWORD` (API key SMTP de Resend; `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `DEFAULT_FROM_EMAIL` tienen defaults)

## Imagenes de producto

Al guardar una `ProductImage` se generan dos variantes WebP junto al original (que nunca se modifica):

- `<original>_thumb.webp` (600px, campo `thumbnail`): tarjetas de catalogo y carrito.
- `<original>_medium.webp` (1600px, campo `medium` en la API): detalle de producto y zoom.

Si la generacion falla, la subida no se pierde: se registra el error y el frontend usa el original.
Para regenerar imagenes existentes (idempotente, se puede re-ejecutar):

```bash
python manage.py generate_thumbnails --dry-run
python manage.py generate_thumbnails
```

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

Pruebas (requieren PostgreSQL por `ArrayField`):

```bash
python manage.py test ecommerce
```

## API docs

La API expone esquema/documentacion Swagger en rutas raiz del servicio:

- `/` (UI)
- `/openapi` (schema)
