from dataclasses import dataclass
from logging import getLogger
from typing import List
import collections

from sqlalchemy import desc
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.orm.exc import NoResultFound
from shop.stripe_constants import MakerspaceMetadataKeys
from shop.stripe_subscriptions import get_subscription_products

from membership.views import member_entity
from service.db import db_session
from service.error import NotFound
from shop.entities import (
    transaction_entity,
    transaction_content_entity,
    product_entity,
    category_entity,
    product_image_entity,
)
from shop.models import Transaction, Product, ProductCategory, ProductAction
from shop.transactions import pending_actions_query

logger = getLogger("makeradmin")


def pending_actions(member_id=None):
    query = pending_actions_query(member_id)

    return [
        {
            "content": {
                "id": content.id,
                "transaction_id": content.transaction_id,
                "product_id": content.product_id,
                "count": content.count,
                "amount": str(content.amount),
            },
            "action": {
                "action": action.action_type,
                "value": action.value,
            },
            "member_id": transaction.member_id,
            "created_at": transaction.created_at.isoformat(),
        }
        for action, content, transaction in query
    ]


def member_history(member_id):
    query = (
        db_session.query(Transaction)
        .options(joinedload("contents"), joinedload("contents.product"))
        .filter(Transaction.member_id == member_id)
        .order_by(desc(Transaction.id))
    )

    return [
        {
            **transaction_entity.to_obj(transaction),
            "contents": [
                {
                    **transaction_content_entity.to_obj(content),
                    "product": product_entity.to_obj(content.product),
                }
                for content in transaction.contents
            ],
        }
        for transaction in query.all()
    ]


def receipt(member_id, transaction_id):
    try:
        transaction = (
            db_session.query(Transaction)
            .filter_by(member_id=member_id, id=transaction_id)
            .options(joinedload("contents"), joinedload("contents.product"))
            .one()
        )
    except NoResultFound:
        raise NotFound()

    return {
        "member": member_entity.to_obj(transaction.member),
        "transaction": {
            **transaction_entity.to_obj(transaction),
            "contents": [
                {
                    **transaction_content_entity.to_obj(content),
                    "product": product_entity.to_obj(content.product),
                }
                for content in transaction.contents
            ],
        },
    }


def special_product_data() -> List[Product]:
    # Make sure subscription products have been created
    get_subscription_products()

    query = (
        db_session.query(Product)
        .filter(Product.deleted_at.is_(None))
        .filter(Product.product_metadata[MakerspaceMetadataKeys.SPECIAL_PRODUCT_ID.value] != "")
    )

    products: List[Product] = query.all()

    duplicates = [
        item
        for item, count in collections.Counter(
            [p.product_metadata[MakerspaceMetadataKeys.SPECIAL_PRODUCT_ID.value] for p in products]
        ).items()
        if count > 1
    ]
    if len(duplicates) > 0:
        raise Exception("Multiple products have the same special product id. Duplicates: " + str(duplicates))

    return products


def all_product_data():
    """Return all public products and categories."""

    query = (
        db_session.query(ProductCategory)
        .join(ProductCategory.products)
        .options(contains_eager(ProductCategory.products))
        .filter(Product.deleted_at.is_(None))
        .order_by(ProductCategory.display_order)
    )

    return [
        {
            **category_entity.to_obj(category),
            "items": [
                product_entity.to_obj(product) for product in sorted(category.products, key=lambda p: p.display_order)
            ],
        }
        for category in query
    ]


def get_product_data(product_id):
    try:
        product = db_session.query(Product).filter_by(id=product_id, deleted_at=None).one()
    except NoResultFound:
        raise NotFound()

    return {
        "product": product_entity.to_obj(product),
        "productData": all_product_data(),
    }


@dataclass
class SimpleProductData:
    id: int
    name: str
    price: float


def get_membership_products() -> List[SimpleProductData]:
    # Find all products which gives a member membership
    # Note: Assumes a product never contains multiple actions of the same type.
    # If this doesn't hold we will get duplicates of that product in the list.
    query = (
        db_session.query(Product)
        .join(ProductAction)
        .filter(
            ProductAction.action_type == ProductAction.ADD_MEMBERSHIP_DAYS,
            ProductAction.deleted_at.is_(None),
            Product.deleted_at.is_(None),
        )
    )

    return [SimpleProductData(p.id, p.name, float(p.price)) for p in query]
