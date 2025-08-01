from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func
from datetime import datetime
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .product import Product

from .base import Base
from .order_products_asossiete import order_product_association_table

class Order(Base):
    
    promocode: Mapped[str | None]
    create_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=datetime.now,
    )
    products: Mapped[List["Product"]] = relationship(
        secondary=order_product_association_table,
        back_populates="orders",
    )