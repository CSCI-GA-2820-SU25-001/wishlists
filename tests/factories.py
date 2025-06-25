"""
Factory file to create fake datasets of wishlists and wishlists_items for ease in application testing
"""

from datetime import datetime, timezone
from decimal import Decimal
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDateTime, FuzzyInteger
from service.wishlist import Wishlist, WishlistItem


class WishlistFactory(factory.Factory):
    """Loading fake wishlists"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Wishlist

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("word")
    description = factory.Faker("sentence")
    customer_id = factory.Faker("word")
    created_at = FuzzyDateTime(datetime(2000, 1, 1, tzinfo=timezone.utc))
    updated_at = FuzzyDateTime(datetime(2000, 1, 1, tzinfo=timezone.utc))
    is_public = FuzzyChoice(choices=[True, False])

    @factory.post_generation
    def wishlist_items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the wishlist items list"""
        if not create:
            return

        if extracted:
            self.wishlist_items = extracted


class WishlistItemFactory(factory.Factory):
    """Loading fake wishlist items from factory"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Maps"""

        model = WishlistItem

    id = factory.Sequence(lambda n: n)
    wishlist_id = factory.Faker("random_int", min=1, max=9999)
    product_id = factory.Faker("random_int", min=1, max=9999)
    product_name = factory.Faker("word")
    product_description = factory.Faker("sentence")
    # Added quantity with a random integer between 1 and 10
    quantity = FuzzyInteger(1, 10)
    product_price = factory.Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True,
        min_value=Decimal("10.00"),
        max_value=Decimal("1000.00"),
    )
    created_at = FuzzyDateTime(datetime(2000, 1, 1, tzinfo=timezone.utc))
    updated_at = FuzzyDateTime(datetime(2000, 1, 1, tzinfo=timezone.utc))
    wishlist = factory.SubFactory(WishlistFactory)
