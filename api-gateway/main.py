from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI(title="EmmaPaws — API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api/v1")

SERVICES = {
    "auth":    os.getenv("AUTH_SERVICE_URL",    "http://auth-service:8001"),
    "catalog": os.getenv("CATALOG_SERVICE_URL", "http://catalog-service:8002"),
    "orders":  os.getenv("ORDERS_SERVICE_URL",  "http://orders-service:8003"),
    "reviews": os.getenv("REVIEWS_SERVICE_URL", "http://reviews-service:8004"),
}


def _forward(method: str, service_name: str, path: str, request: Request, json_body=None):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Servicio '{service_name}' no encontrado.")
    url = f"{SERVICES[service_name]}/{path}"
    try:
        response = requests.request(
            method,
            url,
            params=request.query_params,
            json=json_body,
        )
        response.raise_for_status()
        if response.status_code == 204:
            return {}
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al contactar '{service_name}': {e}")


@router.get("/{service_name}/{path:path}")
async def forward_get(service_name: str, path: str, request: Request):
    return _forward("GET", service_name, path, request)


@router.post("/{service_name}/{path:path}")
async def forward_post(service_name: str, path: str, request: Request):
    body = await request.json()
    return _forward("POST", service_name, path, request, json_body=body)


@router.put("/{service_name}/{path:path}")
async def forward_put(service_name: str, path: str, request: Request):
    body = await request.json()
    return _forward("PUT", service_name, path, request, json_body=body)


@router.delete("/{service_name}/{path:path}")
async def forward_delete(service_name: str, path: str, request: Request):
    return _forward("DELETE", service_name, path, request)


app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "EmmaPaws API Gateway funcionando."}
