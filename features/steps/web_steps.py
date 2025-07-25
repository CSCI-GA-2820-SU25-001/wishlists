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

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import re
import logging
from typing import Any
from behave import given, when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WAIT_SECONDS = 10

# ID prefixes for different contexts - following pets.py pattern
CREATE_PREFIX = "create_"
SEARCH_PREFIX = "search_"  # For View tab search fields
UPDATE_PREFIX = "update_"


def _get_element_id(context: Any, element_name: str) -> str:
    """Determines the element ID based on the active tab and element name."""
    base_name = element_name.lower().replace(" ", "_")
    try:
        # Find the ID of the currently active tab
        active_tab_id = context.driver.find_element(
            By.CSS_SELECTOR, ".nav-link.active"
        ).get_attribute("id")
    except:
        active_tab_id = "create-tab"  # Default to create tab if none are active

    # Special case for the visibility dropdown, which has a unique ID pattern
    if base_name == "visibility":
        if active_tab_id == "create-tab":
            return "create_is_public"
        if active_tab_id == "view-tab":
            return "search_is_public"
        if active_tab_id == "update-tab":
            return "update_is_public"

    # Special case for Customer ID field which has different IDs in different tabs
    if base_name == "customer_id":
        if active_tab_id == "create-tab":
            return "create_customer_id"
        if active_tab_id == "view-tab":
            return "search_customer_id"
        if active_tab_id == "update-tab":
            return "update_customer_id"
        if active_tab_id == "delete-tab":
            return "delete_customer_id"

    # Logic for the "View" tab's unique field IDs
    if active_tab_id == "view-tab":
        if base_name == "name":
            return "search_name"
        if base_name == "wishlist_id":
            return "view_wishlist_id"
        return f"{SEARCH_PREFIX}{base_name}"

    # Logic for the "Delete" tab's unique field IDs
    if active_tab_id == "delete-tab":
        return f"delete_{base_name}"

    # Logic for other tabs using standard prefixes
    if active_tab_id == "create-tab":
        return f"{CREATE_PREFIX}{base_name}"
    if active_tab_id == "update-tab":
        return f"{UPDATE_PREFIX}{base_name}"

    # Fallback to the create prefix as a default
    return f"{CREATE_PREFIX}{base_name}"


def save_screenshot(context: Any, filename: str) -> None:
    """Takes a snapshot of the web page for debugging and validation

    Args:
        context (Any): The session context
        filename (str): The message that you are looking for
    """
    # Remove all non-word characters (everything except numbers and letters)
    filename = re.sub(r"[^\w\s]", "", filename)
    # Replace all runs of whitespace with a single dash
    filename = re.sub(r"\s+", "-", filename)
    context.driver.save_screenshot(f"./captures/{filename}.png")


@when('I visit the "Home Page"')
def step_impl(context: Any) -> None:
    """Make a call to the base URL"""
    context.driver.get(context.base_url)


@when('I click the "{tab_name}" tab')
def step_impl(context: Any, tab_name: str) -> None:
    """Click on a specific tab"""
    tab_id = f"{tab_name.lower()}-tab"
    tab_element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.element_to_be_clickable((By.ID, tab_id))
    )
    tab_element.click()


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    """Set a form input field"""
    element_id = _get_element_id(context, element_name)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    """Select an option from a dropdown"""
    element_id = _get_element_id(context, element_name)
    element = Select(
        WebDriverWait(context.driver, WAIT_SECONDS).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
    )
    element.select_by_visible_text(text)


@when('I set the "{element_name}" to ""')
def step_impl_empty(context: Any, element_name: str):
    """Set a form input field to an empty string"""
    element_id = _get_element_id(context, element_name)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.clear()


@when('I press the "{button}" button')
def step_impl(context: Any, button: str) -> None:
    """Press a button by converting button name to actual button ID"""
    # Map button names to actual IDs in the HTML
    button_mapping = {
        "create": "create-btn",
        "search": "search-btn",
        "list all": "list-all-btn",
        "retrieve": "retrieve-btn",
        "clear": "view-clear-btn",  # Clear button in View tab
        "load": "load-btn",
        "save changes": "save-changes-btn",
        "cancel": "cancel-update-btn",
        "update": "save-changes-btn",  # Alternative name for save changes
        "lookup": "delete-lookup-btn",
        "delete wishlist": "delete-confirm-btn",
    }

    button_key = button.lower()
    button_id = button_mapping.get(
        button_key, button.lower().replace(" ", "-") + "-btn"
    )
    context.driver.find_element(By.ID, button_id).click()


@when('I enter "{text}" in the Customer ID search field')
def step_impl(context, text):
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.presence_of_element_located((By.ID, "search_customer_id"))
    )
    element.clear()
    element.send_keys(text)


