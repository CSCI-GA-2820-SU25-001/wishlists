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
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.wishlist import Wishlist, WishlistItem
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response - serve the admin UI"""
    return app.send_static_file("index.html")


######################################################################
# LIST ALL WISHLISTS
######################################################################
@app.route("/wishlists", methods=["GET"])
def list_wishlists():
    """
    List all Wishlists with optional filters

    Query Parameters:
    - customer_id: Filter wishlists by customer ID
    - name: Case-insensitive partial match on wishlist name

    Returns:
    List of serialized wishlist objects
    """
    app.logger.info("List all wishlists")

    customer_id = request.args.get("customer_id")
    name = request.args.get("name")
    is_public = request.args.get("is_public")

    wishlists = []  # Initialize to satisfy pylint

    if customer_id:
        app.logger.info("Find by customer_id: %s", customer_id)
        wishlists = Wishlist.find_for_user(customer_id)
    elif name:
        app.logger.info("Find by name: %s", name)
        wishlists = Wishlist.find_by_name(name)
    elif is_public is not None:
        if is_public.lower() == "true":
            wishlists = Wishlist.find_by_visibility(True)
        elif is_public.lower() == "false":
            wishlists = Wishlist.find_by_visibility(False)
        else:
            abort(status.HTTP_400_BAD_REQUEST, "is_public must be 'true' or 'false'")
    else:
        wishlists = Wishlist.all()

    results = []

    for wishlist in wishlists:
        data = wishlist.serialize()
        results.append(data)

    return jsonify(results), status.HTTP_200_OK


######################################################################
# READ A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["GET"])
def get_wishlist(wishlist_id):
    """
    Retrieve a single Wishlist
    This endpoint will return a Wishlist based on its ID.
    """
    app.logger.info("Request for Wishlist with id: %s", wishlist_id)

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    return jsonify(wishlist.serialize()), status.HTTP_200_OK


######################################################################
# CREATE A NEW WISHLIST
######################################################################
@app.route("/wishlists", methods=["POST"])
def create_wishlist():
    """
    Create a Wishlist
    This endpoint will create a Wishlist based the data in the body that is posted
    """
    app.logger.info("Request to Create a Wishlist...")
    check_content_type("application/json")

    wishlist = Wishlist()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    wishlist.deserialize(data)

    wishlist.create()
    app.logger.info("Wishlist with new id [%s] saved!", wishlist.id)

    # Return the location of the new Wishlist
    location_url = url_for("get_wishlist", wishlist_id=wishlist.id, _external=True)
    return (
        jsonify(wishlist.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# UPDATE AN EXISTING WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["PUT"])
def update_wishlist(wishlist_id):
    """
    Update a wishlist's name
    """
    app.logger.info("Request to update Wishlist with id: %s", wishlist_id)
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    data = request.get_json()
    original_id = wishlist.id
    wishlist.deserialize(data)
    wishlist.id = original_id
    wishlist.update()
    app.logger.info("Wishlist with ID [%s] updated.", wishlist.id)
    return jsonify(wishlist.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlist(wishlist_id):
    """
    Delete a Wishlist
    """
    app.logger.info("Request to delete wishlist with id: %s", wishlist_id)

    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()

    return "", 204


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health")
def healthcheck():
    """Returns service health status"""
    return jsonify({"status": "OK"}), 200


# ---------------------------------------------------------------------
#                I T E M   M E T H O D S
# ---------------------------------------------------------------------


######################################################################
# Helper Functions for LIST ALL ITEMS IN WISHLIST
######################################################################
def _parse_price_parameters():
    """Parse and validate price parameters from request args"""
    min_price_str = request.args.get("min_price")
    max_price_str = request.args.get("max_price")

    min_price = None
    max_price = None

    try:
        if min_price_str is not None:
            min_price = float(min_price_str)
        if max_price_str is not None:
            max_price = float(max_price_str)
    except ValueError:
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Invalid price parameters. min_price and max_price must be valid numbers.",
        )

    return min_price, max_price


def _build_filter_error_message(
    product_name, category, min_price, max_price, wishlist_id
):
    """Build error message for when no items match the filters"""
    filter_desc = []
    if product_name:
        filter_desc.append(f"product_name '{product_name}'")
    if category:
        filter_desc.append(f"category '{category}'")
    if min_price is not None:
        filter_desc.append(f"min_price '{min_price}'")
    if max_price is not None:
        filter_desc.append(f"max_price '{max_price}'")

    return f"No items found with filters: {', '.join(filter_desc)} in wishlist '{wishlist_id}'."


def _get_filtered_items(wishlist_id, product_name, category, min_price, max_price):
    """Get filtered items and handle empty results"""
    app.logger.info(
        "Filtering items in wishlist %s with: product_name: %s, category: %s, min_price: %s, max_price: %s",
        wishlist_id,
        product_name,
        category,
        min_price,
        max_price,
    )

    items = WishlistItem.find_with_filters(
        wishlist_id=wishlist_id,
        product_name=product_name,
        category=category,
        min_price=min_price,
        max_price=max_price,
    )

    if not items:
        error_message = _build_filter_error_message(
            product_name, category, min_price, max_price, wishlist_id
        )
        abort(status.HTTP_404_NOT_FOUND, error_message)

    return [item.serialize() for item in items]


######################################################################
# LIST ALL ITEMS IN WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["GET"])
def list_wishlist_items(wishlist_id):
    """
    List all items in a wishlist or search by product name
    This endpoint will return a list of all items in a wishlist based on the wishlist ID.

    Supported query parameters:
    - product_name: Filter items by product name.
    - category: Filter items by category.
    - min_price: Filter items with a minimum price.
    - max_price: Filter items with a maximum price.

    Examples:
    - /wishlists/1/items?category=electronics
    - /wishlists/1/items?min_price=100&max_price=500
    - /wishlists/1/items?category=food&min_price=10
    """
    app.logger.info("Request to list all items in wishlist with id: %s", wishlist_id)

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Extract query parameters for filtering
    product_name = request.args.get("product_name")
    category = request.args.get("category")
    min_price, max_price = _parse_price_parameters()

    # Check if any filtering parameters are provided
    has_filters = any(
        [product_name, category, min_price is not None, max_price is not None]
    )

    if has_filters:
        results = _get_filtered_items(
            wishlist_id, product_name, category, min_price, max_price
        )
    else:
        results = [
            wishlist_item.serialize() for wishlist_item in wishlist.wishlist_items
        ]

    # Return the list of items in the wishlist
    return jsonify(results), status.HTTP_200_OK


######################################################################
# ADD AN ITEM TO WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["POST"])
def add_item_to_wishlist(wishlist_id):
    """
    Add an item to a wishlist
    This endpoint will add an item to a wishlist based on the wishlist ID.
    """
    app.logger.info("Request to create an Address for Account with id: %s", wishlist_id)
    check_content_type("application/json")

    # See if the account exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Create an item from the json data
    wishlist_item = WishlistItem()
    wishlist_item.deserialize(request.get_json())

    # Append the address to the account
    wishlist.wishlist_items.append(wishlist_item)
    wishlist.update()

    # Prepare a message to return
    message = wishlist_item.serialize()

    # Send the location to GET the new item
    location_url = url_for(
        "get_wishlist_item",
        wishlist_id=wishlist.id,
        item_id=wishlist_item.id,
        _external=True,
    )
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# Update AN ITEM FROM WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["PUT"])
def update_wishlist_item(wishlist_id, item_id):
    """
    Update a Wishlist Item
    This endpoint will update a wishlist item based on the body that is posted
    """
    app.logger.info("Request to update Item %s for Wishlist %s", item_id, wishlist_id)
    check_content_type("application/json")

    # See if the item exists and abort if it doesn't
    item = WishlistItem.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found.",
        )

    # Make sure the item belongs to the correct wishlist
    if item.wishlist_id != wishlist_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found in Wishlist with id '{wishlist_id}'.",
        )

    # Update from the json in the body of the request, but don't change the ID or wishlist_id
    original_id = item.id
    original_wishlist_id = item.wishlist_id
    item.deserialize(request.get_json())
    item.id = original_id
    item.wishlist_id = original_wishlist_id
    item.update()

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# Remove AN ITEM FROM WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["DELETE"])
def delete_wishlist_item(wishlist_id, item_id):
    """
    Remove an item from a wishlist
    """
    app.logger.info("Request to delete item %s from wishlist %s", item_id, wishlist_id)
    item = WishlistItem.find(item_id)
    if not item or item.wishlist_id != wishlist_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found in Wishlist with id '{wishlist_id}'.",
        )
    item.delete()
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# GET A WISHLIST ITEM
######################################################################
@app.route(
    "/wishlists/<int:wishlist_id>/items/<int:item_id>",
    methods=["GET"],
)
def get_wishlist_item(wishlist_id, item_id):
    """
    Get a single wishlist item from a wishlist
    """
    app.logger.info(
        "Request to get wishlist item %s from wishlist %s",
        item_id,
        wishlist_id,
    )

    # See if the wishlist item exists and abort if it doesn't
    wishlist_item = WishlistItem.find(item_id)
    if not wishlist_item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist item with id '{item_id}' could not be found in wishlist '{wishlist_id}'.",
        )

    return jsonify(wishlist_item.serialize()), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
#  A C T I O N   F U N C T I O N S
######################################################################


@app.route("/wishlists/<int:wishlist_id>/clear", methods=["POST"])
def clear_wishlist(wishlist_id):
    """
    Clear all items from a wishlist
    This endpoint will remove all items from a wishlist but keep the wishlist itself.
    This is an Action endpoint that performs a stateful operation beyond CRUD.
    """
    app.logger.info("Request to clear all items from wishlist with id: %s", wishlist_id)

    # Check if the wishlist exists
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Remove all items from the wishlist
    for item in wishlist.wishlist_items[
        :
    ]:  # Use slice copy to avoid modifying list during iteration
        item.delete()

    app.logger.info("All items cleared from wishlist with id: %s", wishlist_id)

    return (
        jsonify(
            {
                "message": f"All items have been cleared from wishlist {wishlist_id}",
                "wishlist_id": wishlist_id,
                "items_remaining": 0,
            }
        ),
        status.HTTP_200_OK,
    )


######################################################################
# Make it public (ACTION)
######################################################################
@app.route("/wishlists/<int:wishlist_id>/publish", methods=["POST"])
def publish_wishlist(wishlist_id):
    """
    Action: Publish a wishlist (set is_public to True)
    """
    app.logger.info("Request to publish wishlist %s", wishlist_id)
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )
    wishlist.is_public = True
    wishlist.update()
    return (
        jsonify(
            {
                "message": f"Wishlist {wishlist_id} published.",
                "wishlist_id": wishlist.id,
                "is_public": wishlist.is_public,
            }
        ),
        status.HTTP_200_OK,
    )


######################################################################
# Make it private (ACTION)
######################################################################
@app.route("/wishlists/<int:wishlist_id>/unpublish", methods=["POST"])
def unpublish_wishlist(wishlist_id):
    """
    Action: Unpublish a wishlist (set is_public to False)
    """
    app.logger.info("Request to unpublish wishlist %s", wishlist_id)
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )
    wishlist.is_public = False
    wishlist.update()
    return (
        jsonify(
            {
                "message": f"Wishlist {wishlist_id} unpublished.",
                "wishlist_id": wishlist.id,
                "is_public": wishlist.is_public,
            }
        ),
        status.HTTP_200_OK,
    )


######################################################################
# Like a wishlist (ACTION)
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>/like", methods=["POST"])
def like_wishlist_item(wishlist_id, item_id):
    """
    Action: Like a product in a wishlist
    """
    app.logger.info("Request to like item %s in wishlist %s", item_id, wishlist_id)
    item = WishlistItem.find(item_id)
    if not item or item.wishlist_id != wishlist_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found in Wishlist with id '{wishlist_id}'.",
        )
    item.likes = (item.likes or 0) + 1
    item.update()
    return (
        jsonify(
            {
                "message": f"Item {item_id} in wishlist {wishlist_id} liked.",
                "item_id": item.id,
                "wishlist_id": item.wishlist_id,
                "likes": item.likes,
            }
        ),
        status.HTTP_200_OK,
    )


######################################################################
# Copy a wishlist (ACTION)
######################################################################
@app.route("/wishlists/<int:wishlist_id>/copy", methods=["POST"])
def copy_wishlist(wishlist_id):
    """
    Action: Copy a wishlist and all its items
    """
    app.logger.info("Request to copy wishlist %s", wishlist_id)
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )
    # Create a new wishlist with similar attributes
    new_wishlist = Wishlist(
        name=f"{wishlist.name} (Copy)",
        description=wishlist.description,
        customer_id=wishlist.customer_id,
        is_public=wishlist.is_public,
    )
    new_wishlist.create()
    # Copy all items
    for item in wishlist.wishlist_items:
        new_item = WishlistItem(
            wishlist_id=new_wishlist.id,
            product_id=item.product_id,
            product_name=item.product_name,
            product_description=item.product_description,
            product_price=item.product_price,
            category=item.category,
            quantity=item.quantity,
            likes=item.likes,
        )
        new_item.create()
    app.logger.info(
        "Wishlist %s copied to new wishlist %s", wishlist_id, new_wishlist.id
    )
    return (
        jsonify(
            {
                "message": f"Wishlist {wishlist_id} copied to new wishlist {new_wishlist.id}.",
                "original_wishlist_id": wishlist_id,
                "new_wishlist_id": new_wishlist.id,
                "wishlist": new_wishlist.serialize(),
            }
        ),
        status.HTTP_201_CREATED,
    )
