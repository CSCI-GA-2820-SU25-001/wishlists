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
TestWishlistItem CRUD API Service Test Suite
"""

# pylint: disable=duplicate-code
import logging
from service.common import status
from tests.test_base import BaseTestCase, BASE_URL
from tests.factories import WishlistItemFactory


######################################################################
#  T E S T   C A S E S   -   W I S H L I S T   I T E M   C R U D
######################################################################
class TestWishlistItemRoutes(BaseTestCase):
    """REST API Server Tests for Wishlist Item Operations"""

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
