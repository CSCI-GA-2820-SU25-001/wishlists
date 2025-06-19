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

# cspell: ignore Rofrano, onupdate, backref

"""
Persistent Base class for Wishlist database CRUD functions
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError
from .wishlist_item import WishlistItem
from datetime import datetime

logger = logging.getLogger("flask.app")


######################################################################
# WISHLIST
######################################################################
class Wishlist(db.Model, PersistentBase):
    """
    Class that represents a wishlist

    Schema Description:
    id = primary key for Wishlist table
    name = user-assigned wishlist name
    description = a short note user can add for the wishlist
    customer_id = customer_id of the customer who owns the wishlist
    created_at = timestamp field to store when wishlist was created
    updated_at = timestamp field to store when wishlist was last updated
    is_public = boolean flag to check visibility of the wishlist
    """

    ##################################################
    # Wishlist Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    customer_id = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # Timestamp for creation
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # Timestamp for last update
    is_public = db.Column(db.Boolean, default=False)
    wishlist_items = db.relationship('WishlistItem', backref='wishlist', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        created_at_str = self.created_at.isoformat() if self.created_at else 'None'
        updated_at_str = self.updated_at.isoformat() if self.updated_at else 'None'

        # Use repr() for string fields to include quotes and handle special characters
        name_repr = repr(self.name)
        description_repr = repr(self.description) if self.description is not None else 'None'

        return (
            f"Wishlist("
            f"id={self.id}, "
            f"name={name_repr}, "
            f"customer_id={self.customer_id}, "
            f"description={description_repr}, " # Use the repr-safe description
            f"created_at={created_at_str}, "
            f"updated_at={updated_at_str}, "
            f"is_public={self.is_public}" # is_public is already a boolean, no need for quotes
            f")"
        )

    def serialize(self):
        """Serializes a wishlist into a dictionary"""
        wishlist = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "customer_id": self.customer_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_public": self.is_public,
            "wishlist_items": [],
        }
        for wishlist_item in self.wishlist_items:
            wishlist["wishlist_items"].append(wishlist_item.serialize())
        return wishlist

    def deserialize(self, data):
        try:
            # Required fields
            self.name = data["name"]
            self.customer_id = data["customer_id"]
            # Optional fields with default values
            self.description = data.get("description")
            self.is_public = data.get("is_public", False)
            items_data = data.get("items", []) 
            if not isinstance(items_data, list):
                raise DataValidationError("items must be a list of Wishlist Items")
            self.items = [] 
            for item_data in items_data:
                wishlist_item = WishlistItem()
                # Deserializing the item. No need to set wishlist_id here,
                # SQLAlchemy handles it when appending to self.items
                wishlist_item.deserialize(item_data)
                self.items.append(wishlist_item) # Append to the relationship collection

        except KeyError as error:
            raise DataValidationError(f"Invalid Wishlist: missing required field - {error.args[0]}") from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Wishlist: body of request contained bad or no data "
                f"or incorrect type for a field - {error}"
            ) from error
        except ValueError as error:
            # Catch ValueError if fromisoformat is used or other parsing errors
            raise DataValidationError(f"Invalid data format for a field: {error}") from error
        except AttributeError as error:
            # Catch AttributeError for cases like accessing properties on None or incorrect types
            raise DataValidationError(f"Invalid attribute or data structure: {error}") from error
        return self

    @classmethod
    def find_by_name(cls, name):
        """Return all wishlists with the given name"""
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name).all()

    @classmethod
    def find_for_user(cls, customer_id):
        """Return all wishlists for a specific user"""
        logger.info("Processing lookup for user %s ...", customer_id)
        return cls.query.filter(cls.customer_id == customer_id).all()
