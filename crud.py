import asyncio
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, User, Profile, Post, Order, Product, OrderProductAssociation

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

async def create_orders_and_products(session: AsyncSession):
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
        .where(Order.id == order_promo.id)
    )
    
    order_one.products.append(mouse)
    order_one.products.append(keyboard)
    order_promo.products.append(keyboard)
    order_promo.products.append(display)
    
    await session.commit()

async def get_order_with_products(session: AsyncSession) -> list[Order]:
    stmt = select(Order).options(selectinload(Order.products)).order_by(Order.id)
    
    orders = await session.scalars(stmt)
    
    return list(orders)

async def demo_get_orders_with_products_through_secundery(session: AsyncSession):
    orders = await get_order_with_products(session)
    for order in orders:
        print(order.id, order.promocode, order.create_at,"products:")
        for product in order.products:
            print("-", product.id, product.name, product.price,)
            
            
async def get_order_with_products_assoc(session: AsyncSession) -> list[Order]:
    stmt = (
        select(Order)
    .options(selectinload(Order.product_details)
             .joinedload(OrderProductAssociation.product),)
    .order_by(Order.id)
    )
    
    orders = await session.scalars(stmt)
    
    return list(orders)
            

async def demo_get_orders_with_products_with_assoc(session: AsyncSession):
    orders = await get_order_with_products_assoc(session)
    
    for order in orders:
        print(order.id, order.promocode, order.create_at, "products:")
        for order_product_details in order.product_details:
            print("-", order_product_details.product.id, order_product_details.product.name, order_product_details.product.price, "qty: ", order_product_details.count)
            
            
async def create_gift_for_assoc_products(session: AsyncSession):
    orders = await get_order_with_products_assoc(session)
    gift_product = await create_product(
        session,
        name="Gift",
        description="Gift for you",
        price=0,
        )
    for order in orders:
        order.product_details.append(
            OrderProductAssociation(
                
                count=1,
                unit_price=0,
                product=gift_product,
            )
        )
        
    await session.commit()
            
            
async def demo_m2m(session: AsyncSession):
    await demo_get_orders_with_products_with_assoc(session)
    # await create_gift_for_assoc_products(session)
    

async def main():
    async with db_helper.session_factory() as session:
        await demo_m2m(session=session)
        

if __name__ == "__main__":
    asyncio.run(main())
