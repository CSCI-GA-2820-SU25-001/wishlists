import logging
from .persistent_base import db, DataValidationError

logger = logging.getLogger("flask.app")

######################################################################
# ITEM
######################################################################


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
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }

    def deserialize(self, data: dict) -> None:
        """Convert a dictionary into an object"""
        self.id = data.get("id", None)
        self.wishlist_id = data.get("wishlist_id", None)
        self.product_id = data.get("product_id", None)
        self.quantity = data.get("quantity", 1) # Default to 1 if quantity is not provided
        self.product_name = data.get("product_name", None)
        self.product_description = data.get("product_description", None)
        self.product_price = data.get("product_price", None)
        self.created_at = data.get("created_at", None)
        self.updated_at = data.get("updated_at", None)

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
