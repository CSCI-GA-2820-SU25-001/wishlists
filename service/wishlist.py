"""
Wishlist and WishlistItem models

This module contains methods for serialization, deserialization, and database operations.
"""

from datetime import datetime
import logging
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


######################################################################
# WISHLIST
######################################################################


# pylint: disable=too-many-instance-attributes
class Wishlist(db.Model):
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
    # Timestamp for creation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Timestamp for last update
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_public = db.Column(db.Boolean, default=False)
    wishlist_items = db.relationship(
        "WishlistItem", backref="wishlist", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        created_at_str = self.created_at.isoformat() if self.created_at else "None"
        updated_at_str = self.updated_at.isoformat() if self.updated_at else "None"

        # Use repr() for string fields to include quotes and handle special characters
        name_repr = repr(self.name)
        description_repr = (
            repr(self.description) if self.description is not None else "None"
        )

        return (
            f"Wishlist("
            f"id={self.id}, "
            f"name={name_repr}, "
            f"customer_id={self.customer_id}, "
            f"description={description_repr}, "  # Use the repr-safe description
            f"created_at={created_at_str}, "
            f"updated_at={updated_at_str}, "
            f"is_public={self.is_public}"  # is_public is already a boolean, no need for quotes
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
        """
        Populates a Wishlist from a dictionary.
        param data: A dictionary has Wishlist data
        raises DataValidationError: if data is not valid
        """
        try:
            self.name = data["name"]
            self.customer_id = data["customer_id"]
            self.description = data.get("description")

            # Add proper boolean type checking (like Pet example)
            if "is_public" in data:
                if isinstance(data["is_public"], bool):
                    self.is_public = data["is_public"]
                else:
                    raise DataValidationError(
                        "Invalid type for boolean [is_public]: "
                        + str(type(data["is_public"]))
                    )
            else:
                self.is_public = False

            # Fix: Use "wishlist_items" not "items" to match serialize method
            items_data = data.get("wishlist_items", [])
            if not isinstance(items_data, list):
                raise DataValidationError(
                    "wishlist_items must be a list of Wishlist Items"
                )

            # Fix: Use self.wishlist_items not self.items
            self.wishlist_items = []
            for item_data in items_data:
                wishlist_item = WishlistItem()
                wishlist_item.deserialize(item_data)
                self.wishlist_items.append(wishlist_item)

        except KeyError as error:
            raise DataValidationError(
                f"Invalid Wishlist: missing required field - {error.args[0]}"
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Wishlist: body of request contained bad or no data "
                f"or incorrect type for a field - {error}"
            ) from error
        except ValueError as error:
            # Catch ValueError if fromisoformat is used or other parsing errors
            raise DataValidationError(
                f"Invalid data format for a field: {error}"
            ) from error
        except AttributeError as error:
            # Catch AttributeError for cases like accessing properties on None or incorrect types
            raise DataValidationError(
                f"Invalid attribute or data structure: {error}"
            ) from error
        return self

    def create(self) -> None:
        """
        Creates a Account to the database
        """
        logger.info("Creating %s", self)
        # id must be none to generate next primary key
        self.id = None
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self) -> None:
        """
        Updates a Account to the database
        """
        logger.info("Updating %s", self)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self) -> None:
        """Removes a Account from the data store"""
        logger.info("Deleting %s", self)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        # pylint: disable=no-member
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        # pylint: disable=no-member
        return cls.query.session.get(cls, by_id)

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


