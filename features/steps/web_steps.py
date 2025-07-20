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
    
@given('I am on the "Home Page"')
def step_impl(context):
    """ Navigate to the Home Page """
    context.driver.get(context.base_url)

@when('I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)

@when('I fill in the "{element_id}" with "{value}"')
def step_impl(context, element_id, value):
    """ Fills in a form input field by its ID """
    # Use the element_id directly from the Gherkin step
    # e.g., "create_name" or "create_customer_id"
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(value)

@when('I leave the "{element_id}" field empty')
def step_impl(context, element_id):
    """ Clears a form input field by its ID """
    element = context.driver.find_element(By.ID, element_id)
    element.clear()

@when('I click the "{button_id}" button')
def step_impl(context, button_id):
    """ Clicks a button by its ID """
    # e.g., "create-btn" or "list-all-btn"
    button = context.driver.find_element(By.ID, button_id)
    button.click()

@then('I should see a success message containing "{message}"')
def step_impl(context, message):
    """ Checks for a success message in the flash notification """
    # Wait for flash message to appear with success class
    def flash_success_visible(driver):
        flash_div = driver.find_element(By.ID, 'flash_message')
        if flash_div and "flash-success" in flash_div.get_attribute("class"):
            return flash_div
        return False
    
    flash_div = WebDriverWait(context.driver, WAIT_SECONDS).until(flash_success_visible)
    
    # Check that the text contains the expected message
    flash_text = flash_div.find_element(By.ID, 'flash_text')
    assert message in flash_text.text

@then('I should see an error message containing "{message}"')
def step_impl(context, message):
    """ Checks for an error message in the flash notification """
    flash_div = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.visibility_of_element_located((By.ID, 'flash_message'))
    )
    # Check that the div has the 'flash-error' class
    assert "flash-error" in flash_div.get_attribute("class")
    # Check that the text contains the expected message
    flash_text = flash_div.find_element(By.ID, 'flash_text')
    assert message in flash_text.text

@then('I should see "{wishlist_name}" in the results table')
def step_impl(context, wishlist_name):
    """ Verifies that a new wishlist appears in the results table """
    results_table_body = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.visibility_of_element_located((By.ID, 'results-body'))
    )
    # Find a table cell (td) within the results table that contains the wishlist name
    assert wishlist_name in results_table_body.text, f"Wishlist '{wishlist_name}' not found in results"

@then('I should see that the results table is empty')
def step_impl(context):
    """ Verifies that no results are shown in the table """
    results_table_body = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.visibility_of_element_located((By.ID, 'results-body'))
    )
    # Check for the "No wishlists found" message
    assert "No wishlists found" in results_table_body.text