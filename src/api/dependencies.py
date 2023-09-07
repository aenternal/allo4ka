from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import Config


async def check_auth(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer),
):
    if credentials.credentials != Config.BEARER:
        raise HTTPException(status_code=401, detail='Not authorized')
    