"""vm106 hosting entrypoint for bryn1/klartx (MC#2317).

The vm106 renderer runs `python server.py` with NO PORT env; nginx proxies
sibbamala.com/klartx/ -> 127.0.0.1:8150. src/main.py only DEFINES the ASGI `app`;
this shim binds the manifest PORT (default 8150) on 0.0.0.0.
"""
import os

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8150"))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port)
