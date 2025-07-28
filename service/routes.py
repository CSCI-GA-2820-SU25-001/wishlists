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
Wishlist Service with Swagger

This service implements a REST API that allows you to Create, Read, Update
and Delete Wishlists and WishlistItems
"""

from flask import request, url_for
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields, reqparse
from service.wishlist import Wishlist, WishlistItem, DataValidationError
from service.common import status  # HTTP Status Codes

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Wishlist REST API Service",
    description="This is a wishlist microservice that allows CRUD operations on wishlists and items",
    default="wishlists",
    default_label="Wishlist operations",
    doc="/apidocs",
    prefix="/api",
)


######################################################################
# Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """Handles Value Errors from bad data"""
    message = str(error)
    app.logger.error(message)
    return {
        "status_code": status.HTTP_400_BAD_REQUEST,
        "error": "Bad Request",
        "message": message,
    }, status.HTTP_400_BAD_REQUEST


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def index():
    """Index page"""
    return app.send_static_file("index.html")


@app.route("/health")
def health():
    """Health Check endpoint for Kubernetes probes"""
    return {"status": "OK"}, status.HTTP_200_OK


######################################################################
# Define Swagger Data Models
######################################################################

# Create models for Swagger documentation
wishlist_model = api.model(
    "Wishlist",
    {
        "id": fields.Integer(readOnly=True, description="Wishlist unique identifier"),
        "name": fields.String(required=True, description="The name of the wishlist"),
        "description": fields.String(description="Description of the wishlist"),
        "customer_id": fields.String(
            required=True, description="Customer ID who owns the wishlist"
        ),
        "is_public": fields.Boolean(description="Whether the wishlist is public"),
        "created_at": fields.DateTime(
            readOnly=True, description="When the wishlist was created"
        ),
        "updated_at": fields.DateTime(
            readOnly=True, description="When the wishlist was last updated"
        ),
    },
)

create_wishlist_model = api.model(
    "CreateWishlist",
    {
        "name": fields.String(required=True, description="The name of the wishlist"),
        "description": fields.String(description="Description of the wishlist"),
        "customer_id": fields.String(
            required=True, description="Customer ID who owns the wishlist"
        ),
        "is_public": fields.Boolean(
            description="Whether the wishlist is public", default=False
        ),
    },
)

wishlist_item_model = api.model(
    "WishlistItem",
    {
        "id": fields.Integer(readOnly=True, description="Item unique identifier"),
        "wishlist_id": fields.Integer(
            readOnly=True, description="Wishlist ID this item belongs to"
        ),
        "product_id": fields.String(required=True, description="Product ID"),
        "product_name": fields.String(required=True, description="Product name"),
        "product_description": fields.String(description="Product description"),
        "product_price": fields.Float(required=True, description="Product price"),
        "category": fields.String(description="Product category"),
        "quantity": fields.Integer(description="Quantity of the item", default=1),
        "likes": fields.Integer(readOnly=True, description="Number of likes"),
        "created_at": fields.DateTime(
            readOnly=True, description="When the item was created"
        ),
        "updated_at": fields.DateTime(
            readOnly=True, description="When the item was last updated"
        ),
    },
)

create_item_model = api.model(
    "CreateWishlistItem",
    {
        "product_id": fields.String(required=True, description="Product ID"),
        "product_name": fields.String(required=True, description="Product name"),
        "product_description": fields.String(description="Product description"),
        "product_price": fields.Float(required=True, description="Product price"),
        "category": fields.String(description="Product category"),
        "quantity": fields.Integer(description="Quantity of the item", default=1),
    },
)


######################################################################
# Wishlist Collection Resource
######################################################################
@api.route("/wishlists")
class WishlistCollection(Resource):
    """Handles all interactions with collections of Wishlists"""

    @api.doc("list_wishlists")
    @api.expect(
        api.parser()
        .add_argument(
            "customer_id", type=str, location="args", help="Filter by customer ID"
        )
        .add_argument(
            "name",
            type=str,
            location="args",
            help="Filter by wishlist name (partial match)",
        )
        .add_argument(
            "is_public",
            type=str,
            location="args",
            help="Filter by visibility (true/false)",
        )
    )
    @api.marshal_list_with(wishlist_model)
    def get(self):
        """
        List all Wishlists with optional filters

        This endpoint will return all wishlists unless a filter is provided
        """
        app.logger.info("Request for wishlist list")

        customer_id = request.args.get("customer_id")
        name = request.args.get("name")
        is_public = request.args.get("is_public")

        query = Wishlist.query

        if customer_id is not None:
            query = query.filter_by(customer_id=customer_id)

        if name:
            query = query.filter(Wishlist.name.ilike(f"%{name}%"))

        if is_public is not None:
            if is_public.lower() == "true":
                query = query.filter_by(is_public=True)
            elif is_public.lower() == "false":
                query = query.filter_by(is_public=False)
            else:
                api.abort(
                    status.HTTP_400_BAD_REQUEST, "is_public must be 'true' or 'false'"
                )

        wishlists = query.all()
        return [w.serialize() for w in wishlists], status.HTTP_200_OK

    @api.doc("create_wishlist")
    @api.expect(create_wishlist_model)
    @api.marshal_with(wishlist_model, code=201)
    def post(self):
        """
        Create a Wishlist
        This endpoint will create a Wishlist based the data in the body that is posted
        """
        app.logger.info("Request to create a Wishlist")

        wishlist = Wishlist()
        # Get the data from the request and deserialize it
        data = api.payload
        app.logger.info("Processing: %s", data)
        wishlist.deserialize(data)

        wishlist.create()
        app.logger.info("Wishlist with new id [%s] saved!", wishlist.id)

        # Return the serialized wishlist with 201 status
        return wishlist.serialize(), status.HTTP_201_CREATED


######################################################################
# Individual Wishlist Resource
######################################################################
@api.route("/wishlists/<int:wishlist_id>")
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistResource(Resource):
    """Handles all interactions with a single Wishlist"""

    @api.doc("get_wishlist")
    @api.marshal_with(wishlist_model)
    def get(self, wishlist_id):
        """
        Retrieve a single Wishlist
        This endpoint will return a Wishlist based on its ID
        """
        app.logger.info("Request for Wishlist with id: %s", wishlist_id)

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )

        return wishlist.serialize(), status.HTTP_200_OK

    @api.doc("update_wishlist")
    @api.expect(create_wishlist_model)
    @api.marshal_with(wishlist_model)
    def put(self, wishlist_id):
        """
        Update a Wishlist
        This endpoint will update a Wishlist based the body that is posted
        """
        app.logger.info("Request to update Wishlist with id: %s", wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )

        data = api.payload
        original_id = wishlist.id
        wishlist.deserialize(data)
        wishlist.id = original_id
        wishlist.update()
        app.logger.info("Wishlist with ID [%s] updated.", wishlist.id)

        return wishlist.serialize(), status.HTTP_200_OK

    @api.doc("delete_wishlist")
    def delete(self, wishlist_id):
        """
        Delete a Wishlist
        This endpoint will delete a Wishlist based the id specified in the path
        """
        app.logger.info("Request to delete Wishlist with id: %s", wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if wishlist:
            wishlist.delete()
            app.logger.info("Wishlist with ID [%s] delete complete.", wishlist_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
# Wishlist Items Collection Resource
######################################################################
@api.route("/wishlists/<int:wishlist_id>/items")
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistItemCollection(Resource):
    """Handles all interactions with collections of WishlistItems"""

    @api.doc("list_wishlist_items")
    @api.expect(
        api.parser()
        .add_argument(
            "product_name", type=str, location="args", help="Filter by product name"
        )
        .add_argument("category", type=str, location="args", help="Filter by category")
        .add_argument(
            "min_price", type=float, location="args", help="Filter by minimum price"
        )
        .add_argument(
            "max_price", type=float, location="args", help="Filter by maximum price"
        )
    )
    @api.marshal_list_with(wishlist_item_model)
    def get(self, wishlist_id):
        """
        List all items in a wishlist
        This endpoint will return a list of all items in a wishlist based on the wishlist ID
        """
        app.logger.info(
            "Request to list all items in wishlist with id: %s", wishlist_id
        )

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )

        # Get query parameters
        product_name = request.args.get("product_name")
        category = request.args.get("category")
        min_price = request.args.get("min_price", type=float)
        max_price = request.args.get("max_price", type=float)

        # Apply filters using your existing logic
        items = WishlistItem.find_with_filters(
            wishlist_id=wishlist_id,
            product_name=product_name,
            category=category,
            min_price=min_price,
            max_price=max_price,
        )

        return [item.serialize() for item in items], status.HTTP_200_OK

    @api.doc("create_wishlist_item")
    @api.expect(create_item_model)
    @api.marshal_with(wishlist_item_model, code=201)
    def post(self, wishlist_id):
        """
        Add an item to a wishlist
        This endpoint will add an item to a wishlist based on the data in the body
        """
        app.logger.info("Request to create item in Wishlist with id: %s", wishlist_id)

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )

        item = WishlistItem()
        data = api.payload
        data["wishlist_id"] = wishlist_id  # Set the wishlist_id from the URL
        app.logger.info("Processing: %s", data)
        item.deserialize(data)

        item.create()
        app.logger.info("Item with new id [%s] saved!", item.id)

        return item.serialize(), status.HTTP_201_CREATED


######################################################################
# Individual Wishlist Item Resource
######################################################################
@api.route("/wishlists/<int:wishlist_id>/items/<int:item_id>")
@api.param("wishlist_id", "The Wishlist identifier")
@api.param("item_id", "The WishlistItem identifier")
class WishlistItemResource(Resource):
    """Handles all interactions with a single WishlistItem"""

    @api.doc("get_wishlist_item")
    @api.marshal_with(wishlist_item_model)
    def get(self, wishlist_id, item_id):
        """
        Get an item from a wishlist
        This endpoint will return a WishlistItem based on its ID
        """
        app.logger.info("Request for item %s in wishlist %s", item_id, wishlist_id)

        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' could not be found in Wishlist with id '{wishlist_id}'.",
            )

        return item.serialize(), status.HTTP_200_OK

    @api.doc("update_wishlist_item")
    @api.expect(create_item_model)
    @api.marshal_with(wishlist_item_model)
    def put(self, wishlist_id, item_id):
        """
        Update an item in a wishlist
        This endpoint will update a WishlistItem based on the body that is posted
        """
        app.logger.info(
            "Request to update item %s in wishlist %s", item_id, wishlist_id
        )

        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' could not be found in Wishlist with id '{wishlist_id}'.",
            )

        data = api.payload
        data["wishlist_id"] = wishlist_id  # Ensure wishlist_id stays the same
        original_id = item.id
        item.deserialize(data)
        item.id = original_id
        item.update()
        app.logger.info("Item with ID [%s] updated.", item.id)

        return item.serialize(), status.HTTP_200_OK

    @api.doc("delete_wishlist_item")
    def delete(self, wishlist_id, item_id):
        """
        Remove an item from a wishlist
        This endpoint will delete a WishlistItem based on the id specified in the path
        """
        app.logger.info(
            "Request to delete item %s from wishlist %s", item_id, wishlist_id
        )

        item = WishlistItem.find(item_id)
        if item and item.wishlist_id == wishlist_id:
            item.delete()
            app.logger.info("Item with ID [%s] delete complete.", item_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
# Action Resources
######################################################################


@api.route("/wishlists/<int:wishlist_id>/clear")
@api.param("wishlist_id", "The Wishlist identifier")
class ClearWishlist(Resource):
    """Clear all items from a wishlist action"""

    @api.doc("clear_wishlist")
    def post(self, wishlist_id):
        """
        Clear all items from a wishlist
        This endpoint will remove all items from a wishlist but keep the wishlist itself
        """
        app.logger.info(
            "Request to clear all items from wishlist with id: %s", wishlist_id
        )

        # Check if the wishlist exists
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )

        # Remove all items from the wishlist
        for item in wishlist.wishlist_items[
            :
        ]:  # Use slice copy to avoid modifying list during iteration
            item.delete()

        app.logger.info("All items cleared from wishlist with id: %s", wishlist_id)

        return {
            "message": f"All items have been cleared from wishlist {wishlist_id}",
            "wishlist_id": wishlist_id,
            "items_remaining": 0,
        }, status.HTTP_200_OK


@api.route("/wishlists/<int:wishlist_id>/publish")
@api.param("wishlist_id", "The Wishlist identifier")
class PublishWishlist(Resource):
    """Publish a wishlist action"""

    @api.doc("publish_wishlist")
    def post(self, wishlist_id):
        """
        Publish a wishlist (make it public)
        This endpoint will set the wishlist's is_public flag to True
        """
        app.logger.info("Request to publish wishlist %s", wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )

        wishlist.is_public = True
        wishlist.update()

        return {
            "message": f"Wishlist {wishlist_id} published.",
            "wishlist_id": wishlist.id,
            "is_public": wishlist.is_public,
        }, status.HTTP_200_OK


@api.route("/wishlists/<int:wishlist_id>/unpublish")
@api.param("wishlist_id", "The Wishlist identifier")
class UnpublishWishlist(Resource):
    """Unpublish a wishlist action"""

    @api.doc("unpublish_wishlist")
    def post(self, wishlist_id):
        """
        Unpublish a wishlist (make it private)
        This endpoint will set the wishlist's is_public flag to False
        """
        app.logger.info("Request to unpublish wishlist %s", wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )

        wishlist.is_public = False
        wishlist.update()

        return {
            "message": f"Wishlist {wishlist_id} unpublished.",
            "wishlist_id": wishlist.id,
            "is_public": wishlist.is_public,
        }, status.HTTP_200_OK


@api.route("/wishlists/<int:wishlist_id>/items/<int:item_id>/like")
@api.param("wishlist_id", "The Wishlist identifier")
@api.param("item_id", "The WishlistItem identifier")
class LikeWishlistItem(Resource):
    """Like a wishlist item action"""

    @api.doc("like_wishlist_item")
    def post(self, wishlist_id, item_id):
        """
        Like an item in a wishlist
        This endpoint will increment the likes count for a wishlist item
        """
        app.logger.info("Request to like item %s in wishlist %s", item_id, wishlist_id)

        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' could not be found in Wishlist with id '{wishlist_id}'.",
            )

        item.likes = (item.likes or 0) + 1
        item.update()

        return {
            "message": f"Item {item_id} in wishlist {wishlist_id} liked.",
            "item_id": item.id,
            "wishlist_id": item.wishlist_id,
            "likes": item.likes,
        }, status.HTTP_200_OK


@api.route("/wishlists/<int:wishlist_id>/copy")
@api.param("wishlist_id", "The Wishlist identifier")
class CopyWishlist(Resource):
    """Copy a wishlist action"""

    @api.doc("copy_wishlist")
    def post(self, wishlist_id):
        """
        Copy a wishlist and all its items
        This endpoint will create a duplicate of the wishlist with all its items
        """
        app.logger.info("Request to copy wishlist %s", wishlist_id)

        original_wishlist = Wishlist.find(wishlist_id)
        if not original_wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )

        # Create a new wishlist with copied data
        new_wishlist = Wishlist()
        new_wishlist.name = f"Copy of {original_wishlist.name}"
        new_wishlist.description = original_wishlist.description
        new_wishlist.customer_id = original_wishlist.customer_id
        new_wishlist.is_public = False  # Copies are private by default
        new_wishlist.create()

        # Copy all items from the original wishlist
        for original_item in original_wishlist.wishlist_items:
            new_item = WishlistItem()
            new_item.wishlist_id = new_wishlist.id
            new_item.product_id = original_item.product_id
            new_item.product_name = original_item.product_name
            new_item.product_description = original_item.product_description
            new_item.product_price = original_item.product_price
            new_item.category = original_item.category
            new_item.quantity = original_item.quantity
            new_item.likes = 0  # Reset likes for copied items
            new_item.create()

        app.logger.info(
            "Wishlist %s copied to new wishlist %s", wishlist_id, new_wishlist.id
        )

        return {
            "message": f"Wishlist {wishlist_id} has been copied.",
            "original_wishlist_id": wishlist_id,
            "new_wishlist_id": new_wishlist.id,
            "new_wishlist_name": new_wishlist.name,
        }, status.HTTP_201_CREATED
