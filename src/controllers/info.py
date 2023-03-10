from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.dependencies.services import get_services
from src.models import schemas
from src.services import ServiceFactory

router = APIRouter()


@router.get("/system", response_model=schemas.SystemInfo, status_code=http_status.HTTP_200_OK)
async def system(service: ServiceFactory = Depends(get_services)):
    return await service.info.get_system_info()


@router.get("/version", status_code=http_status.HTTP_200_OK)
async def version(details: bool = False, service: ServiceFactory = Depends(get_services)):
    return await service.info.get_version(details=details)


@router.get("/network", response_model=schemas.LANNetworkInfo, status_code=http_status.HTTP_200_OK)
async def internet(service: ServiceFactory = Depends(get_services)):
    return await service.info.get_network_info()
