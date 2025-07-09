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
TestWishlist Filtering and Search API Service Test Suite
"""

# pylint: disable=duplicate-code
from decimal import Decimal
from service.common import status
from tests.test_base import BaseTestCase, BASE_URL
from tests.factories import WishlistItemFactory


######################################################################
#  T E S T   C A S E S   -   F I L T E R I N G   &   S E A R C H
######################################################################
class TestWishlistFilters(BaseTestCase):
    """REST API Server Tests for Wishlist Filtering and Search Operations"""

    def test_search_items_by_product_name(self):
        """It should search for items by product name in a wishlist"""
        # Create a wishlist
        wishlist = self._create_wishlists(1)[0]

        # Create items with different names
        item1 = WishlistItemFactory(product_name="iPhone 15")
        item2 = WishlistItemFactory(product_name="Samsung Galaxy")
        item3 = WishlistItemFactory(product_name="iPhone 14")

        # Add all items to the wishlist
        for item in [item1, item2, item3]:
            resp = self.client.post(
                f"{BASE_URL}/{wishlist.id}/items",
                json=item.serialize(),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Search for items with "iPhone" in the name
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items?product_name=iPhone 15")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_name"], "iPhone 15")

    def test_search_items_by_product_name_multiple_results(self):
        """It should return multiple items when multiple matches exist"""
        # Create a wishlist
        wishlist = self._create_wishlists(1)[0]

        # Create multiple items with the same name
        item1 = WishlistItemFactory(product_name="iPhone")
        item2 = WishlistItemFactory(product_name="iPhone")

        # Add items to the wishlist
        for item in [item1, item2]:
            resp = self.client.post(
                f"{BASE_URL}/{wishlist.id}/items",
                json=item.serialize(),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Search for items
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items?product_name=iPhone")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)
        for item in data:
            self.assertEqual(item["product_name"], "iPhone")

    def test_search_items_by_product_name_not_found(self):
        """It should return 404 when no items match the search term"""
        # Create a wishlist with some items
        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory(product_name="iPhone")

        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Search for a product that doesn't exist
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items?product_name=NonExistentProduct"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Verify the error message
        data = resp.get_json()
        self.assertIn("NonExistentProduct", data["message"])

    def test_search_items_in_nonexistent_wishlist(self):
        """It should return 404 when searching in a non-existent wishlist"""
        resp = self.client.get(f"{BASE_URL}/99999/items?product_name=iPhone")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_items_empty_wishlist(self):
        """It should return 404 when searching in an empty wishlist"""
        # Create an empty wishlist
        wishlist = self._create_wishlists(1)[0]

        # Search for items in the empty wishlist
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items?product_name=iPhone")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_items_by_category(self):
        """It should filter items by category"""
        # Create a wishlist
        wishlist = self._create_wishlists(1)[0]

        # Create items with different categories
        electronics_item = WishlistItemFactory(
            category="electronics", product_name="iPhone"
        )
        food_item = WishlistItemFactory(category="food", product_name="Pizza")
        clothing_item = WishlistItemFactory(category="clothing", product_name="T-shirt")

        # Add all items to the wishlist
        for item in [electronics_item, food_item, clothing_item]:
            resp = self.client.post(
                f"{BASE_URL}/{wishlist.id}/items",
                json=item.serialize(),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Filter by electronics category
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items?category=electronics")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["category"], "electronics")
        self.assertEqual(data[0]["product_name"], "iPhone")

    def test_filter_items_by_price_range(self):
        """It should filter items by price range"""
        # Create a wishlist
        wishlist = self._create_wishlists(1)[0]

        # Create items with different prices
        cheap_item = WishlistItemFactory(
            product_price=Decimal("50.00"), product_name="Cheap Item"
        )
        medium_item = WishlistItemFactory(
            product_price=Decimal("150.00"), product_name="Medium Item"
        )
        expensive_item = WishlistItemFactory(
            product_price=Decimal("500.00"), product_name="Expensive Item"
        )

        # Add all items to the wishlist
        for item in [cheap_item, medium_item, expensive_item]:
            resp = self.client.post(
                f"{BASE_URL}/{wishlist.id}/items",
                json=item.serialize(),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Filter by price range 100-200
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items?min_price=100&max_price=200"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_name"], "Medium Item")
        self.assertEqual(float(data[0]["product_price"]), 150.00)

    def test_filter_items_by_min_price_only(self):
        """It should filter items by minimum price only"""
        # Create a wishlist
        wishlist = self._create_wishlists(1)[0]

        # Create items with different prices
        cheap_item = WishlistItemFactory(product_price=Decimal("50.00"))
        expensive_item = WishlistItemFactory(product_price=Decimal("500.00"))

        # Add items to the wishlist
        for item in [cheap_item, expensive_item]:
            resp = self.client.post(
                f"{BASE_URL}/{wishlist.id}/items",
                json=item.serialize(),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Filter by minimum price 100
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items?min_price=100")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(float(data[0]["product_price"]), 500.00)

    def test_filter_items_by_max_price_only(self):
        """It should filter items by maximum price only"""
        # Create a wishlist
        wishlist = self._create_wishlists(1)[0]

        # Create items with different prices
        cheap_item = WishlistItemFactory(product_price=Decimal("50.00"))
        expensive_item = WishlistItemFactory(product_price=Decimal("500.00"))

        # Add items to the wishlist
        for item in [cheap_item, expensive_item]:
            resp = self.client.post(
                f"{BASE_URL}/{wishlist.id}/items",
                json=item.serialize(),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Filter by maximum price 100
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items?max_price=100")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(float(data[0]["product_price"]), 50.00)

    def test_filter_items_combined_filters(self):
        """It should filter items using multiple filters combined"""
        # Create a wishlist
        wishlist = self._create_wishlists(1)[0]

        # Create items with different attributes
        target_item = WishlistItemFactory(
            category="electronics",
            product_price=Decimal("150.00"),
            product_name="Target Item",
        )
        wrong_category = WishlistItemFactory(
            category="food",
            product_price=Decimal("150.00"),
            product_name="Wrong Category",
        )
        wrong_price = WishlistItemFactory(
            category="electronics",
            product_price=Decimal("50.00"),
            product_name="Wrong Price",
        )

        # Add all items to the wishlist
        for item in [target_item, wrong_category, wrong_price]:
            resp = self.client.post(
                f"{BASE_URL}/{wishlist.id}/items",
                json=item.serialize(),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Filter by both category and price range
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items?category=electronics&min_price=100&max_price=200"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_name"], "Target Item")
        self.assertEqual(data[0]["category"], "electronics")
        self.assertEqual(float(data[0]["product_price"]), 150.00)

    def test_filter_items_no_results(self):
        """It should return 404 when no items match the filters"""
        # Create a wishlist with some items
        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory(
            category="electronics", product_price=Decimal("100.00")
        )

        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Search for a category that doesn't exist
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items?category=nonexistent")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_items_invalid_price(self):
        """It should return 400 for invalid price parameters"""
        wishlist = self._create_wishlists(1)[0]

        # Test invalid min_price
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items?min_price=invalid")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid max_price
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items?max_price=not_a_number")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_items_min_price_no_results(self):
        """It should return 404 with min_price in error message when no items match min_price filter"""
        # Create a wishlist with low-priced items
        wishlist = self._create_wishlists(1)[0]
        cheap_item = WishlistItemFactory(product_price=Decimal("25.00"))

        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=cheap_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Search for items with min_price that won't match
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items?min_price=100")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Check that error message includes min_price information (correct format)
        data = resp.get_json()
        self.assertIn("min_price '100.0'", data["message"])

    def test_filter_items_max_price_no_results(self):
        """It should return 404 with max_price in error message when no items match max_price filter"""
        # Create a wishlist with expensive items
        wishlist = self._create_wishlists(1)[0]
        expensive_item = WishlistItemFactory(product_price=Decimal("500.00"))

        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=expensive_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Search for items with max_price that won't match
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items?max_price=100")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Check that error message includes max_price information (correct format)
        data = resp.get_json()
        self.assertIn("max_price '100.0'", data["message"])

    def test_filter_items_price_range_no_results(self):
        """It should return 404 with both price filters in error message when no items match price range"""
        # Create a wishlist with items outside the search range
        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory(product_price=Decimal("500.00"))

        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Search for items in a price range that won't match
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items?min_price=50&max_price=100"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Check that error message includes both price filters (correct format)
        data = resp.get_json()
        self.assertIn("min_price '50.0'", data["message"])
        self.assertIn("max_price '100.0'", data["message"])

    def test_filter_items_combined_filters_with_prices_no_results(self):
        """It should return 404 with all filters in error message when no items match combined filters including prices"""
        # Create a wishlist with items that won't match the combined filters
        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory(
            category="electronics",
            product_price=Decimal("500.00"),
            product_name="iPhone",
        )

        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Search with combined filters that won't match
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items?category=food&product_name=Pizza&min_price=10&max_price=50"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Check that error message includes all filters (correct format)
        data = resp.get_json()
        self.assertIn("category 'food'", data["message"])  # Note: space, not =
        self.assertIn("product_name 'Pizza'", data["message"])  # Note: space, not =
        self.assertIn("min_price '10.0'", data["message"])  # Note: .0 decimal
        self.assertIn("max_price '50.0'", data["message"])  # Note: .0 decimal
