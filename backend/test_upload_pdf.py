import asyncio
import httpx
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table

async def run_test():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # 1. Login
        login_data = {
            "username": "testuser@forr.com",
            "password": "securepassword123"
        }
        res = await client.post("/api/v1/auth/login", data=login_data)
        assert res.status_code == 200, f"Login failed: {res.text}"
        access_token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # 2. Get business ID
        res = await client.get("/api/v1/businesses", headers=headers)
        assert res.status_code == 200
        businesses = res.json()
        assert len(businesses) >= 1
        business_id = businesses[0]["id"]

        # 3. Create dummy PDF with a table
        pdf_path = "test_data.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        data = [
            ["PDFItem", "PDFCost", "PDFDetails"],
            ["PDF Laptop", "2000", "A nice laptop"],
            ["PDF Phone", "1000", "A nice phone"]
        ]
        from reportlab.platypus import TableStyle
        from reportlab.lib import colors
        t = Table(data)
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements = [t]
        doc.build(elements)

        # 4. Upload and Parse
        with open(pdf_path, "rb") as f:
            files = {"file": ("test_data.pdf", f, "application/pdf")}
            res = await client.post(
                f"/api/v1/businesses/{business_id}/products/upload/parse",
                headers=headers,
                files=files
            )
        assert res.status_code == 200, f"Parse failed: {res.text}"
        parse_data = res.json()
        assert "PDFItem" in parse_data["headers"]
        assert len(parse_data["data"]) == 2
        print("PDF parsed successfully!")

        # 5. Send Bulk Request (Mapped)
        mapped_payload = []
        for row in parse_data["data"]:
            mapped_payload.append({
                "name": row["PDFItem"],
                "price": float(row["PDFCost"]),
                "description": row["PDFDetails"],
                "quantity": 0,
                "category": "Electronics",
                "status": "draft"
            })
        
        res = await client.post(
            f"/api/v1/businesses/{business_id}/products/bulk",
            headers=headers,
            json=mapped_payload
        )
        assert res.status_code == 201, f"Bulk insert failed: {res.text}"
        print("PDF Bulk insert successful!")

        # Cleanup
        os.remove(pdf_path)

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_test())
