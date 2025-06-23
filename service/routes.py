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
from service.wishlist import Wishlist, WishlistItem, DataValidationError
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return jsonify(name="Wishlist REST API Service", version="1.0"), status.HTTP_200_OK


######################################################################
# LIST ALL WISHLISTS
######################################################################


######################################################################
# READ A WISHLIST
######################################################################
# NOT FINISHED, JUST A SKELETON
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

    # Save the new Wishlist to the database
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


######################################################################
# DELETE A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlist(wishlist_id):
    """Delete a wishlist by ID"""
    app.logger.info("Request to delete wishlist with id: %s", wishlist_id)

    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(404, f"Wishlist with id '{wishlist_id}' was not found.")

    wishlist.delete()
    return "", 204

######################################################################
# ADD AN ITEM TO WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/wishlist_items", methods=["POST"])
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
        wishlist_item_id=wishlist_item.id,
        _external=True
    )
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# GET A WISHLIST ITEM
######################################################################
@app.route("/wishlists/<int:wishlist_id>/wishlist_items/<int:wishlist_item_id>", methods=["GET"])
def get_wishlist_item(wishlist_id, wishlist_item_id):
    """
    Get a single wishlist item from a wishlist
    """
    app.logger.info("Request to get wishlist item %s from wishlist %s", wishlist_item_id, wishlist_id)
    
    # See if the wishlist item exists and abort if it doesn't
    wishlist_item = WishlistItem.find(wishlist_item_id)
    if not wishlist_item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist item with id '{wishlist_item_id}' could not be found in wishlist '{wishlist_id}'.",
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


# Todo: Place your REST API code here ...
