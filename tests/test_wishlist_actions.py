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
TestWishlist Actions API Service Test Suite
"""

# pylint: disable=duplicate-code
from service.common import status
from tests.test_base import BaseTestCase, BASE_URL
from tests.factories import WishlistFactory, WishlistItemFactory


######################################################################
#  T E S T   C A S E S   -   A C T I O N   E N D P O I N T S
######################################################################
class TestWishlistActions(BaseTestCase):
    """REST API Server Tests for Wishlist Action Operations"""

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

    def test_publish_wishlist(self):
        """It should publish a wishlist (set is_public to True)"""
        wishlist = WishlistFactory(is_public=False)
        wishlist.create()
        resp = self.client.post(f"{BASE_URL}/{wishlist.id}/publish")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertTrue(data["is_public"])
        self.assertIn("published", data["message"])

    def test_unpublish_wishlist(self):
        """It should unpublish a wishlist (set is_public to False)"""
        wishlist = WishlistFactory(is_public=True)
        wishlist.create()
        resp = self.client.post(f"{BASE_URL}/{wishlist.id}/unpublish")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertFalse(data["is_public"])
        self.assertIn("unpublished", data["message"])

    def test_publish_wishlist_not_found(self):
        """It should return 404 when publishing a non-existent wishlist"""
        resp = self.client.post(f"{BASE_URL}/99999/publish")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("could not be found", resp.get_data(as_text=True))

    def test_unpublish_wishlist_not_found(self):
        """It should return 404 when unpublishing a non-existent wishlist"""
        resp = self.client.post(f"{BASE_URL}/99999/unpublish")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("could not be found", resp.get_data(as_text=True))

    def test_like_wishlist_item(self):
        """It should like a wishlist item (increment likes)"""
        # Create a wishlist and add an item
        wishlist = WishlistFactory()
        wishlist.create()
        item = WishlistItemFactory(wishlist=wishlist, likes=0)
        item.create()

        # Like the item
        resp = self.client.post(f"{BASE_URL}/{wishlist.id}/items/{item.id}/like")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["item_id"], item.id)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["likes"], 1)
        self.assertIn("liked", data["message"])

        # Like again to check increment
        resp = self.client.post(f"{BASE_URL}/{wishlist.id}/items/{item.id}/like")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["likes"], 2)

    def test_copy_wishlist(self):
        """It should copy a wishlist and all its items"""
        # Create a wishlist with items
        wishlist = WishlistFactory()
        wishlist.create()
        item1 = WishlistItemFactory(wishlist=wishlist)
        item1.create()
        item2 = WishlistItemFactory(wishlist=wishlist)
        item2.create()

        # Copy the wishlist
        resp = self.client.post(f"{BASE_URL}/{wishlist.id}/copy")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertIn("copied", data["message"])
        self.assertNotEqual(data["original_wishlist_id"], data["new_wishlist_id"])
        self.assertEqual(len(data["wishlist"]["wishlist_items"]), 2)
        # Ensure copied items are not the same id as original
        original_item_ids = {item1.id, item2.id}
        copied_item_ids = {item["id"] for item in data["wishlist"]["wishlist_items"]}
        self.assertTrue(copied_item_ids.isdisjoint(original_item_ids))

    def test_copy_wishlist_not_found(self):
        """It should return 404 when copying a non-existent wishlist"""
        resp = self.client.post(f"{BASE_URL}/99999/copy")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("could not be found", resp.get_data(as_text=True))

    def test_like_wishlist_item_not_found(self):
        """It should return 404 when liking a non-existent item"""
        wishlist = WishlistFactory()
        wishlist.create()
        resp = self.client.post(f"{BASE_URL}/{wishlist.id}/items/99999/like")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("could not be found", resp.get_data(as_text=True))

    def test_like_wishlist_item_wrong_wishlist(self):
        """It should return 404 when liking an item not in the wishlist"""
        wishlist1 = WishlistFactory()
        wishlist1.create()
        wishlist2 = WishlistFactory()
        wishlist2.create()
        item = WishlistItemFactory(wishlist=wishlist1)
        item.create()
        resp = self.client.post(f"{BASE_URL}/{wishlist2.id}/items/{item.id}/like")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("could not be found in Wishlist", resp.get_data(as_text=True))
