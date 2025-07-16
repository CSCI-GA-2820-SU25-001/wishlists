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
        $(`#${tabId} select`).prop('selectedIndex', 0);
    }

    // Validate required fields
    function validate_required_fields(fields) {
        let isValid = true;
        let missingFields = [];

        fields.forEach(field => {
            const value = $(`#${field.id}`).val().trim();
            if (!value) {
                isValid = false;
                missingFields.push(field.name);
                $(`#${field.id}`).addClass('has-error');
            } else {
                $(`#${field.id}`).removeClass('has-error');
            }
        });

        if (!isValid) {
            flash_message(`Please fill in the following required fields: ${missingFields.join(', ')}`, 'error');
        }

        return isValid;
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
        // Validate required fields
        const requiredFields = [
            { id: 'create_name', name: 'Wishlist Name' },
            { id: 'create_customer_id', name: 'Customer ID' }
        ];

        if (!validate_required_fields(requiredFields)) {
            return;
        }

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

        ajax.done(function(res) {
            flash_message("Success: Wishlist created successfully!", 'success');
            // Optionally populate form with created wishlist data
            // This would be useful for showing the assigned ID
        });

        ajax.fail(function(res) {
            let errorMessage = "Error creating wishlist";
            if (res.responseJSON && res.responseJSON.message) {
                errorMessage = res.responseJSON.message;
            }
            flash_message(errorMessage, 'error');
        });
    });

    $("#create-clear-btn").click(function () {
        clear_form('create');
        $("#flash_message").fadeOut();
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

        ajax.done(function(res) {
            // Clear previous results and show single result
            update_results_table([res]);
            flash_message("Success: Wishlist retrieved successfully!", 'success');
        });

        ajax.fail(function(res) {
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

        $("#flash_message").fadeOut();

        const ajax = $.ajax({
            type: "GET",
            url: `/wishlists${queryString}`,
            contentType: "application/json"
        });

        ajax.done(function(res) {
            update_results_table(res);
            flash_message(`Success: Found ${res.length} wishlist(s)`, 'success');
        });

        ajax.fail(function(res) {
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

        ajax.done(function(res) {
            update_results_table(res);
            flash_message(`Success: Listed ${res.length} wishlist(s)`, 'success');
        });

        ajax.fail(function(res) {
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
    window.view_wishlist = function(wishlist_id) {
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
    $(window).resize(function() {
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
});