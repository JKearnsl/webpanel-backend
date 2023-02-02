
from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from pydantic.error_wrappers import ErrorWrapper

from src.dependencies.services import get_services
from src.models import schemas
from src.services import ServiceFactory


from src.views.user import UserSmallResponse
from src.views.user import UserBigResponse
from src.utils.validators import is_int64

router = APIRouter()  # todo: сделать нормально ошибку в одном мете


@router.get("/current", response_model=UserBigResponse)
async def get_current_user(services: ServiceFactory = Depends(get_services)):
    return await services.user.get_me()


@router.get("/{user_id}", response_model=UserSmallResponse | UserBigResponse)
async def get_user(user_id: int, services: ServiceFactory = Depends(get_services)):
    if not is_int64(user_id):
        raise RequestValidationError(
            errors=[ErrorWrapper(ValueError("user_id is not int64"), loc=('path', 'user_id'),), ]
        )
    return await services.user.get_user(user_id)


@router.post("/update", response_model=None)
async def update_user(data: schemas.UserUpdate, services: ServiceFactory = Depends(get_services)):
    await services.user.update_me(**data.dict(exclude_unset=True))


@router.delete("/delete", response_model=None, status_code=204)
async def delete_user(user_id: int, services: ServiceFactory = Depends(get_services)):
    await services.user.delete_user(user_id)
