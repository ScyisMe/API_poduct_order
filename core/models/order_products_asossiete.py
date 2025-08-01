from sqlalchemy import Table, Column, ForeignKey, Integer, UniqueConstraint

from .base import Base

order_product_association_table = Table(
    "order_product_association_table",
    Base.metadata,
    Column("id", Integer, primary_key=True,  autoincrement=True),
    Column("order_id", ForeignKey("orders.id"),  nullable=False),
    Column("product_id", ForeignKey("products.id"),  nullable=False),
    UniqueConstraint("order_id", "product_id", name="index_uniqe_order_product"),
)
