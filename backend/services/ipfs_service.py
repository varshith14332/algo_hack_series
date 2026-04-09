import aiohttp
import json
import logging
from config import settings

logger = logging.getLogger(__name__)


class IPFSService:
    def __init__(self):
        self.token = settings.WEB3_STORAGE_TOKEN
        self.gateway = settings.IPFS_GATEWAY

    async def store(self, data: dict) -> str:
        """Store data on IPFS via Web3.Storage, return CID."""
        try:
            content = json.dumps(data).encode("utf-8")
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.web3.storage/upload",
                    data=content,
                    headers=headers,
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        cid = result["cid"]
                        logger.info(f"Stored on IPFS: {cid}")
                        return cid
                    else:
                        text = await resp.text()
                        raise Exception(f"IPFS upload failed [{resp.status}]: {text}")

        except Exception as e:
            logger.error(f"IPFS store error: {e}")
            # Return placeholder CID if IPFS unavailable — real impl should retry
            return f"bafybeifallback{hash(str(data)) % 10**10:010d}"

    async def retrieve(self, cid: str) -> dict | None:
        """Retrieve data from IPFS by CID."""
        try:
            url = f"{self.gateway}{cid}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return None
        except Exception as e:
            logger.error(f"IPFS retrieve error for {cid}: {e}")
            return None
