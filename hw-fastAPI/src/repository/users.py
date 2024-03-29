from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    statement = select(User).filter_by(email=email)
    user = await db.execute(statement)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    avatar = None
    try:
        gr_avatar = Gravatar(body.email)
        avatar = gr_avatar.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    user.refresh_token = token
    await db.commit()


# async def confirmed_email(email: str, db: AsyncSession) -> None:
#     user = await get_user_by_email(email, db)
#     user.confirmed = True
#     await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    user = await get_user_by_email(email, db)
    
    if user is not None:
        user.confirmed = True
        await db.commit()
        await db.refresh(user)
    else:
        raise ValueError("User not found for email: {}".format(email))
    

# чому тут на прийом не <user>: [User], а <email>: str
# оскiльки ми зiбралися кешувати <user>, то попередня сесiя до БД збереглася як об'єкт [user] з
# певними параметрами, а зараз при iнiцiюваннi нових змiн вже потрiбна iнша сесiя до БД, тому
# як якорь беремо незмiнний парамерт <email>  
async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user