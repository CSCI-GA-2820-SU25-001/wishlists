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
Wishlist Steps

Steps file for setting up Wishlist data.
This file should only contain steps that interact with the API to set up preconditions.
"""
import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given("the following wishlists")
def step_impl(context):
    """Delete all Wishlists and load new ones from data table"""

    # Get a list of all wishlists
    rest_endpoint = f"{context.base_url}/api/wishlists"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)

    # Delete them one by one
    for wishlist in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{wishlist['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # Load the database with new wishlists from the data table
    for row in context.table:
        payload = {
            "name": row["name"],
            "customer_id": str(row["customer_id"]),
            "description": row["description"],
            "is_public": row["is_public"] in ["True", "true", "1"],
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)


@given('a wishlist named "{name}" already exists for customer "{customer_id}"')
def step_impl(context, name, customer_id):
    """
    Creates a single wishlist directly via the API to set up the test condition.
    """
    # Clean up any old wishlists to ensure a fresh start
    rest_endpoint = f"{context.base_url}/api/wishlists"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    if context.resp.status_code == HTTP_200_OK:
        for wishlist in context.resp.json():
            requests.delete(f"{rest_endpoint}/{wishlist['id']}", timeout=WAIT_TIMEOUT)

    # Create the specific wishlist needed for the test
    headers = {"Content-Type": "application/json"}
    payload = {
        "name": name,
        "customer_id": customer_id,
        "is_public": False,
        "description": "Pre-existing wishlist for BDD test setup",
    }
    context.resp = requests.post(
        rest_endpoint, json=payload, headers=headers, timeout=WAIT_TIMEOUT
    )
    expect(context.resp.status_code).equal_to(HTTP_201_CREATED)
