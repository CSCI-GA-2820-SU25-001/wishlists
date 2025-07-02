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
TestWishlist API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.wishlist import db, Wishlist
from tests.factories import WishlistFactory, WishlistItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/wishlists"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlistService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def _create_wishlists(self, count):
        """Factory method to create wishlists in bulk via API"""
        wishlists = []
        for _ in range(count):
            wishlist = WishlistFactory()
            resp = self.client.post(BASE_URL, json=wishlist.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Wishlist",
            )
            new_wishlist = resp.get_json()
            wishlist.id = new_wishlist["id"]
            wishlists.append(wishlist)
        return wishlists

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_wishlist(self):
        """It should Create a new Wishlist"""
        test_wishlist = WishlistFactory()
        logging.debug("Test Wishlist: %s", test_wishlist.serialize())
        response = self.client.post(BASE_URL, json=test_wishlist.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_wishlist = response.get_json()
        self.assertEqual(new_wishlist["name"], test_wishlist.name)
        self.assertEqual(new_wishlist["customer_id"], test_wishlist.customer_id)
        self.assertEqual(new_wishlist["description"], test_wishlist.description)
        self.assertEqual(new_wishlist["is_public"], test_wishlist.is_public)

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_wishlist(self):
        """It should delete a wishlist by ID"""
        # create a wishlist
        test_wishlist = WishlistFactory()
        response = self.client.post(BASE_URL, json=test_wishlist.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wishlist_id = response.get_json()["id"]

        # delete this wishlist
        delete_response = self.client.delete(f"{BASE_URL}/{wishlist_id}")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # check
        get_response = self.client.get(f"{BASE_URL}/{wishlist_id}")
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------

    def test_get_wishlist(self):
        """It should retrieve a single wishlist successfully."""
        # Create a wishlist using the helper
        wishlist = self._create_wishlists(1)[0]

        # Send a GET request
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Validate response data
        data = resp.get_json()
        self.assertEqual(data["name"], wishlist.name)
        self.assertEqual(data["customer_id"], wishlist.customer_id)
        self.assertEqual(data["description"], wishlist.description)
        self.assertEqual(data["is_public"], wishlist.is_public)

    def test_list_all_items_in_wishlist(self):
        """It should list all items in a wishlist"""
        # Add two wishlist items to a wishlist
        wishlist = self._create_wishlists(1)[0]
        wishlist_item_list = WishlistItemFactory.create_batch(2)

        # Create item 1
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=wishlist_item_list[0].serialize(),
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=wishlist_item_list[1].serialize(),
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Get list back and make sure we get both items
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(len(data), 2)

    def test_list_items_on_nonexistent_wishlist(self):
        """It should not list items for a non-existent wishlist"""
        resp = self.client.get(f"{BASE_URL}/0/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_wishlist_item(self):
        """It should add an item to a wishlist"""
        # Create a wishlist
        wishlist = self._create_wishlists(1)[0]
        wishlist_item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=wishlist_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location, "Location header should be set")

        data = resp.get_json()
        logging.debug("Added Wishlist Item: %s", data)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["product_id"], wishlist_item.product_id)
        self.assertEqual(data["product_name"], wishlist_item.product_name)
        self.assertEqual(data["product_description"], wishlist_item.product_description)
        self.assertEqual(data["quantity"], wishlist_item.quantity)
        self.assertEqual(data["product_price"], str(wishlist_item.product_price))

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_wishlist_item = resp.get_json()
        self.assertEqual(
            new_wishlist_item["product_id"],
            wishlist_item.product_id,
            "Product ID should match",
        )

    def test_add_item_to_nonexistent_wishlist(self):
        """It should not add an item to a non-existent wishlist"""
        item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/0/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_wishlist_items(self):
        """It should Get an wishlist item from a wishlist"""
        # Create a known wishlist item
        wishlist = self._create_wishlists(1)[0]
        wishlist_item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=wishlist_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        wishlist_item_id = data["id"]

        # Retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items/{wishlist_item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug("Retrieved Wishlist Item: %s", data)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["product_id"], wishlist_item.product_id)
        self.assertEqual(data["product_name"], wishlist_item.product_name)
        self.assertEqual(data["product_description"], wishlist_item.product_description)
        self.assertEqual(data["quantity"], wishlist_item.quantity)
        self.assertEqual(data["product_price"], str(wishlist_item.product_price))

    def test_get_wishlist_item_not_found(self):
        """It should not Get an item that is not found"""
        wishlist = self._create_wishlists(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items/0",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_wishlist_item(self):
        """It should Update a wishlist item"""
        # Create a known wishlist and item
        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Get the item data from the creation response
        data = resp.get_json()
        logging.debug("Original Wishlist Item: %s", data)
        item_id = data["id"]

        # Update the item with new data
        data["quantity"] = 10
        data["product_name"] = "A new product name"

        resp = self.client.put(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Get the updated item and check the fields
        updated_item = resp.get_json()
        self.assertEqual(updated_item["id"], item_id)
        self.assertEqual(updated_item["wishlist_id"], wishlist.id)
        self.assertEqual(updated_item["quantity"], 10)
        self.assertEqual(updated_item["product_name"], "A new product name")

    def test_delete_wishlist_item(self):
        """It should Delete a wishlist item"""
        # Create a known wishlist and item
        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory()
        # Add the item to the wishlist
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        item_id = data["id"]

        # Send a request to delete the item
        resp = self.client.delete(f"{BASE_URL}/{wishlist.id}/items/{item_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the item is gone
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items/{item_id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_wishlist_name(self):
        """It should update the wishlist name successfully."""
        # Create a wishlist using the helper
        wishlist = self._create_wishlists(1)[0]

        # Define new name
        new_name = "Updated Name"

        # Send PUT request to update the name
        resp = self.client.put(
            f"{BASE_URL}/{wishlist.id}",
            json={"name": new_name, "customer_id": wishlist.customer_id},
            content_type="application/json",
        )

        # Check the response status
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Validate that the name is updated in the response
        data = resp.get_json()
        self.assertEqual(data["name"], new_name)

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_list_wishlists(self):
        """It should list all wishlists"""
        self._create_wishlists(3)

        # Get the list of wishlists
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 3)

    def test_list_wishlists_by_customer_id(self):
        """It should list wishlists filtered by customer_id"""
        # Create wishlists with different customer_ids
        wishlist1 = WishlistFactory(customer_id="customer1")
        wishlist2 = WishlistFactory(customer_id="customer2")
        self.client.post(BASE_URL, json=wishlist1.serialize())
        self.client.post(BASE_URL, json=wishlist2.serialize())

        # Filter by customer_id
        resp = self.client.get(f"{BASE_URL}?customer_id=customer1")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["customer_id"], "customer1")

    def test_list_wishlists_by_name(self):
        """It should list wishlists filtered by name"""
        # Create wishlists with different names
        wishlist1 = WishlistFactory(name="Special Wishlist")
        wishlist2 = WishlistFactory(name="Regular Wishlist")
        self.client.post(BASE_URL, json=wishlist1.serialize())
        self.client.post(BASE_URL, json=wishlist2.serialize())

        # Filter by name
        resp = self.client.get(f"{BASE_URL}?name=Special Wishlist")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Special Wishlist")

    def test_clear_wishlist_with_items(self):
        """It should clear all items from a wishlist with items"""
        # Create a wishlist
        wishlist = self._create_wishlists(1)[0]

        # Add multiple items to the wishlist
        item1 = WishlistItemFactory()
        item2 = WishlistItemFactory()

        resp1 = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item1.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        resp2 = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item2.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)

        # Verify items were added
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)

        # Clear the wishlist
        resp = self.client.post(f"{BASE_URL}/{wishlist.id}/clear")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Verify response content
        data = resp.get_json()
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["items_remaining"], 0)
        self.assertIn("cleared", data["message"])

        # Verify all items are gone
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

        # Verify wishlist still exists
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_clear_empty_wishlist(self):
        """It should clear a wishlist that has no items"""
        # Create a wishlist with no items
        wishlist = self._create_wishlists(1)[0]

        # Verify it has no items
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

        # Clear the empty wishlist
        resp = self.client.post(f"{BASE_URL}/{wishlist.id}/clear")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Verify response
        data = resp.get_json()
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["items_remaining"], 0)

        # Verify wishlist still exists
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_clear_nonexistent_wishlist(self):
        """It should return 404 when trying to clear a non-existent wishlist"""
        resp = self.client.post(f"{BASE_URL}/999/clear")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        data = resp.get_json()
        self.assertIn("could not be found", data["message"])

    def test_clear_wishlist_method_not_allowed(self):
        """It should not allow other HTTP methods on clear endpoint"""
        wishlist = self._create_wishlists(1)[0]

        # Test GET method (should not be allowed)
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/clear")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test PUT method (should not be allowed)
        resp = self.client.put(f"{BASE_URL}/{wishlist.id}/clear")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test DELETE method (should not be allowed)
        resp = self.client.delete(f"{BASE_URL}/{wishlist.id}/clear")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


