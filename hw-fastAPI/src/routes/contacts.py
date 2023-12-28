from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import contacts as rep_contacts
from src.entity.models import User, Role
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponseSchema
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix='/contacts', tags=['contacts'])

# Цей функтор буде пропускати тiльки тi запити, ролi в користувачiв яких спiвпадають
access_elevated = RoleAccess([Role.admin, Role.moderator])


@router.get("/", response_model=list[ContactResponseSchema], description="No more than 10 requests per minute",
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                    db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contact = await rep_contacts.get_contacts(limit, offset, db, user)
    return contact



@router.get("/all", response_model=list[ContactResponseSchema], dependencies=[Depends(access_elevated)])
async def get_contacts_all(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                    db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contact = await rep_contacts.get_contacts_all(limit, offset, db)
    return contact


@router.get("/{contact_id}", response_model=ContactResponseSchema, description="No more than 10 requests per minute",
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    contact = await rep_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ENTITY NOT FOUND.")
    return contact


@router.post("/", response_model=ContactResponseSchema, status_code=status.HTTP_201_CREATED,
             description="No more than 3 injections per minute", dependencies=[Depends(RateLimiter(times=3, seconds=60))])
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await rep_contacts.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}", description="No more than 5 requests per minute",
            dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def update_contact(body: ContactSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await rep_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ENTITY NOT FOUND.")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, description="No more than 3 graveyards per minute",
            dependencies=[Depends(RateLimiter(times=3, seconds=60))])
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await rep_contacts.delete_contact(contact_id, db, user)
    return contact