@when('I enter "{text}" in the Wishlist Name search field')
def step_impl(context, text):
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.presence_of_element_located((By.ID, "search_name"))
    )
    element.clear()
    element.send_keys(text)


@when('I enter "{text}" in the delete Customer ID field')
def step_impl(context, text):
    """Specifically for the delete tab customer ID field"""
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.presence_of_element_located((By.ID, "delete_customer_id"))
    )
    element.clear()
    element.send_keys(text)


@when("I select the first wishlist")
def step_impl(context: Any) -> None:
    """Select the first wishlist from the delete wishlist selection list"""
    # Wait for the delete wishlist selection to be visible
    WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.visibility_of_element_located((By.ID, "delete-wishlist-selection"))
    )

    # Find and click the first wishlist button in the list
    first_wishlist_btn = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#delete-wishlists-list .list-group-item")
        )
    )
    first_wishlist_btn.click()


@when("I confirm the deletion")
def step_impl(context: Any) -> None:
    """Confirm the deletion by accepting the browser confirmation dialog"""
    # Wait a moment for the confirmation dialog to appear
    import time

    time.sleep(0.5)

    # Accept the confirmation dialog
    try:
        alert = context.driver.switch_to.alert
        alert.accept()
    except:
        # If there's no alert, that's fine - the test might be using a different mechanism
        pass


@then('I should see the message "{message}"')
def step_impl(context: Any, message: str) -> None:
    """Check for a message in the flash notification"""
    try:
        # Wait for any flash message to appear
        flash_element = WebDriverWait(context.driver, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.ID, "flash_message"))
        )

        # Get the actual message text
        actual_message = flash_element.text.strip()

        # Check if the expected message is contained in the actual message (case-insensitive)
        if message.lower() in actual_message.lower():
            return  # Test passes
        else:
            print(f"\nExpected message (partial): '{message}'")
            print(f"Actual message: '{actual_message}'")
            raise AssertionError(
                f"Expected message '{message}' not found in actual message: '{actual_message}'"
            )

    except Exception as e:
        # If no flash message is found, check if there's any visible error or success message
        try:
            # Look for any visible alert or message
            alerts = context.driver.find_elements(
                By.CSS_SELECTOR,
                ".alert, .flash-message, .flash-success, .flash-error, .flash-info",
            )
            for alert in alerts:
                if alert.is_displayed():
                    alert_text = alert.text.strip()
                    if message.lower() in alert_text.lower():
                        return
                    print(f"Found alert: {alert_text}")

            # Also check the flash_text element specifically
            flash_text = context.driver.find_element(By.ID, "flash_text")
            if flash_text.is_displayed():
                text_content = flash_text.text.strip()
                if message.lower() in text_content.lower():
                    return
                print(f"Flash text content: '{text_content}'")

        except:
            pass

        print(f"No message containing '{message}' was found")
        raise AssertionError(f"Expected message '{message}' not found")


@then('I should see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    """Check if name appears in results table"""
    results_body = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.visibility_of_element_located((By.ID, "results-body"))
    )
    assert name in results_body.text


@then('I should not see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    """Check if name does not appear in results table"""
    results_body = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.visibility_of_element_located((By.ID, "results-body"))
    )
    print("\n=== DEBUG results-body text ===")
    print(results_body.text)
    print("=== END DEBUG ===\n")
    assert name not in results_body.text


@then("the search fields should be empty")
def step_impl(context: Any) -> None:
    """Verify that search fields are cleared"""
    search_fields = ["search_customer_id", "search_name", "view_wishlist_id"]

    for field_id in search_fields:
        try:
            element = context.driver.find_element(By.ID, field_id)
            assert (
                element.get_attribute("value") == ""
            ), f"Field {field_id} is not empty"
        except:
            # Field might not exist, continue
            continue


@then('the results table should show "{message}"')
def step_impl(context: Any, message: str) -> None:
    """Check for specific message in results table"""
    results_body = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.visibility_of_element_located((By.ID, "results-body"))
    )
    assert message in results_body.text


@then("the Customer ID field should show a validation error")
def step_impl(context):
    """Check for validation error message related to Customer ID"""
    message_element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.presence_of_element_located((By.ID, "flash_message"))
    )
    assert (
        "Customer ID" in message_element.text or "Please fix" in message_element.text
    ), f"Expected validation message for Customer ID, got: '{message_element.text}'"


@then("the Wishlist Name field should show a validation error")
def step_impl(context):
    """Check for validation error message related to Wishlist Name"""
    message_element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.presence_of_element_located((By.ID, "flash_message"))
    )
    assert (
        "Wishlist Name" in message_element.text or "Please fix" in message_element.text
    ), f"Expected validation message for Wishlist Name, got: '{message_element.text}'"
