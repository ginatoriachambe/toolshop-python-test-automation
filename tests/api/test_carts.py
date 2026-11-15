NON_EXISTENT_ID = "01AAAAAAAAAAAAAAAAAAAAAAAA"  # valid ULID format, no such cart


def add_to_cart(api_client, cart_id, product_id, quantity):
    return api_client.post(f"/carts/{cart_id}", json={"product_id": product_id, "quantity": quantity})


def get_cart_item(api_client, cart_id, product_id):
    cart = api_client.get(f"/carts/{cart_id}").json()
    for item in cart["cart_items"]:
        if item["product_id"] == product_id:
            return item
    return None


def test_create_cart_returns_cart_id(api_client):
    response = api_client.post("/carts")

    assert response.status_code == 201
    assert response.json()["id"]


def test_add_product_shows_it_in_cart_with_quantity(api_client, cart_id, product_id):
    response = add_to_cart(api_client, cart_id, product_id, 2)

    assert response.status_code == 200
    item = get_cart_item(api_client, cart_id, product_id)
    assert item is not None
    assert item["quantity"] == 2


def test_adding_same_product_twice_increases_quantity(api_client, cart_id, product_id):
    add_to_cart(api_client, cart_id, product_id, 1)

    response = add_to_cart(api_client, cart_id, product_id, 2)

    assert response.status_code == 200
    assert get_cart_item(api_client, cart_id, product_id)["quantity"] == 3


def test_removing_product_removes_it_from_cart(api_client, cart_id, product_id):
    add_to_cart(api_client, cart_id, product_id, 1)

    response = api_client.delete(f"/carts/{cart_id}/product/{product_id}")

    assert response.status_code == 204
    assert get_cart_item(api_client, cart_id, product_id) is None


def test_get_unknown_cart_returns_404(api_client):
    response = api_client.get(f"/carts/{NON_EXISTENT_ID}")

    assert response.status_code == 404
    assert response.json() == {"message": "Requested item not found"}
