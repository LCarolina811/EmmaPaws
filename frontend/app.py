from flask import Flask, render_template, request, redirect, url_for
import os
import requests

app = Flask(__name__)

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")

CATEGORIES = ["Peluches", "Mordedores", "Cuerda", "Electrónicos"]


def gateway(service, path):
    return f"{API_GATEWAY_URL}/api/v1/{service}/api/v1/{path}"


@app.route("/")
def index():
    try:
        response = requests.get(gateway("catalog", "products/"), timeout=5)
        products = response.json()
    except requests.exceptions.RequestException:
        products = []
    return render_template("index.html", title="Catálogo", products=products)


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    try:
        product = requests.get(gateway("catalog", f"products/{product_id}"), timeout=5).json()
    except requests.exceptions.RequestException:
        product = None

    try:
        review_data = requests.get(gateway("reviews", f"reviews/{product_id}"), timeout=5).json()
    except requests.exceptions.RequestException:
        review_data = {"product_id": product_id, "total_reviews": 0, "avg_rating": 0, "reviews": []}

    return render_template("product.html", title=product["name"] if product else "Producto",
                           product=product, review_data=review_data)


@app.route("/product/<int:product_id>/review", methods=["POST"])
def create_review(product_id):
    data = {
        "product_id": product_id,
        "user_email": request.form.get("user_email"),
        "rating": int(request.form.get("rating", 5)),
        "comment": request.form.get("comment"),
    }
    requests.post(gateway("reviews", "reviews/"), json=data, timeout=5)
    return redirect(url_for("product_detail", product_id=product_id))


@app.route("/order/new/<int:product_id>", methods=["GET", "POST"])
def order_new(product_id):
    if request.method == "POST":
        data = {
            "user_email": request.form.get("user_email"),
            "items": [{"product_id": product_id,
                       "quantity": int(request.form.get("quantity", 1))}],
        }
        try:
            requests.post(gateway("orders", "orders/"), json=data, timeout=5)
            return redirect(url_for("order_success"))
        except requests.exceptions.RequestException:
            return render_template("order_new.html", title="Hacer pedido",
                                   product=None, error="Error al crear la orden.")

    try:
        product = requests.get(gateway("catalog", f"products/{product_id}"), timeout=5).json()
    except requests.exceptions.RequestException:
        product = None
    return render_template("order_new.html", title="Hacer pedido", product=product, error=None)


@app.route("/order/success")
def order_success():
    return render_template("order_success.html", title="¡Pedido realizado!")


@app.route("/admin/products", methods=["GET", "POST"])
def admin_products():
    error = None
    if request.method == "POST":
        image_url = request.form.get("image_url", "").strip() or None
        data = {
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "price": float(request.form.get("price", 0)),
            "stock": int(request.form.get("stock", 0)),
            "category": request.form.get("category"),
            "image_url": image_url,
        }
        try:
            requests.post(gateway("catalog", "products/"), json=data, timeout=5)
            return redirect(url_for("admin_products"))
        except requests.exceptions.RequestException:
            error = "Error al conectar con el servicio de catálogo."

    try:
        products = requests.get(gateway("catalog", "products/"), timeout=5).json()
    except requests.exceptions.RequestException:
        products = []

    return render_template("admin_products.html", title="Admin — Productos",
                           products=products, categories=CATEGORIES, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