######################################################################
#  T E S T   S A D   P A T H S
######################################################################
class TestSadPaths(TestCase):
    """Test REST Exception Handling"""

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()

    def test_create_wishlist_no_data(self):
        """It should not Create a Wishlist with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wishlist_no_content_type(self):
        """It should not Create a Wishlist with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_wishlist_wrong_content_type(self):
        """It should not Create a Wishlist with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_wishlist_bad_is_public(self):
        """It should not Create a Wishlist with bad is_public data"""
        test_wishlist = WishlistFactory()
        # change is_public to a string
        test_wishlist.is_public = "true"
        response = self.client.post(BASE_URL, json=test_wishlist.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wishlist_missing_name(self):
        """It should not Create a Wishlist without name"""
        wishlist_data = {"customer_id": "customer123", "description": "Missing name"}
        response = self.client.post(BASE_URL, json=wishlist_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wishlist_missing_customer_id(self):
        """It should not Create a Wishlist without customer_id"""
        wishlist_data = {"name": "Test Wishlist", "description": "Missing customer_id"}
        response = self.client.post(BASE_URL, json=wishlist_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_item_not_found(self):
        """It should return 404 if the item does not exist"""
        wishlist = WishlistFactory()
        wishlist.create()
        resp = self.client.put(
            f"/wishlists/{wishlist.id}/items/99999",
            json={"product_name": "test"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)
        self.assertIn(b"could not be found", resp.data)

    def test_update_item_wrong_wishlist(self):
        """It should return 404 if the item does not belong to the wishlist"""
        wishlist1 = WishlistFactory()
        wishlist1.create()
        wishlist2 = WishlistFactory()
        wishlist2.create()
        item = WishlistItemFactory(wishlist=wishlist1)
        item.create()
        resp = self.client.put(
            f"/wishlists/{wishlist2.id}/items/{item.id}",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)
        self.assertIn(b"could not be found in Wishlist", resp.data)

    def test_update_item_content_type(self):
        """It should return 415 if Content-Type is not application/json"""
        wishlist = WishlistFactory()
        wishlist.create()
        item = WishlistItemFactory(wishlist=wishlist)
        item.create()
        resp = self.client.put(
            f"/wishlists/{wishlist.id}/items/{item.id}",
            data="not json",
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, 415)
        self.assertIn(b"Content-Type must be application/json", resp.data)

    def test_update_wishlist_no_content_type(self):
        """It should not update a wishlist without content type"""
        wishlist = WishlistFactory()
        wishlist.create()
        resp = self.client.put(f"{BASE_URL}/{wishlist.id}")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_nonexistent_wishlist(self):
        """It should return 404 when updating a non-existent wishlist"""
        response = self.client.put(
            f"{BASE_URL}/99999",
            json={"name": "Test", "customer_id": "test"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_item_no_content_type(self):
        """It should return 415 when adding item without content type"""
        wishlist = WishlistFactory()
        wishlist.create()
        response = self.client.post(f"{BASE_URL}/{wishlist.id}/items")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_wishlist_item_wrong_wishlist(self):
        """It should return 404 when getting item from wrong wishlist"""
        # check wishlist_id match
        response = self.client.get(f"{BASE_URL}/99999/items/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