class WishlistItem(db.Model):
    """
    Class that represents a wishlist item

    Schema Description:
    id = primary key for Wishlist item table
    wishlist_id = id of the wishlist that the item belongs to
    product_id = the id of the product
    product_name = the name of the product
    product_description = the description of the product
    product_price = the price of the product
    category = the category of the product
    created_at = timestamp field to store when wishlist item was created
    updated_at = timestamp field to store when wishlist item was last updated
    quantity = How many of this product are desired in the wishlist
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
    category = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    # updated_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return (
            f"<WishlistItem '{self.product_name}' "
            f"id=[{self.id}] "
            f"product_description='{self.product_description}', "
            f"product_price={self.product_price}, "
            f"category='{self.category}', "
            f"wishlist[{self.wishlist_id}] "
            f"product[{self.product_id}]>"
            f"quantity={self.quantity}, "
            f"created_at={self.created_at.isoformat() if self.created_at else 'None'}, "
            f"updated_at={self.updated_at.isoformat() if self.updated_at else 'None'}"
        )

    def serialize(self) -> dict:
        """Convert an object into a dictionary"""
        return {
            "id": self.id,
            "wishlist_id": self.wishlist_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_description": self.product_description,
            "quantity": self.quantity,
            "product_price": self.product_price,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }

    def deserialize(self, data):
        """
        Populates a WishlistItem from a dictionary.
        :param data: A dictionary containing WishlistItem data
        :raises DataValidationError: if data is not valid
        """
        if not isinstance(data, dict):
            raise DataValidationError("Invalid WishlistItem: not a dictionary")
        try:
            self.id = data.get("id", None)
            self.wishlist_id = data["wishlist_id"]
            self.product_id = data["product_id"]
            self.product_name = data["product_name"]
            self.product_description = data["product_description"]
            self.quantity = data.get("quantity", 1)
            self.product_price = float(data["product_price"])
            self.category = data.get("category", None)
            self.created_at = data.get("created_at", None)
            self.updated_at = data.get("updated_at", None)
            if self.product_name is None or not isinstance(self.product_name, str):
                raise DataValidationError(
                    "Invalid WishlistItem: product_name must be a string"
                )
            if self.product_description is None or not isinstance(
                self.product_description, str
            ):
                raise DataValidationError(
                    "Invalid WishlistItem: product_description must be a string"
                )
            if not isinstance(self.quantity, int):
                raise DataValidationError(
                    "Invalid WishlistItem: quantity must be an integer"
                )
        except KeyError as error:
            raise DataValidationError(
                "Invalid WishlistItem: missing " + error.args[0]
            ) from error
        except (ValueError, TypeError) as error:
            raise DataValidationError(
                "Invalid WishlistItem: bad or no data - " + str(error)
            ) from error
        return self

    def create(self) -> None:
        """
        Creates a Account to the database
        """
        logger.info("Creating %s", self)
        # id must be none to generate next primary key
        self.id = None
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self) -> None:
        """
        Updates a Account to the database
        """
        logger.info("Updating %s", self)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self) -> None:
        """Removes a Account from the data store"""
        logger.info("Deleting %s", self)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    @classmethod
    def find_by_product_name(cls, product_name, wishlist_id):
        """Return all items matching product_name"""
        logger.info("Processing lookup for item %s ...", product_name)
        return cls.query.filter(
            cls.wishlist_id == wishlist_id, cls.product_name == product_name
        ).all()
        
    @classmethod
    def find_by_category(cls, category, wishlist_id):
        """Return all items matching category in a specific wishlist"""
        logger.info("Processing lookup for category %s in wishlist %s...", category, wishlist_id)
        return cls.query.filter(
            cls.wishlist_id == wishlist_id, 
            cls.category == category
        ).all()
        
    @classmethod
    def find_by_price_range(cls, min_price, max_price, wishlist_id):
        """Return all items within a price range in a specific wishlist"""
        logger.info("Processing lookup for price range %s-%s in wishlist %s...", 
                   min_price, max_price, wishlist_id)
        query = cls.query.filter(cls.wishlist_id == wishlist_id)
        
        if min_price is not None:
            min_price = Decimal(str(min_price))
            query = query.filter(cls.product_price >= min_price)
        if max_price is not None:
            max_price = Decimal(str(max_price))
            query = query.filter(cls.product_price <= max_price)
        
        return query.all()
    
    @classmethod
    def find_with_filters(cls, wishlist_id, product_name=None, category=None, 
                          min_price=None, max_price=None):
        """
        Find items with multiple filters applied
        This is the most flexible method that combines all possible filters
        """
        logger.info("Processing lookup with filters in wishlist %s...", wishlist_id)
        query = cls.query.filter(cls.wishlist_id == wishlist_id)
        
        if product_name:
            query = query.filter(cls.product_name == product_name)
        if category:
            query = query.filter(cls.category == category)
        if min_price is not None:
            query = query.filter(cls.product_price >= min_price)
        if max_price is not None:
            query = query.filter(cls.product_price <= max_price)
        
        return query.all()

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        # pylint: disable=no-member
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        # pylint: disable=no-member
        return cls.query.session.get(cls, by_id)
