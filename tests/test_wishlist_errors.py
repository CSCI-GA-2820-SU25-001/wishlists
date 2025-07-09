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
TestWishlist Error Handling and Sad Paths API Service Test Suite
"""

# pylint: disable=duplicate-code
from service.common import status
from tests.test_base import BaseTestCase, BASE_URL
from tests.factories import WishlistFactory, WishlistItemFactory


######################################################################
#  T E S T   S A D   P A T H S   A N D   E R R O R   H A N D L I N G
######################################################################
class TestWishlistErrors(BaseTestCase):
    """Test REST Exception Handling and Error Cases"""

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
