"""
Test cases for WishlistItem Model
"""

import logging
import os
from unittest import TestCase
from wsgi import app
from service.wishlist import Wishlist, WishlistItem, db, DataValidationError
from tests.factories import WishlistItemFactory, WishlistFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        W I S H L I S T  I T E M   M O D E L   T E S T   C A S E S
######################################################################
class TestWishlistItem(TestCase):
    """WishlistItem Model Test Cases"""

    # pylint: disable=duplicate-code
    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    # pylint: disable=duplicate-code
    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    # pylint: disable=duplicate-code
    def setUp(self):
        """This runs before each test"""
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.query(WishlistItem).delete()  # clean up the last tests
        db.session.commit()

    # pylint: disable=duplicate-code
    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_serialize_an_wishlist_item(self):
        """It should serialize an wishlist item"""
        wishlist_item = WishlistItemFactory()
        serial_wishlist_item = wishlist_item.serialize()
        self.assertEqual(serial_wishlist_item["id"], wishlist_item.id)
        self.assertEqual(serial_wishlist_item["wishlist_id"], wishlist_item.wishlist_id)
        self.assertEqual(serial_wishlist_item["product_id"], wishlist_item.product_id)
        self.assertEqual(
            serial_wishlist_item["product_name"], wishlist_item.product_name
        )
        self.assertEqual(
            serial_wishlist_item["product_description"],
            wishlist_item.product_description,
        )
        self.assertEqual(
            serial_wishlist_item["product_price"], wishlist_item.product_price
        )
        self.assertEqual(
            serial_wishlist_item["created_at"], wishlist_item.created_at.isoformat()
        )
        self.assertEqual(
            serial_wishlist_item["updated_at"],
            wishlist_item.updated_at.isoformat(),
        )

    def test_deserialize_a_wishlist_item(self):
        """It should deserialize a wishlist item"""
        wishlist_item = WishlistItemFactory()
        wishlist_item.create()
        new_wishlist_item = WishlistItem()
        new_wishlist_item.deserialize(wishlist_item.serialize())
        self.assertEqual(new_wishlist_item.wishlist_id, wishlist_item.wishlist_id)
        self.assertEqual(new_wishlist_item.product_id, wishlist_item.product_id)
        self.assertEqual(new_wishlist_item.product_name, wishlist_item.product_name)
        self.assertEqual(
            new_wishlist_item.product_description, wishlist_item.product_description
        )
        self.assertEqual(new_wishlist_item.product_price, wishlist_item.product_price)

    def test_add_wishlist_item(self):
        """It should Create a wishlist with an item and add it to the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = WishlistFactory()
        item = WishlistItemFactory(wishlist=wishlist)
        wishlist.wishlist_items.append(item)
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

        new_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(new_wishlist.wishlist_items[0].product_name, item.product_name)

        item2 = WishlistItemFactory(wishlist=wishlist)
        wishlist.wishlist_items.append(item2)
        wishlist.update()

        new_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(len(new_wishlist.wishlist_items), 2)
        self.assertEqual(
            new_wishlist.wishlist_items[1].product_name, item2.product_name
        )
