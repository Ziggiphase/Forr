import asyncio
import httpx

async def run_test():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # 1. Login with the test user we created earlier
        login_data = {
            "username": "testuser@forr.com",
            "password": "securepassword123"
        }
        res = await client.post("/api/v1/auth/login", data=login_data)
        assert res.status_code == 200, f"Login failed: {res.text}"
        access_token = res.json()["access_token"]
        print("Login successful")

        headers = {"Authorization": f"Bearer {access_token}"}

        # 2. Get the test business ID created in Phase 3
        res = await client.get("/api/v1/businesses", headers=headers)
        assert res.status_code == 200, f"List businesses failed: {res.text}"
        businesses = res.json()
        assert len(businesses) >= 1
        business_id = businesses[0]["id"]
        print(f"Using business ID: {business_id}")

        # 3. Create a Product
        product_payload = {
            "name": "Test iPhone",
            "price": 1000.0,
            "description": "Brand new",
            "quantity": 10,
            "category": "Electronics",
            "status": "draft"
        }
        res = await client.post(f"/api/v1/businesses/{business_id}/products", json=product_payload, headers=headers)
        assert res.status_code == 201, f"Product creation failed: {res.text}"
        created_product = res.json()
        print("Product created successfully:", created_product["name"])
        product_id = created_product["id"]

        # 4. List Products
        res = await client.get(f"/api/v1/businesses/{business_id}/products", headers=headers)
        assert res.status_code == 200, f"List products failed: {res.text}"
        products = res.json()
        assert len(products) >= 1
        assert any(p["id"] == product_id for p in products)
        print(f"Products list retrieved successfully, count: {len(products)}")

        # 5. Update Product
        update_payload = {
            "price": 950.0,
            "status": "active"
        }
        res = await client.put(f"/api/v1/businesses/{business_id}/products/{product_id}", json=update_payload, headers=headers)
        assert res.status_code == 200, f"Update product failed: {res.text}"
        updated_product = res.json()
        assert updated_product["price"] == 950.0
        assert updated_product["status"] == "active"
        print("Product updated successfully")

        # 6. Delete Product
        res = await client.delete(f"/api/v1/businesses/{business_id}/products/{product_id}", headers=headers)
        assert res.status_code == 204, f"Delete product failed: {res.text}"
        
        # Verify deletion
        res = await client.get(f"/api/v1/businesses/{business_id}/products", headers=headers)
        products = res.json()
        assert not any(p["id"] == product_id for p in products)
        print("Product deleted successfully")

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_test())
