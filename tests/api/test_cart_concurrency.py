import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from toolshop.api_client import ApiClient

THREADS = 10


def add_one(api_base_url, cart_id, product_id, barrier):
    client = ApiClient(api_base_url)  # each thread owns its own session
    try:
        barrier.wait(timeout=10)  # release all threads at the same moment
        response = client.post(f"/carts/{cart_id}", json={"product_id": product_id, "quantity": 1})
        return response.status_code
    finally:
        client.close()


@pytest.mark.parametrize("run", range(5))
def test_parallel_adds_to_same_cart_keep_every_quantity(run, api_client, api_base_url, cart_id, product_id):
    barrier = threading.Barrier(THREADS)
    with ThreadPoolExecutor(max_workers=THREADS) as pool:
        futures = [pool.submit(add_one, api_base_url, cart_id, product_id, barrier) for _ in range(THREADS)]
        statuses = [future.result() for future in futures]

    assert statuses == [200] * THREADS

    cart = api_client.get(f"/carts/{cart_id}").json()
    quantities = [item["quantity"] for item in cart["cart_items"] if item["product_id"] == product_id]
    assert sum(quantities) == THREADS, f"expected total quantity {THREADS}, got {sum(quantities)}: quantities {quantities}"

    if len(quantities) > 1:
        pytest.xfail(
            f"Bug #14: concurrent adds create duplicate cart lines: "
            f"got {len(quantities)} lines, quantities {quantities}"
        )
