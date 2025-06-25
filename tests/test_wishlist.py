"""
Test cases for Wishlist Model
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.wishlist import Wishlist, WishlistItem, DataValidationError, db
from tests.factories import WishlistFactory, WishlistItemFactory

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

    def test_add_wishlist_items(self):
        """It should create a wishlist and assert that it exists"""
        fake_wishlist = WishlistFactory()
        # pylint: disable=unexpected-keyword-arg
        wishlist = Wishlist(
            name=fake_wishlist.name,
            id=fake_wishlist.id,
            is_public=fake_wishlist.is_public,
            customer_id=fake_wishlist.customer_id,
            description=fake_wishlist.description,
            created_at=fake_wishlist.created_at,
            updated_at=fake_wishlist.updated_at,
        )
        self.assertIsNotNone(wishlist)
        self.assertEqual(wishlist.id, fake_wishlist.id)
        self.assertEqual(wishlist.name, fake_wishlist.name)
        self.assertEqual(wishlist.customer_id, fake_wishlist.customer_id)
        self.assertEqual(wishlist.description, fake_wishlist.description)
        self.assertEqual(wishlist.created_at, fake_wishlist.created_at)
        self.assertEqual(wishlist.updated_at, fake_wishlist.updated_at)
        self.assertEqual(wishlist.wishlist_items, fake_wishlist.wishlist_items)

    def test_serialize_a_wishlist(self):
        """It should serialize a wishlist with items"""
        wishlist = WishlistFactory()
        item = WishlistItemFactory(wishlist=wishlist)
        wishlist.wishlist_items.append(item)
        wishlist.create()
        serial = wishlist.serialize()
        self.assertEqual(serial["id"], wishlist.id)
        self.assertEqual(serial["name"], wishlist.name)
        self.assertEqual(serial["customer_id"], wishlist.customer_id)
        self.assertEqual(serial["is_public"], wishlist.is_public)
        self.assertEqual(len(serial["wishlist_items"]), 1)
        self.assertEqual(serial["wishlist_items"][0]["product_name"], item.product_name)

    def test_deserialize_a_wishlist(self):
        """It should deserialize a wishlist from a dict with items"""
        wishlist = WishlistFactory()
        item = WishlistItemFactory(wishlist=wishlist)
        wishlist_dict = wishlist.serialize()
        wishlist_dict["wishlist_items"] = [item.serialize()]
        new_wishlist = Wishlist()
        new_wishlist.deserialize(wishlist_dict)
        self.assertEqual(new_wishlist.name, wishlist.name)
        self.assertEqual(new_wishlist.customer_id, wishlist.customer_id)
        self.assertEqual(len(new_wishlist.wishlist_items), 1)
        self.assertEqual(new_wishlist.wishlist_items[0].product_name, item.product_name)
        self.assertEqual(new_wishlist.wishlist_items[0].product_id, item.product_id)
        self.assertEqual(new_wishlist.wishlist_items[0].quantity, item.quantity)
        self.assertEqual(
            new_wishlist.wishlist_items[0].product_description, item.product_description
        )
        self.assertEqual(
            float(new_wishlist.wishlist_items[0].product_price),
            float(item.product_price),
        )

    def test_delete_a_wishlist(self):
        """It should delete a wishlist from the database"""
        wishlist = WishlistFactory()
        wishlist.create()
        wishlist_id = wishlist.id
        wishlist.delete()
        self.assertIsNone(Wishlist.find(wishlist_id))

    def test_find_by_name(self):
        """It should find wishlists by name"""
        wishlist = WishlistFactory(name="SpecialName")
        wishlist.create()
        found = Wishlist.find_by_name("SpecialName")
        self.assertGreaterEqual(len(found), 1)
        self.assertEqual(found[0].name, "SpecialName")

    def test_find_for_user(self):
        """It should find wishlists for a specific user"""
        wishlist = WishlistFactory(customer_id="user123")
        wishlist.create()
        found = Wishlist.find_for_user("user123")
        self.assertGreaterEqual(len(found), 1)
        self.assertEqual(found[0].customer_id, "user123")

    def test_deserialize_wishlist_key_error(self):
        """It should raise DataValidationError for missing required fields"""
        wishlist = Wishlist()
        with self.assertRaises(DataValidationError):
            wishlist.deserialize({})

    def test_deserialize_wishlist_type_error(self):
        """It should raise DataValidationError for wrong type"""
        wishlist = Wishlist()
        with self.assertRaises(DataValidationError):
            wishlist.deserialize([])

    def test_deserialize_wishlist_items_type_error(self):
        """It should raise DataValidationError if wishlist_items is not a list"""
        wishlist = Wishlist()
        data = {"name": "Test", "customer_id": "c1", "wishlist_items": "notalist"}
        with self.assertRaises(DataValidationError):
            wishlist.deserialize(data)

    def test_wishlist_create_db_exception(self):
        """It should raise DataValidationError if db.session.add or commit fails during create"""
        wishlist = WishlistFactory()
        wishlist.id = None
        # Patch db.session.add to raise Exception
        original_add = db.session.add

        def raise_exc(obj):
            raise Exception("DB error")

        db.session.add = raise_exc
        try:
            with self.assertRaises(DataValidationError):
                wishlist.create()
        finally:
            db.session.add = original_add

    def test_wishlist_update_db_exception(self):
        """It should raise DataValidationError if db.session.commit fails during update"""
        wishlist = WishlistFactory()
        wishlist.create()
        original_commit = db.session.commit

        def raise_exc():
            raise Exception("DB error")

        db.session.commit = raise_exc
        try:
            with self.assertRaises(DataValidationError):
                wishlist.update()
        finally:
            db.session.commit = original_commit

    def test_wishlist_delete_db_exception(self):
        """It should raise DataValidationError if db.session.delete or commit fails during delete"""
        wishlist = WishlistFactory()
        wishlist.create()
        original_delete = db.session.delete

        def raise_exc(obj):
            raise Exception("DB error")

        db.session.delete = raise_exc
        try:
            with self.assertRaises(DataValidationError):
                wishlist.delete()
        finally:
            db.session.delete = original_delete
