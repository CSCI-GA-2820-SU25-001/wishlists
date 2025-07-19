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
from behave import given # pylint: disable=no-name-in-module

# This should be the base URL for your API
API_URL = "http://localhost:8080/wishlists"

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60

@given('a wishlist named "{name}" already exists for customer "{customer_id}"')
def step_impl(context, name, customer_id):
    """
    Creates a wishlist directly via the API to set up the test condition.
    """
    # clean up any old wishlists to ensure a fresh start
    context.resp = requests.get(API_URL, timeout=WAIT_TIMEOUT)
    if context.resp.status_code == HTTP_200_OK:
        for wishlist in context.resp.json():
            requests.delete(f"{API_URL}/{wishlist['id']}", timeout=WAIT_TIMEOUT)

    # create the specific wishlist needed for the test
    headers = {'Content-Type': 'application/json'}
    payload = {
        "name": name,
        "customer_id": customer_id,
        "is_public": False,
        "description": "Pre-existing wishlist for BDD test setup"
    }
    context.resp = requests.post(API_URL, json=payload, headers=headers, timeout=WAIT_TIMEOUT)
    assert context.resp.status_code == HTTP_201_CREATED, "Failed to create prerequisite wishlist via API"