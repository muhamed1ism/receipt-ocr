from sqlmodel import Session, select

from app.models import ProductCreate, Product, ProductReceiptItemIn


def get_or_create_product(*, session: Session, product_data: ProductCreate | ProductReceiptItemIn) -> Product:
    product = session.exec(
        select(Product).where(
            Product.name == product_data.name,
            Product.brand == product_data.brand,
        )
    ).first()

    if product:
        return product

    db_obj = Product.model_validate(product_data)
    session.add(db_obj)
    session.flush()
    return db_obj