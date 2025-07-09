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

    def test_find_by_visibility_public(self):
        """It should find all public wishlists"""
        # Create public and private wishlists
        public_wishlist1 = WishlistFactory(is_public=True, name="Public List 1")
        public_wishlist2 = WishlistFactory(is_public=True, name="Public List 2")
        private_wishlist = WishlistFactory(is_public=False, name="Private List")

        # Create them in the database
        for wishlist in [public_wishlist1, public_wishlist2, private_wishlist]:
            wishlist.create()

        # Find public wishlists
        public_wishlists = Wishlist.find_by_visibility(True)

        # Should find exactly 2 public wishlists
        self.assertEqual(len(public_wishlists), 2)
        for wishlist in public_wishlists:
            self.assertTrue(wishlist.is_public)
            self.assertIn(wishlist.name, ["Public List 1", "Public List 2"])

    def test_find_by_visibility_private(self):
        """It should find all private wishlists"""
        # Create public and private wishlists
        public_wishlist = WishlistFactory(is_public=True, name="Public List")
        private_wishlist1 = WishlistFactory(is_public=False, name="Private List 1")
        private_wishlist2 = WishlistFactory(is_public=False, name="Private List 2")

        # Create them in the database
        for wishlist in [public_wishlist, private_wishlist1, private_wishlist2]:
            wishlist.create()

        # Find private wishlists
        private_wishlists = Wishlist.find_by_visibility(False)

        # Should find exactly 2 private wishlists
        self.assertEqual(len(private_wishlists), 2)
        for wishlist in private_wishlists:
            self.assertFalse(wishlist.is_public)
            self.assertIn(wishlist.name, ["Private List 1", "Private List 2"])

    def test_find_by_visibility_no_results(self):
        """It should return empty list when no wishlists match the visibility setting"""
        # Create only private wishlists
        private_wishlist = WishlistFactory(is_public=False)
        private_wishlist.create()

        # Search for public wishlists (should find none)
        public_wishlists = Wishlist.find_by_visibility(True)
        self.assertEqual(public_wishlists, [])

    def test_find_public_wishlists_convenience_method(self):
        """It should find public wishlists using convenience method"""
        # Create public and private wishlists
        public_wishlist = WishlistFactory(is_public=True)
        private_wishlist = WishlistFactory(is_public=False)

        for wishlist in [public_wishlist, private_wishlist]:
            wishlist.create()

        # Use convenience method
        public_wishlists = Wishlist.find_public_wishlists()

        self.assertEqual(len(public_wishlists), 1)
        self.assertTrue(public_wishlists[0].is_public)

    def test_find_private_wishlists_convenience_method(self):
        """It should find private wishlists using convenience method"""
        # Create public and private wishlists
        public_wishlist = WishlistFactory(is_public=True)
        private_wishlist = WishlistFactory(is_public=False)

        for wishlist in [public_wishlist, private_wishlist]:
            wishlist.create()

        # Use convenience method
        private_wishlists = Wishlist.find_private_wishlists()

        self.assertEqual(len(private_wishlists), 1)
        self.assertFalse(private_wishlists[0].is_public)
