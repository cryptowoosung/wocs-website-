import asyncio
import aiohttp

WEBHOOK_URL = "https://wocs.app.n8n.cloud/webhook/wocs-flux-complete"

async def test():
    async with aiohttp.ClientSession() as session:
        for scene in range(1, 5):
            payload = {
                "request_id": f"test-scene{scene}",
                "status": "COMPLETED",
                "payload": {
                    "images": [{
                        "url": f"https://example.com/test_scene{scene}.jpg",
                        "width": 1080,
                        "height": 1920
                    }]
                }
            }
            url = f"{WEBHOOK_URL}?row=3&scene={scene}"
            async with session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as r:
                print(f"Scene {scene}: HTTP {r.status}")
            await asyncio.sleep(1)

asyncio.run(test())
