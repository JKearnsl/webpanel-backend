from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi import status as http_status

from src.dependencies.services import get_services
from src.models import schemas
from src.services import ServiceFactory
from src.views import UserBigResponse

router = APIRouter()  # todo: move to app.py


@router.put("/create_start_user", status_code=http_status.HTTP_201_CREATED)
async def sign_up(user: schemas.UserSignUp, service: ServiceFactory = Depends(get_services)):
    await service.initial.create_start_user(user)


@router.post("/ping", status_code=http_status.HTTP_200_OK)
async def ping():
    return 'pong'
