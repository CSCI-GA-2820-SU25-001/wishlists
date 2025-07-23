Feature: Wishlist Management
    As an eCommerce manager
    I need to create and update wishlists using a web user interface
    So that I can efficiently manage customer wishlists without requiring direct access to the backend system.

    Background:
        Given the following wishlists
            | name              | customer_id | description        | is_public |
            | Holiday Shopping  | 123         | Christmas gifts    | True      |
            | Kitchen Appliances| 456         | New kitchen items  | False     |
        When I visit the "Home Page"

    Scenario: Create a new wishlist
        When I set the "Name" to "Birthday List"
        And I set the "Customer Id" to "789"
        And I set the "Description" to "Birthday gifts for family"
        And I select "Public" in the "Visibility" dropdown
        And I press the "Create" button
        Then I should see the message "Success"

    Scenario: Create a wishlist with minimal information
        When I set the "Name" to "Simple List"
        And I set the "Customer Id" to "999"
        And I press the "Create" button
        Then I should see the message "Success"

    Scenario: Attempt to create a wishlist with duplicate name
        When I set the "Name" to "Kitchen Appliances"
        And I set the "Customer Id" to "456"
        And I press the "Create" button
        Then I should see the message "already exists"

    Scenario: Attempt to create a wishlist with missing required fields
        When I set the "Name" to ""
        And I set the "Customer Id" to "999"
        And I press the "Create" button
        Then I should see the message "Please fill in the following required fields"

    Scenario: View and search wishlists
        When I click the "View" tab
        And I press the "List All" button
        Then I should see the message "Success"
        And I should see "Holiday Shopping" in the results
        And I should see "Kitchen Appliances" in the results

    Scenario: Search for wishlists by customer
        When I click the "View" tab
        And I set the "Customer Id" to "123"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "Holiday Shopping" in the results

    Scenario: Search for wishlists by name
        When I click the "View" tab
        And I set the "Name" to "Holiday Shopping"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "Holiday Shopping" in the results

    Scenario: Search a specific wishlist by Customer ID and Wishlist Name
        When I click the "View" tab
        And I set the "Customer Id" to "123"
        And I set the "Name" to "Holiday Shopping"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "Holiday Shopping" in the results
        And I should not see "Kitchen Appliances" in the results

    Scenario: Clear search results
        When I click the "View" tab
        And I set the "Name" to "Holiday Shopping"
        And I press the "Search" button
        Then I should see the message "Success"
        When I press the "Clear" button
        Then the search fields should be empty
        And the results table should show "No results to display"

    Scenario: Show validation error when Customer ID is invalid
        When I click the "View" tab
        And I enter "!!@" in the Customer ID search field
        And I press the "Search" button
        Then the Customer ID field should show a validation error

    Scenario: Show validation error when Wishlist Name is invalid
        When I click the "View" tab
        And I enter "<script>" in the Wishlist Name search field
        And I press the "Search" button
        Then the Wishlist Name field should show a validation error

    Scenario: Look up wishlists for deletion
        When I click the "Delete" tab
        And I enter "123" in the delete Customer ID field
        And I press the "Lookup" button
        Then I should see the message "Success"

    Scenario: Attempt to delete a non-existent wishlist  
        When I click the "Delete" tab
        And I enter "999" in the delete Customer ID field
        And I press the "Lookup" button
        Then I should see the message "No wishlists found"

    Scenario: Attempt to delete without providing required information
        When I click the "Delete" tab
        And I press the "Lookup" button
        Then I should see the message "Please enter a Customer ID"
        