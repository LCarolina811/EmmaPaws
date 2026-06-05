# EmmaPaws — Ecommerce de Juguetes para Mascotas

| Código | Nombre | Correo |
|:---|:---|:---|
| 1143875526 | Javier Jose Gaviria Morales | javier.gaviria.5526@miremington.edu.co |
| 1005945264 | Luz Carolina Hernandez Vega | luz.hernandez.5264@miremington.edu.co |

---

## Descripción del Proyecto

**EmmaPaws** es un ecommerce ultra sencillo para la venta de juguetes para mascotas, implementado con arquitectura de microservicios. El proyecto demuestra comunicación entre servicios independientes, uso de distintos tipos de bases de datos y orquestación con Docker.

---

## Arquitectura

```
Frontend (Flask :5000)
    └── API Gateway (FastAPI :8000)
            ├── catalog-service  (:8002) → PostgreSQL  — Catálogo de productos
            ├── orders-service   (:8003) → MongoDB     — Órdenes de compra
            └── reviews-service  (:8004) → PostgreSQL  — Reseñas de productos
```

---

## Objetivos del Seminario

* Diseñar microservicios independientes que se comunican entre sí.
* Implementar API RESTful con FastAPI.
* Utilizar diferentes tipos de bases de datos para cada microservicio.
* Implementar un front-end básico para hacer uso de los microservicios.
* Contenerizar aplicaciones con Docker.
* Orquestar la infraestructura con Docker Compose.

---

## Requisitos Previos

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo.
* Git instalado.

---

## Clonar y Ejecutar el Proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/JavierJGaviria/EmmaPaws.git
cd EmmaPaws
```

### 2. Crear el archivo de variables de entorno

**Linux / macOS:**
```bash
cp _env.example .env
```

**Windows (PowerShell):**
```powershell
Copy-Item _env.example .env
```

> No es necesario modificar el `.env` para ejecutar en local con Docker.

### 3. Levantar todo el stack

```bash
docker-compose up --build
```

> La primera vez tarda unos minutos mientras descarga las imágenes de Python, PostgreSQL y MongoDB.

### 4. Verificar que todos los servicios están corriendo

```bash
docker-compose ps
```

Deberías ver 10 contenedores con estado `Up`. Las bases de datos PostgreSQL aparecen como `(healthy)`.

### 5. Detener el proyecto

```bash
docker-compose down
```

> Para borrar también los datos almacenados en las bases de datos:
> ```bash
> docker-compose down -v
> ```

---

## Probar la Aplicación

### Desde el navegador

| URL | Descripción |
|:---|:---|
| `http://localhost:5000` | Frontend — Catálogo de juguetes |
| `http://localhost:5000/admin/products` | Panel para agregar productos |
| `http://localhost:8000/docs` | Swagger del API Gateway |
| `http://localhost:8002/docs` | Swagger del Catálogo |
| `http://localhost:8003/docs` | Swagger de Órdenes |
| `http://localhost:8004/docs` | Swagger de Reseñas |

### Flujo de prueba sugerido

1. Ir a `http://localhost:5000/admin/products` y agregar un juguete (nombre, precio, categoría, stock).
2. Ir al catálogo `http://localhost:5000` y verificar que el producto aparece.
3. Hacer clic en un producto → **"Ver detalles"** → **"Pedir ahora"**.
4. Ingresar un email y cantidad → confirmar el pedido.
5. Volver al detalle del producto y dejar una reseña con calificación (1–5 estrellas).

### Probar la API directamente (Swagger)

Ir a `http://localhost:8002/docs` y ejecutar:

```
POST /api/v1/products/
{
  "name": "Peluchito Suave",
  "description": "Juguete de tela para perros pequeños",
  "price": 12.99,
  "stock": 30,
  "category": "Peluches"
}
```

---

## Estructura del Proyecto

```
EmmaPaws/
├── frontend/                  # Aplicación web (Flask)
├── api-gateway/               # Enrutador de peticiones (FastAPI)
├── services/
│   ├── authentication/        # Servicio de autenticación (MongoDB)
│   ├── catalog-service/       # Catálogo de productos (PostgreSQL)
│   ├── orders-service/        # Órdenes de compra (MongoDB)
│   └── reviews-service/       # Reseñas de productos (PostgreSQL)
├── docker-compose.yml
├── _env.example
└── .env
```
