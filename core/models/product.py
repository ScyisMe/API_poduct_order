from sqlalchemy.orm import Mapped, relationship
from typing import List, TYPE_CHECKING

from .order_products_asossiete import order_product_association_table
from .base import Base
if TYPE_CHECKING:   
    from .order import Order

class Product(Base):
    
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[int] 
    
    orders: Mapped[List["Order"]] = relationship(
        secondary=order_product_association_table,
        back_populates="products",
    )