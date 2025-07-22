$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Show flash message with type (success, error, info)
    function flash_message(message, type = 'info') {
        const flashDiv = $("#flash_message");
        const flashText = $("#flash_text");

        // Remove any existing classes
        flashDiv.removeClass('flash-success flash-error flash-info');

        // Add appropriate class and show message
        flashDiv.addClass(`flash-${type}`);
        flashText.text(message);
        flashDiv.fadeIn();

        // Auto-hide after 5 seconds for success/info messages
        if (type !== 'error') {
            setTimeout(() => {
                flashDiv.fadeOut();
            }, 5000);
        }
    }

    // Clear all form fields in a specific tab
    function clear_form(tabId) {
        $(`#${tabId} input[type="text"]`).val('');
        $(`#${tabId} textarea`).val('');
        $(`#${tabId} input[type="checkbox"]`).prop('checked', false);
        $(`#${tabId} select`).prop('selectedIndex', 0);
        // Remove any error styling
        $(`#${tabId} .has-error`).removeClass('has-error');
    }

    // Validate required fields
    function validate_required_fields(fields) {
        let isValid = true;
        let missingFields = [];

        // Clear any existing error styling first
        fields.forEach(field => {
            $(`#${field.id}`).removeClass('has-error');
        });

        fields.forEach(field => {
            const value = $(`#${field.id}`).val().trim();
            if (!value) {
                isValid = false;
                missingFields.push(field.name);
                $(`#${field.id}`).addClass('has-error');
            }
        });

        if (!isValid) {
            flash_message(`Please fill in the following required fields: ${missingFields.join(', ')}`, 'error');
        }

        return isValid;
    }

    // Validate wishlist name format
    function validate_wishlist_name(name) {
        // Clear any existing error styling
        $("#create_name").removeClass('has-error');

        // Basic validation: minimum length
        if (name.length < 2) {
            flash_message("Wishlist name must be at least 2 characters long.", 'error');
            $("#create_name").addClass('has-error');
            return false;
        }

        // Maximum length validation
        if (name.length > 100) {
            flash_message("Wishlist name must be less than 100 characters.", 'error');
            $("#create_name").addClass('has-error');
            return false;
        }

        // Check for invalid characters
        const invalidChars = /[<>\"'&]/;
        if (invalidChars.test(name)) {
            flash_message("Wishlist name contains invalid characters. Please avoid: < > \" ' &", 'error');
            $("#create_name").addClass('has-error');
            return false;
        }

        return true;
    }

    // Check for duplicate wishlist names
    function check_duplicate_wishlist(customerId, wishlistName, callback) {
        const ajax_check = $.ajax({
            type: "GET",
            url: `/wishlists?customer_id=${encodeURIComponent(customerId)}`,
            contentType: "application/json",
        });

        ajax_check.done(function (existingWishlists) {
            // Check if any existing wishlists have the same name (case-insensitive)
            const duplicateExists = existingWishlists.some(wishlist =>
                wishlist.name.toLowerCase() === wishlistName.toLowerCase()
            );

            if (duplicateExists) {
                flash_message(`Error: A wishlist named '${wishlistName}' already exists for this customer. Please choose a different name.`, 'error');
                $("#create_name").addClass('has-error');
                callback(false);
            } else {
                callback(true);
            }
        });

        ajax_check.fail(function (res) {
            // If the check fails, log it but still proceed
            console.warn("Could not check for duplicate wishlist names:", res);
            callback(true); // Allow creation to proceed
        });
    }

    // Format date for display
    function format_date(dateString) {
        try {
            return new Date(dateString).toLocaleDateString();
        } catch (e) {
            return dateString;
        }
    }

    // ****************************************
    //  C R E A T E   F U N C T I O N A L I T Y
    // ****************************************

    $("#create-btn").click(function () {
        // Disable the button and show loading state
        const createBtn = $(this);
        const originalText = createBtn.html();
        createBtn.prop('disabled', true).html('<span class="loading-spinner"></span> Creating...');

        // Validate required fields
        const requiredFields = [
            { id: 'create_name', name: 'Wishlist Name' },
            { id: 'create_customer_id', name: 'Customer ID' }
        ];

        if (!validate_required_fields(requiredFields)) {
            createBtn.prop('disabled', false).html(originalText);
            return;
        }

        const wishlistName = $("#create_name").val().trim();
        const customerId = $("#create_customer_id").val().trim();

        // Validate wishlist name format
        if (!validate_wishlist_name(wishlistName)) {
            createBtn.prop('disabled', false).html(originalText);
            return;
        }

        // Check for duplicate wishlist names
        check_duplicate_wishlist(customerId, wishlistName, function (isUnique) {
            if (!isUnique) {
                createBtn.prop('disabled', false).html(originalText);
                return;
            }

            // Proceed with creation
            createWishlist(createBtn, wishlistName, originalText);
        });
    });

    // Separated creation logic for better organization
    function createWishlist(createBtn, wishlistName, originalText) {
        // Gather form data
        const data = {
            name: $("#create_name").val().trim(),
            customer_id: $("#create_customer_id").val().trim(),
            description: $("#create_description").val().trim(),
            is_public: $("#create_is_public").val() === "true"
        };

        // Clear any existing messages
        $("#flash_message").fadeOut();

        // Make API call
        const ajax = $.ajax({
            type: "POST",
            url: "/wishlists",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            // Enhanced success message with more details
            flash_message(`Success: Wishlist '${res.name}' created successfully with ID ${res.id}!`, 'success');

            // Clear the form after successful creation
            clear_form('create');

            // Auto-refresh the view tab if it contains results
            if ($("#results-body tr").length > 1) { // More than just the "no results" row
                setTimeout(() => {
                    $("#list-all-btn").trigger('click');
                }, 500); // Small delay to let user see the success message
            }

            // Re-enable the button
            createBtn.prop('disabled', false).html(originalText);
        });

        ajax.fail(function (res) {
            let errorMessage = "Error creating wishlist";

            // Enhanced error handling
            if (res.responseJSON && res.responseJSON.message) {
                errorMessage = res.responseJSON.message;
            } else if (res.status === 400) {
                errorMessage = "Invalid input data. Please check your entries and try again.";
            } else if (res.status === 409) {
                errorMessage = "A wishlist with this name already exists for this customer.";
            } else if (res.status === 500) {
                errorMessage = "Server error occurred. Please try again later.";
            } else if (res.status === 0) {
                errorMessage = "Network error. Please check your connection and try again.";
            }

            flash_message(errorMessage, 'error');

            // Re-enable the button
            createBtn.prop('disabled', false).html(originalText);
        });
    }

    $("#create-clear-btn").click(function () {
        clear_form('create');
        $("#flash_message").fadeOut();
        flash_message("Form cleared successfully. Ready to create a new wishlist.", 'info');
    });

    // ****************************************
    //  V I E W   F U N C T I O N A L I T Y
    // ****************************************

    $("#retrieve-btn").click(function () {
        const wishlist_id = $("#view_wishlist_id").val().trim();

        if (!wishlist_id) {
            flash_message("Please enter a Wishlist ID", 'error');
            return;
        }

        $("#flash_message").fadeOut();

        const ajax = $.ajax({
            type: "GET",
            url: `/wishlists/${wishlist_id}`,
            contentType: "application/json"
        });

        ajax.done(function (res) {
            // Clear previous results and show single result
            update_results_table([res]);
            flash_message("Success: Wishlist retrieved successfully!", 'success');
        });

        ajax.fail(function (res) {
            clear_results_table();
            let errorMessage = `Wishlist with id '${wishlist_id}' could not be found.`;
            if (res.responseJSON && res.responseJSON.message) {
                errorMessage = res.responseJSON.message;
            }
            flash_message(errorMessage, 'error');
        });
    });

    $("#search-btn").click(function () {
        const customer_id = $("#search_customer_id").val().trim();
        const name = $("#search_name").val().trim();
        const is_public = $("#search_is_public").val();

        let queryParams = [];
        if (customer_id) queryParams.push(`customer_id=${encodeURIComponent(customer_id)}`);
        if (name) queryParams.push(`name=${encodeURIComponent(name)}`);
        if (is_public) queryParams.push(`is_public=${is_public}`);

        const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';

        // Clear any previous results immediately
        clear_results_table();
        $("#flash_message").fadeOut();

        const ajax = $.ajax({
            type: "GET",
            url: `/wishlists${queryString}`,
            contentType: "application/json"
        });

        ajax.done(function (res) {
            clear_results_table();
            update_results_table(res);
            flash_message(`Success: Found ${res.length} wishlist(s)`, 'success');
        });

        ajax.fail(function (res) {
            clear_results_table();
            let errorMessage = "Error performing search";
            if (res.responseJSON && res.responseJSON.message) {
                errorMessage = res.responseJSON.message;
            }
            flash_message(errorMessage, 'error');
        });
    });

    $("#list-all-btn").click(function () {
        $("#flash_message").fadeOut();

        const ajax = $.ajax({
            type: "GET",
            url: "/wishlists",
            contentType: "application/json"
        });

        ajax.done(function (res) {
            update_results_table(res);
            flash_message(`Success: Listed ${res.length} wishlist(s)`, 'success');
        });

        ajax.fail(function (res) {
            clear_results_table();
            let errorMessage = "Error listing wishlists";
            if (res.responseJSON && res.responseJSON.message) {
                errorMessage = res.responseJSON.message;
            }
            flash_message(errorMessage, 'error');
        });
    });

    $("#view-clear-btn").click(function () {
        clear_form('view');
        clear_results_table();
        $("#flash_message").fadeOut();
    });

    // ****************************************
    //  R E S U L T S   T A B L E   F U N C T I O N S
    // ****************************************

    function update_results_table(wishlists) {
        const tbody = $("#results-body");
        tbody.empty();

        if (wishlists.length === 0) {
            tbody.append(`
                <tr>
                    <td colspan="7" class="text-center text-muted">No wishlists found</td>
                </tr>
            `);
            return;
        }

        wishlists.forEach(wishlist => {
            const row = `
                <tr>
                    <td>${wishlist.id}</td>
                    <td>${wishlist.name}</td>
                    <td>${wishlist.customer_id}</td>
                    <td>${wishlist.description || ''}</td>
                    <td>
                        <span class="label label-${wishlist.is_public ? 'success' : 'default'}">
                            ${wishlist.is_public ? 'Public' : 'Private'}
                        </span>
                    </td>
                    <td>${format_date(wishlist.created_at)}</td>
                    <td>
                        <button class="btn btn-xs btn-info" onclick="view_wishlist(${wishlist.id})">
                            <i class="glyphicon glyphicon-eye-open"></i> View
                        </button>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });
    }

    function clear_results_table() {
        const tbody = $("#results-body");
        tbody.empty();
        tbody.append(`
            <tr>
                <td colspan="7" class="text-center text-muted">No results to display</td>
            </tr>
        `);
    }

    // ****************************************
    //  G L O B A L   F U N C T I O N S
    // ****************************************

    // Make this function globally accessible for onclick handlers
    window.view_wishlist = function (wishlist_id) {
        $("#view_wishlist_id").val(wishlist_id);
        $("#retrieve-btn").click();
    };

    // ****************************************
    //  I N I T I A L I Z A T I O N
    // ****************************************

    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // Handle tab switching
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        // Clear flash messages when switching tabs
        $("#flash_message").fadeOut();
    });

    // Add responsive behavior for mobile
    $(window).resize(function () {
        // Adjust table container height on mobile
        if ($(window).width() < 768) {
            $('.table-responsive').css('max-height', '300px');
        } else {
            $('.table-responsive').css('max-height', '500px');
        }
    });

    // Initial call to set responsive behavior
    $(window).resize();

    // Show welcome message
    flash_message("Welcome to the Wishlist Admin Interface! Select a tab to get started.", 'info');

    // ****************************************
    //  U P D A T E   F U N C T I O N A L I T Y
    // ****************************************

    $("#load-btn").click(function () {
        const customer_id = $("#update_search_customer_id").val().trim();
        const name = $("#update_search_name").val().trim();

        if (!customer_id && !name) {
            flash_message("Please enter either Customer ID or Wishlist Name to search", 'error');
            return;
        }

        $("#flash_message").fadeOut();

        // Build search query
        let queryParams = [];
        if (customer_id) queryParams.push(`customer_id=${encodeURIComponent(customer_id)}`);
        if (name) queryParams.push(`name=${encodeURIComponent(name)}`);
        const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';

        const ajax = $.ajax({
            type: "GET",
            url: `/wishlists${queryString}`,
            contentType: "application/json"
        });

        ajax.done(function (res) {
            if (res.length === 0) {
                flash_message("No wishlists found matching the search criteria", 'error');
                return;
            }

            // If multiple results, use the first one (or could show selection UI)
            const wishlist = res[0];

            // Populate the update form
            $("#update_id").val(wishlist.id);
            $("#update_name").val(wishlist.name);
            $("#update_customer_id").val(wishlist.customer_id);
            $("#update_description").val(wishlist.description || '');
            $("#update_is_public").val(wishlist.is_public.toString());

            // Show the update form
            $("#update-form-section").fadeIn();

            flash_message(`Loaded wishlist: ${wishlist.name}`, 'success');
        });

        ajax.fail(function (res) {
            let errorMessage = "Error loading wishlist";
            if (res.responseJSON && res.responseJSON.message) {
                errorMessage = res.responseJSON.message;
            }
            flash_message(errorMessage, 'error');
        });
    });

    $("#save-changes-btn").click(function () {
        const wishlist_id = $("#update_id").val();

        if (!wishlist_id) {
            flash_message("No wishlist loaded for updating", 'error');
            return;
        }

        // Validate required fields
        const requiredFields = [
            { id: 'update_name', name: 'Wishlist Name' }
        ];

        if (!validate_required_fields(requiredFields)) {
            return;
        }

        const name = $("#update_name").val().trim();

        // Validate wishlist name format
        if (!validate_update_wishlist_name(name)) {
            return;
        }

        // Prepare update data
        const data = {
            name: name,
            customer_id: $("#update_customer_id").val().trim(),
            description: $("#update_description").val().trim(),
            is_public: $("#update_is_public").val() === "true"
        };

        $("#flash_message").fadeOut();

        const ajax = $.ajax({
            type: "PUT",
            url: `/wishlists/${wishlist_id}`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            flash_message(`Success: Wishlist '${res.name}' updated successfully!`, 'success');
        });

        ajax.fail(function (res) {
            let errorMessage = "Error updating wishlist";

            if (res.responseJSON && res.responseJSON.message) {
                errorMessage = res.responseJSON.message;
            } else if (res.status === 400) {
                errorMessage = "Invalid input data. Please check your entries and try again.";
            } else if (res.status === 404) {
                errorMessage = "Wishlist not found. It may have been deleted by another user.";
            } else if (res.status === 409) {
                errorMessage = "A wishlist with this name already exists for this customer.";
            } else if (res.status === 500) {
                errorMessage = "Server error occurred. Please try again later.";
            }

            flash_message(errorMessage, 'error');
        });
    });

    $("#cancel-update-btn").click(function () {
        // Hide the update form and clear fields
        $("#update-form-section").fadeOut();
        clear_update_form();
        flash_message("Update cancelled", 'info');
    });

    $("#update-clear-search-btn").click(function () {
        $("#update_search_customer_id").val('');
        $("#update_search_name").val('');
        $("#update-form-section").fadeOut();
        clear_update_form();
        $("#flash_message").fadeOut();
    });

    // ****************************************
    //  U P D A T E   H E L P E R   F U N C T I O N S
    // ****************************************

    function clear_update_form() {
        $("#update_id").val('');
        $("#update_name").val('');
        $("#update_customer_id").val('');
        $("#update_description").val('');
        $("#update_is_public").prop('selectedIndex', 0);
        // Remove any error styling
        $("#update-form .has-error").removeClass('has-error');
    }

    function validate_update_wishlist_name(name) {
        // Clear any existing error styling
        $("#update_name").removeClass('has-error');

        // Basic validation: minimum length
        if (name.length < 2) {
            flash_message("Wishlist name must be at least 2 characters long.", 'error');
            $("#update_name").addClass('has-error');
            return false;
        }

        // Maximum length validation
        if (name.length > 100) {
            flash_message("Wishlist name must be less than 100 characters.", 'error');
            $("#update_name").addClass('has-error');
            return false;
        }

        // Check for invalid characters
        const invalidChars = /[<>\"'&]/;
        if (invalidChars.test(name)) {
            flash_message("Wishlist name contains invalid characters. Please avoid: < > \" ' &", 'error');
            $("#update_name").addClass('has-error');
            return false;
        }

        return true;
    }

    // ****************************************
    //  R E A L - T I M E   V A L I D A T I O N
    // ****************************************

    // Real-time validation for wishlist name
    $("#create_name").on('input blur', function () {
        const name = $(this).val().trim();
        if (name.length > 0) {
            validate_wishlist_name(name);
        } else {
            $(this).removeClass('has-error');
        }
    });

    // Real-time validation for update wishlist name
    $("#update_name").on('input blur', function () {
        const name = $(this).val().trim();
        if (name.length > 0) {
            validate_update_wishlist_name(name);
        } else {
            $(this).removeClass('has-error');
        }
    });

    // Real-time validation for customer ID
    $("#create_customer_id").on('blur', function () {
        const customerId = $(this).val().trim();
        if (customerId.length > 0) {
            $(this).removeClass('has-error');
        }
    });

    // Clear error states when user starts typing
    $("#create_name, #create_customer_id, #update_name").on('input', function () {
        $(this).removeClass('has-error');
    });

});