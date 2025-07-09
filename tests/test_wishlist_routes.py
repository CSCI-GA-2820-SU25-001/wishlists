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
TestWishlist Basic CRUD API Service Test Suite
"""

# pylint: disable=duplicate-code
import logging
from service.common import status
from tests.test_base import BaseTestCase, BASE_URL
from tests.factories import WishlistFactory


######################################################################
#  T E S T   C A S E S   -   B A S I C   W I S H L I S T   C R U D
######################################################################
class TestWishlistRoutes(BaseTestCase):
    """REST API Server Tests for Basic Wishlist Operations"""

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

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

    def test_filter_wishlists_by_is_public(self):
        """It should return Wishlists filtered by is_public value"""
        # Create one public and one private wishlist
        public_wishlist = WishlistFactory(is_public=True)
        private_wishlist = WishlistFactory(is_public=False)

        self.client.post(BASE_URL, json=public_wishlist.serialize())
        self.client.post(BASE_URL, json=private_wishlist.serialize())

        # Test filtering for public wishlists
        resp = self.client.get(f"{BASE_URL}?is_public=true")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertGreaterEqual(len(data), 1)
        for item in data:
            self.assertTrue(item["is_public"])

        # Test filtering for private wishlists
        resp = self.client.get(f"{BASE_URL}?is_public=false")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertGreaterEqual(len(data), 1)
        for item in data:
            self.assertFalse(item["is_public"])

    def test_health_check(self):
        """It should return health status"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"status": "OK"})
