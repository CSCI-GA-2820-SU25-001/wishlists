"""
Test cases for Wishlist Model
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.wishlist import Wishlist, WishlistItem, DataValidationError, db
from tests.factories import WishlistFactory

# cspell: ignore psycopg testdb, psycopg

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  W I S H L I S T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlist(TestCase):
    """Test Cases for Wishlist Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.query(WishlistItem).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_wishlist(self):
        """It should create a wishlist and assert that it exists"""
        fake_wishlist = WishlistFactory()
        # pylint: disable=unexpected-keyword-arg
        wishlist = Wishlist(
            name=fake_wishlist.name,
            is_public=fake_wishlist.is_public,
            customer_id=fake_wishlist.customer_id,
            description=fake_wishlist.description,
            created_at=fake_wishlist.created_at,
            updated_at=fake_wishlist.updated_at,
        )
        self.assertIsNotNone(wishlist)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, fake_wishlist.name)
        self.assertEqual(wishlist.customer_id, fake_wishlist.customer_id)
        self.assertEqual(wishlist.description, fake_wishlist.description)
        self.assertEqual(wishlist.created_at, fake_wishlist.created_at)
        self.assertEqual(wishlist.updated_at, fake_wishlist.updated_at)
        self.assertEqual(wishlist.wishlist_items, fake_wishlist.wishlist_items)

    def test_read_wishlist(self):
        """It should Read a wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()

        # Read it back
        found_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(found_wishlist.id, wishlist.id)
        self.assertEqual(found_wishlist.name, wishlist.name)
        self.assertEqual(found_wishlist.customer_id, wishlist.customer_id)
        self.assertEqual(found_wishlist.description, wishlist.description)
        self.assertEqual(found_wishlist.created_at, wishlist.created_at)
        self.assertEqual(found_wishlist.updated_at, wishlist.updated_at)
        self.assertEqual(found_wishlist.wishlist_items, [])

    def test_update_without_id_raises(self):
        """It should raise DataValidationError if update called without id"""
        wishlist = WishlistFactory()
        wishlist.id = None
        with self.assertRaises(DataValidationError):
            wishlist.update()

    def test_wishlist_deserialize_attribute_error_in_items(self):
        """It should raise DataValidationError for attribute error in items processing"""
        wishlist = Wishlist()
        # This will cause an AttributeError when trying to process wishlist_items
        data = {
            "name": "Test",
            "customer_id": "c1",
            "wishlist_items": [{"invalid": "data"}],
        }
        with self.assertRaises(DataValidationError):
            wishlist.deserialize(data)

    def test_wishlist_deserialize_value_error_in_items(self):
        """It should raise DataValidationError for value error in items processing"""
        wishlist = Wishlist()
        data = {
            "name": "Test",
            "customer_id": "c1",
            "wishlist_items": [{"product_price": "invalid_float"}],
        }
        with self.assertRaises(DataValidationError):
            wishlist.deserialize(data)
