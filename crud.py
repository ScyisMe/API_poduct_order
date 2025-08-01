import asyncio
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, User, Profile, Post, Order, Product

async def create_user(session: AsyncSession, username: str) -> User:
    user = User(username=username)
    session.add(user)
    await session.commit()
    print("user", user)
    return user

async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    result: Result = await session.execute(stmt)
    user: User | None = result.scalar_one_or_none()
    print("found user", username, user)
    return user

async def create_profile(session: AsyncSession, user_id: int,
                         first_name: str | None = None,
                         last_name: str | None = None,
                         bio: str | None = None,
                         ) -> Profile:
    profile = Profile(
                    user_id=user_id,
                    first_name=first_name,
                    last_name=last_name, bio=bio,
                      )
    session.add(profile)
    await session.commit()
    return profile

async def get_profile_by_username(session: AsyncSession) -> list[User]:
    stmt = select(User).options(joinedload(User.profile)).order_by(User.id)
    # result: Result =  await session.execute(stmt)
    # users = await session.scalars(result)
    users = await session.scalars(stmt)
    for user in users:
        print(user)

async def create_posts(
                    session: AsyncSession,
                    user_id: int,
                    *post_title: str,
                    ) -> list[Post]:
    posts = [
        Post(title=title, user_id=user_id)
        for title in post_title
    ]
    session.execute(posts)
    await session.commit()
    print(posts)
    return posts

async def get_user_with_post_and_profiles(
    session: AsyncSession,
    ):
    stmt = select(User).options(
        joinedload(User.profile),
        selectinload(User.posts)
        ).order_by(User.id)
    
    result = await session.execute(stmt)
    # users = result.unique().scalars().all()
    users = result.scalars().all()
    
    for user in users:
        print("***")
        print(user, user.profile and user.profile.first_name)
        for post in user.posts:
            print("-", post)

async def get_user_with_post(
    session: AsyncSession,
    ):
    #stmt = select(User).options(joinedload(User.posts)).order_by(User.id)
    stmt = select(User).options(
        # joinedload(User.posts)
        selectinload(User.posts)
        ).order_by(User.id)
    result = await session.execute(stmt)
    # users = result.unique().scalars().all()
    users = result.scalars().all()
    
    for user in users:
        print("***")
        print(user)
        for post in user.posts:
            print("-", post)
            
async def get_post_with_authors(
    session: AsyncSession,
):
    stmt = select(Post).options(joinedload(Post.user)).order_by(Post.id)
    posts = await session.scalars(stmt)
    
    for post in posts:
        print("post",post)
        print("autor", post.user)
        
async def get_profiles_with_users_and_users_with_profiles(session: AsyncSession):
    stmt = (
        select(Profile) 
        .options(
            joinedload(Profile.user).selectinload(User.posts),
        )
        .order_by(Profile.id)
    )
    profiles = await session.scalars(stmt)
    
    for profile in profiles:
        print(profile.first_name, profile.user)
        print(profile.user.posts)
        
async def main_relation(session: AsyncSession):
        # await create_user(session=session, username="alias")
        # user_tolik = await get_user_by_username(session=session, username="tolik")
        # user_vanya = await get_user_by_username(session=session, username="Vanya")
        # # await create_profile(
        # #     session=session,
        # #     user_id=user_vanya.id,
        #     first_name="Vanya",
        #     last_name="Geordiy",
        # )
        # await get_profile_by_username(session=session)
        # await create_posts(
        #     session,
        #     user_vanya.id,
        #     "Sql load 12312",
        #     "Sql eqweqeq 12312",
        # )
        # await get_user_with_post(session=session)
        # await get_user_with_post_and_profiles(session=session)
        await get_profiles_with_users_and_users_with_profiles(session=session)
        
async def create_order(session: AsyncSession, promocode: str | None = None) -> Order:
    order = Order(promocode=promocode)
    
    session.add(order)
    await session.commit()
    return order

async def create_product(
    session: AsyncSession,
    name : str,
    description: str,
    price: str,
    )-> Product:
    product = Product(name=name,
                      description=description,
                      price=price,
                      )
    
    session.add(product)
    await session.commit()
    return product

        
async def demo_m2m(session: AsyncSession):
    order_one = await create_order(session=session)
    order_promo = await create_order(session=session, promocode="promocode")
    
    mouse = await create_product(
        session,
        "Mouse",
        "Great gaming mouse",
        price=123,
    )
    keyboard = await create_product(
        session,
        "Keyboard",
        "Great gaming keyboard",
        price=333,
    )
    display = await create_product(
        session,
        "Display",
        "Office display",
        price=551,
    )
    order_one = await session.scalar(
        select(Order)
        .options(selectinload(Order.products))
        .where(Order.id == order_one.id)
    )
    order_promo = await session.scalar(
        select(Order)
        .options(selectinload(Order.products))
        .where(Order.id == order_one.id)
    )
    order_one.products.append(mouse)
    order_one.products.append(keyboard)
    order_promo.products.append(keyboard)
    order_promo.products.append(display)
    
    await session.commit()

async def main():
    async with db_helper.session_factory() as session:
        await demo_m2m(session=session)
        

if __name__ == "__main__":
    asyncio.run(main())
