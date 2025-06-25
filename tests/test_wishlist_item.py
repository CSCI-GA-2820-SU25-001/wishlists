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
        self.assertEqual(
            new_wishlist_item.product_price, float(wishlist_item.product_price)
        )
        self.assertEqual(new_wishlist_item.quantity, wishlist_item.quantity)

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

    def test_create_and_find_wishlist_item(self):
        """It should create and find a wishlist item"""
        wishlist = WishlistFactory()
        wishlist.create()
        item = WishlistItemFactory(wishlist=wishlist)
        item.create()
        found = WishlistItem.find(item.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.product_name, item.product_name)

    def test_update_wishlist_item(self):
        """It should update a wishlist item"""
        wishlist = WishlistFactory()
        wishlist.create()
        item = WishlistItemFactory(wishlist=wishlist)
        item.create()
        item.product_name = "Updated Name"
        item.update()
        updated = WishlistItem.find(item.id)
        self.assertEqual(updated.product_name, "Updated Name")

    def test_delete_a_wishlist_item(self):
        """It should delete a wishlist item from the database"""
        wishlist = WishlistFactory()
        wishlist.create()
        item = WishlistItemFactory(wishlist=wishlist)
        item.create()
        item_id = item.id
        item.delete()
        self.assertIsNone(WishlistItem.find(item_id))

    def test_find_by_product_name(self):
        """It should find a wishlist item by product_name"""
        wishlist = WishlistFactory()
        wishlist.create()
        item = WishlistItemFactory(wishlist=wishlist, product_name="UniqueName")
        item.create()
        found_items = WishlistItem.find_by_product_name("UniqueName", wishlist.id)
        self.assertGreaterEqual(len(found_items), 1)
        self.assertEqual(found_items[0].product_name, "UniqueName")

    def test_wishlist_item_repr(self):
        """It should return a string representation of WishlistItem"""
        item = WishlistItemFactory()
        self.assertIn(item.product_name, repr(item))

    def test_wishlist_item_serialize(self):
        """It should serialize a WishlistItem"""
        item = WishlistItemFactory()
        data = item.serialize()
        self.assertEqual(data["product_name"], item.product_name)

    def test_wishlist_item_deserialize(self):
        """It should deserialize a WishlistItem"""
        item = WishlistItem()
        data = WishlistItemFactory().serialize()
        item.deserialize(data)
        self.assertEqual(item.product_name, data["product_name"])

    def test_update_without_id_raises(self):
        """It should raise DataValidationError if update called without id"""
        item = WishlistItemFactory()
        item.id = None
        with self.assertRaises(DataValidationError):
            item.update()

    def test_wishlist_item_deserialize_key_error(self):
        """It should raise DataValidationError for missing required fields"""
        item = WishlistItem()
        with self.assertRaises(DataValidationError):
            item.deserialize({})

    def test_wishlist_item_deserialize_type_error(self):
        """It should raise DataValidationError for wrong type"""
        item = WishlistItem()
        with self.assertRaises(DataValidationError):
            item.deserialize([])

    def test_wishlist_item_deserialize_value_error(self):
        """It should raise DataValidationError for value error"""
        item = WishlistItem()
        data = {
            "wishlist_id": 1,
            "product_id": 2,
            "product_name": "Test",
            "product_description": "desc",
            "product_price": "not-a-float",
            "quantity": 1,
        }
        with self.assertRaises(DataValidationError):
            item.deserialize(data)

    def test_wishlist_item_deserialize_attribute_error(self):
        """It should raise DataValidationError for attribute error"""
        item = WishlistItem()
        data = {
            "wishlist_id": 1,
            "product_id": 2,
            "product_name": None,
            "product_description": "desc",
            "product_price": 1.0,
            "quantity": 1,
        }
        with self.assertRaises(DataValidationError):
            item.deserialize(data)

    def test_delete_with_db_exception(self):
        """It should raise DataValidationError if db.session.delete fails"""
        item = WishlistItemFactory()
        item.create()
        original_delete = db.session.delete

        def raise_exc(obj):
            raise Exception("DB error")

        db.session.delete = raise_exc
        try:
            with self.assertRaises(DataValidationError):
                item.delete()
        finally:
            db.session.delete = original_delete

    def test_update_with_db_exception(self):
        """It should raise DataValidationError if db.session.commit fails"""
        item = WishlistItemFactory()
        item.create()
        original_commit = db.session.commit

        def raise_exc():
            raise Exception("DB error")

        db.session.commit = raise_exc
        try:
            with self.assertRaises(DataValidationError):
                item.update()
        finally:
            db.session.commit = original_commit

    def test_find_by_product_name_not_found(self):
        """It should return empty list if product_name not found"""
        wishlist = WishlistFactory()
        wishlist.create()
        found_items = WishlistItem.find_by_product_name("NotExist", wishlist.id)
        self.assertEqual(found_items, [])

    def test_all_empty(self):
        """It should return empty list if no items"""
        WishlistItem.query.delete()
        db.session.commit()
        items = WishlistItem.all()
        self.assertEqual(items, [])

    def test_find_not_found(self):
        """It should return None if id not found"""
        self.assertIsNone(WishlistItem.find(999999))

    def test_wishlist_item_deserialize_invalid_types(self):
        """It should raise DataValidationError for invalid types"""
        item = WishlistItem()
        # product_name is not a string
        data = {
            "wishlist_id": 1,
            "product_id": 2,
            "product_name": None,
            "product_description": "desc",
            "quantity": 1,
            "product_price": 1.0,
        }
        with self.assertRaises(DataValidationError):
            item.deserialize(data)
        # product_description is not a string
        data["product_name"] = "Valid"
        data["product_description"] = None
        with self.assertRaises(DataValidationError):
            item.deserialize(data)
        # quantity is not an int
        data["product_description"] = "desc"
        data["quantity"] = "not-an-int"
        with self.assertRaises(DataValidationError):
            item.deserialize(data)

    def test_wishlist_item_deserialize_missing_fields(self):
        """It should raise DataValidationError for missing required fields"""
        item = WishlistItem()
        # missing product_name
        data = {
            "wishlist_id": 1,
            "product_id": 2,
            "product_description": "desc",
            "quantity": 1,
            "product_price": 1.0,
        }
        with self.assertRaises(DataValidationError):
            item.deserialize(data)
        # missing product_description
        data = {
            "wishlist_id": 1,
            "product_id": 2,
            "product_name": "Test",
            "quantity": 1,
            "product_price": 1.0,
        }
        with self.assertRaises(DataValidationError):
            item.deserialize(data)
        # missing product_price
        data = {
            "wishlist_id": 1,
            "product_id": 2,
            "product_name": "Test",
            "product_description": "desc",
            "quantity": 1,
        }
        with self.assertRaises(DataValidationError):
            item.deserialize(data)

    def test_wishlist_item_deserialize_not_dict(self):
        """It should raise DataValidationError if input is not a dict"""
        item = WishlistItem()
        with self.assertRaises(DataValidationError):
            item.deserialize(["not", "a", "dict"])
