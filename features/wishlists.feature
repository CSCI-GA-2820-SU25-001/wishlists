Feature: Wishlist Management
    As an eCommerce manager
    I need to create a new wishlist or a new item using a web user interface
    So that I can efficiently manage customer wishlists or items without requiring direct access to the backend system.

    Background:
        Given I am on the "Home Page"

    Scenario: Successfully create a new wishlist
        When I fill in the "create_name" with "My Holiday Wishlist"
        And I fill in the "create_customer_id" with "123"
        And I fill in the "create_description" with "Gifts for the family"
        And I click the "create-btn" button
        Then I should see a success message containing "Success"

    Scenario: Attempt to create a wishlist with a duplicate name
        Given a wishlist named "Kitchen Appliances" already exists for customer "456"
        When I fill in the "create_name" with "Kitchen Appliances"
        And I fill in the "create_customer_id" with "456"
        And I click the "create-btn" button
        Then I should see an error message containing "already exists"

    Scenario: Attempt to create a wishlist with missing required data
        When I fill in the "create_name" with "My New Wishlist"
        And I leave the "create_customer_id" field empty
        And I click the "create-btn" button
        Then I should see an error message containing "Please fill in the following required fields"