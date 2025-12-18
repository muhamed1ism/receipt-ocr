from sqlmodel import Session, select

from app.models import Product
from app.schemas import ProductCreate, ProductReceiptItemIn


def get_or_create_product(*, session: Session, product_data: ProductCreate | ProductReceiptItemIn) -> Product:
    print({'PRODUCT': product_data})
    product = session.exec(
        select(Product).where(
            Product.name == product_data.name,
            Product.brand == product_data.brand,
        )
    ).one_or_none()

    if product:
        return product

    new_product = Product.model_validate(product_data)
    session.add(new_product)
    session.flush()
    return new_product