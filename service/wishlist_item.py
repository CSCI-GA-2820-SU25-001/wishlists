# cspell: ignore Rofrano, ondelete, onupdate
######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Persistent Base class for wishlist item database CRUD functions
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError

logger = logging.getLogger("flask.app")


######################################################################
#  W I S H L I S T  I T E M   M O D E L
######################################################################
class WishlistItem(db.Model, PersistentBase):
    """
    Class that represents a wishlist item

    Schema Description:
    id = primary key for Wishlist item table
    wishlist_id = id of the wishlist that the item belongs to
    product_id = the id of the product
    product_name = the name of the product
    product_description = the description of the product
    product_price = the price of the product
    created_at = timestamp field to store when wishlist item was created
    last_updated_at = timestamp field to store when wishlist item was last updated
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(
        db.Integer, db.ForeignKey("wishlist.id", ondelete="CASCADE"), nullable=False
    )
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    product_description = db.Column(db.String(255), nullable=False)
    product_price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    # last_updated_at = db.Column(db.DateTime, default=db.func.now())
    last_updated_at = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False
    )

    def __repr__(self):
        return (
            f"<WishlistItem '{self.product_name}' "
            f"id=[{self.id}] "
            f"product_description='{self.product_description}', "
            f"product_price={self.product_price}, "
            f"wishlist[{self.wishlist_id}] "
            f"product[{self.product_id}]>"
            f"created_at={self.created_at.isoformat() if self.created_at else 'None'}, "
            f"last_updated_at={self.last_updated_at.isoformat() if self.last_updated_at else 'None'}"
        )

    def __str__(self):
        return (
            f"'{self.product_name}': {self.product_description}, "
            f"Price: {self.product_price}, "
            f"Created: {self.created_at.isoformat() if self.created_at else 'None'}, "
            f"Updated: {self.last_updated_at.isoformat() if self.last_updated_at else 'None'}"
        )

    def serialize(self) -> dict:
        """Serializes the wishlist item into a dictionary."""
        return {
            "id": self.id,
            "wishlist_id": self.wishlist_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_description": self.product_description,
            "product_price": self.product_price,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated_at": (
                self.last_updated_at.isoformat() if self.last_updated_at else None
            ),
        }

    def deserialize(self, data):
        """
        Populates the wishlist item from a dictionary.
        data -> is a dictionary containing wishlist item data.
        """
        try:
            self.wishlist_id = data["wishlist_id"]
            self.product_id = data["product_id"]
            self.product_name = data["product_name"]
            self.product_description = data["product_description"]
            self.product_price = data["product_price"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid data: missing " + error.args[0]
            ) from error
        except (ValueError, TypeError) as error:
            raise DataValidationError(
                "Invalid data: body of request contained bad or no data - " + str(error)
            ) from error
        return self

    @classmethod
    def find_by_product_name(cls, product_name, wishlist_id):
        """Return all items matching product_name"""
        logger.info("Processing lookup for item %s ...", product_name)
        return cls.query.filter(cls.wishlist_id == wishlist_id, cls.product_name == product_name).all()