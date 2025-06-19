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

logger = logging.getLogger("flask.app")


######################################################################
#  W I S H L I S T   M O D E L
######################################################################
class Wishlist(db.Model, PersistentBase):
    """
    Class that represents a wishlist

    Schema Description:
    id = primary key for Wishlist table
    name = user-assigned wishlist name
    description = a short note user can add for the wishlist
    username = username of the customer who owns the wishlist
    created_at = timestamp field to store when wishlist was created
    last_updated_at = timestamp field to store when wishlist was last updated
    is_public = boolean flag to check visibility of the wishlist
    """

    ##################################################
    # Wishlist Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    username = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    # last_updated_at = db.Column(db.DateTime, default=db.func.now())
    last_updated_at = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False
    )
    is_public = db.Column(db.Boolean, default=False)
    wishlist_items = db.relationship(
        "WishlistItem", backref="wishlist", passive_deletes=True
    )

    def __repr__(self):
        return (
            f"Wishlist("
            f"id={self.id}, "
            f"name={self.name}, "
            f"username={self.username}, "
            f"description='{self.description}', "
            f"created_at={self.created_at.isoformat()}, "
            f"last_updated_at={self.last_updated_at.isoformat()}, "
            f"is_public='{self.is_public}'"
            f")"
        )

    def serialize(self):
        """Serializes a wishlist into a dictionary"""
        wishlist = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "username": self.username,
            "created_at": self.created_at.isoformat(),
            "last_updated_at": self.last_updated_at.isoformat(),
            "is_public": self.is_public,
            "wishlist_items": [],
        }
        for wishlist_item in self.wishlist_items:
            wishlist["wishlist_items"].append(wishlist_item.serialize())
        return wishlist

    def deserialize(self, data):
        """
        Populates an wishlist from a dictionary. data -> is a dictionary containing resource data
        """
        try:
            self.name = data["name"]
            self.username = data["username"]
            self.description = data.get("description", None)
            self.is_public = data.get("is_public", False)
            # self.created_at = data.get("created_at", str(db.func.now()))
            # self.last_updated_at = data.get("last_updated_at", str(db.func.now()))
            # handle inner list of addresses
            wishlist_items_items = data.get("wishlist_items", [])
            for json_wishlists_items in wishlist_items_items:
                wishlist_item = WishlistItem()
                wishlist_item.deserialize(json_wishlists_items)
                self.wishlist_items.append(wishlist_item)
        except KeyError as error:
            raise DataValidationError(
                "Invalid Wishlist Item: missing " + error.args[0]
            ) from error
        except (ValueError, TypeError) as error:
            raise DataValidationError(
                "Invalid Wishlist Item: body of request contained "
                "bad or no data - " + error.args[0]
            ) from error
        return self

    @classmethod
    def find_by_name(cls, name):
        """Return all wishlists with the given name"""
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name).all()

    @classmethod
    def find_for_user(cls, username):
        """Return all wishlists for a specific user"""
        logger.info("Processing lookup for user %s ...", username)
        return cls.query.filter(cls.username == username).all()