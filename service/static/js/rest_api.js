$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Enhanced toast notification system (no layout shift)
    function flash_message(message, type = 'info') {
        const flashDiv = $("#flash_message");
        const flashText = $("#flash_text");

        // Remove any existing classes and animations
        flashDiv.removeClass('flash-success flash-error flash-info flash-warning show hide');

        // Add appropriate class and show message with close button
        flashDiv.addClass(`flash-${type}`);
        flashText.html(`
            ${message}
            <button class="close-btn" onclick="hideFlashMessage()" title="Close">&times;</button>
        `);

        // Show with slide-in animation
        flashDiv.show().addClass('show');

        // Auto-hide with different timings based on type
        const hideDelay = type === 'error' ? 8000 : type === 'warning' ? 6000 : 4000;
        setTimeout(() => {
            hideFlashMessage();
        }, hideDelay);
    }

    // Function to manually hide flash message
    window.hideFlashMessage = function() {
        const flashDiv = $("#flash_message");
        flashDiv.addClass('hide');
        setTimeout(() => {
            flashDiv.hide().removeClass('show hide');
        }, 300); // Wait for animation to complete
    };

    // Enhanced loading state management
    const LoadingManager = {
        // Show loading state on button with enhanced options
        showButtonLoading: function(buttonSelector, options = {}) {
            const $button = $(buttonSelector);
            const originalText = options.originalText || $button.html();
            const loadingText = options.loadingText || 'Loading...';
            const spinnerClass = options.spinnerClass || 'loading-spinner';

            $button.prop('disabled', true);
            $button.addClass('btn-loading');
            $button.html(`<span class="${spinnerClass}"></span><span class="btn-text">${loadingText}</span>`);

            // Store original text for restoration
            $button.data('original-text', originalText);
            return originalText;
        },

        // Hide loading state on button
        hideButtonLoading: function(buttonSelector, originalText = null) {
            const $button = $(buttonSelector);
            const textToRestore = originalText || $button.data('original-text') || 'Button';

            $button.prop('disabled', false);
            $button.removeClass('btn-loading');
            $button.html(textToRestore);
            $button.removeData('original-text');
        },

        // Show loading overlay on panel with enhanced options
        showPanelLoading: function(panelSelector, options = {}) {
            const $panel = $(panelSelector);
            if ($panel.find('.loading-overlay').length === 0) {
                const loadingText = options.loadingText || '';
                const spinnerSize = options.spinnerSize || 'loading-spinner-lg';
                const overlayClass = options.dark ? 'loading-overlay loading-overlay-dark' : 'loading-overlay';

                $panel.css('position', 'relative');
                $panel.append(`
                    <div class="${overlayClass}">
                        <div class="loading-spinner ${spinnerSize}"></div>
                        ${loadingText ? `<div class="loading-text">${loadingText}</div>` : ''}
                    </div>
                `);
            }
        },

        // Hide loading overlay on panel
        hidePanelLoading: function(panelSelector) {
            $(panelSelector).find('.loading-overlay').remove();
        },

        // Show table loading state with skeleton rows
        showTableLoading: function(tableSelector, rowCount = 3) {
            const $table = $(tableSelector);
            const $tbody = $table.find('tbody');
            const columnCount = $table.find('thead th').length || 5;

            $tbody.empty();
            $table.addClass('table-loading');

            for (let i = 0; i < rowCount; i++) {
                let skeletonRow = '<tr class="table-skeleton-row">';
                for (let j = 0; j < columnCount; j++) {
                    skeletonRow += '<td class="table-skeleton-cell"><div class="skeleton skeleton-text"></div></td>';
                }
                skeletonRow += '</tr>';
                $tbody.append(skeletonRow);
            }
        },

        // Hide table loading state
        hideTableLoading: function(tableSelector) {
            const $table = $(tableSelector);
            $table.removeClass('table-loading');
            $table.find('.table-skeleton-row').remove();
        },

        // Show form loading state
        showFormLoading: function(formSelector) {
            const $form = $(formSelector);
            $form.addClass('form-loading');
            $form.find('.btn').prop('disabled', true);
        },

        // Hide form loading state
        hideFormLoading: function(formSelector) {
            const $form = $(formSelector);
            $form.removeClass('form-loading');
            $form.find('.btn').prop('disabled', false);
        },

        // Show progress bar
        showProgress: function(containerSelector, progress = 0, options = {}) {
            const $container = $(containerSelector);
            const animated = options.animated ? 'progress-bar-animated' : '';
            const colorClass = options.color ? `progress-bar-${options.color}` : '';

            if ($container.find('.progress-container').length === 0) {
                $container.append(`
                    <div class="progress-container">
                        <div class="progress-bar ${animated} ${colorClass}" style="width: ${progress}%"></div>
                    </div>
                `);
            } else {
                $container.find('.progress-bar').css('width', `${progress}%`);
            }
        },

        // Update progress
        updateProgress: function(containerSelector, progress) {
            const $container = $(containerSelector);
            $container.find('.progress-bar').css('width', `${progress}%`);
        },

        // Hide progress bar
        hideProgress: function(containerSelector) {
            $(containerSelector).find('.progress-container').remove();
        }
    };

    // Legacy function wrappers for backward compatibility
    function showButtonLoading(buttonSelector, originalText) {
        return LoadingManager.showButtonLoading(buttonSelector, { originalText });
    }

    function hideButtonLoading(buttonSelector, originalText) {
        LoadingManager.hideButtonLoading(buttonSelector, originalText);
    }

    function showPanelLoading(panelSelector) {
        LoadingManager.showPanelLoading(panelSelector);
    }

    function hidePanelLoading(panelSelector) {
        LoadingManager.hidePanelLoading(panelSelector);
    }

    // Enhanced AJAX wrapper with loading states
    function makeAjaxRequest(options) {
        const {
            url,
            method = 'GET',
            data = null,
            buttonSelector = null,
            panelSelector = null,
            successCallback = null,
            errorCallback = null,
            originalButtonText = null
        } = options;

        // Show loading states
        let buttonText = '';
        if (buttonSelector) {
            buttonText = showButtonLoading(buttonSelector, originalButtonText);
        }
        if (panelSelector) {
            showPanelLoading(panelSelector);
        }

        const ajaxOptions = {
            type: method,
            url: url,
            contentType: "application/json"
        };

        if (data) {
            ajaxOptions.data = JSON.stringify(data);
        }

        return $.ajax(ajaxOptions)
            .done(function(response) {
                if (successCallback) {
                    successCallback(response);
                }
            })
            .fail(function(xhr) {
                let errorMessage = 'An unexpected error occurred';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMessage = xhr.responseJSON.message;
                } else if (xhr.responseText) {
                    try {
                        const errorData = JSON.parse(xhr.responseText);
                        errorMessage = errorData.message || errorMessage;
                    } catch (e) {
                        errorMessage = xhr.responseText;
                    }
                }

                if (errorCallback) {
                    errorCallback(errorMessage, xhr);
                } else {
                    flash_message(`<i class="fa fa-exclamation-circle"></i> ${errorMessage}`, 'error');
                }
            })
            .always(function() {
                // Hide loading states
                if (buttonSelector) {
                    hideButtonLoading(buttonSelector, buttonText);
                }
                if (panelSelector) {
                    hidePanelLoading(panelSelector);
                }
            });
    }

    // Clear all form fields in a specific form
    function clear_form(formId) {
        if (formId === 'create') {
            // Clear create form specifically
            $('#create_name').val('');
            $('#create_customer_id').val('');
            $('#create_description').val('');
            $('#create_is_public').val('false');
        } else {
            // Generic clear for other forms
            $(`#${formId} input[type="text"]`).val('');
            $(`#${formId} textarea`).val('');
            $(`#${formId} input[type="checkbox"]`).prop('checked', false);
            $(`#${formId} select`).prop('selectedIndex', 0);
        }
        // Remove any error styling
        $('.has-error').removeClass('has-error');
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

        // Show progress indicator
        LoadingManager.showProgress('#create-progress', 0, { animated: true });
        $('#create-progress').show();

        // Simulate progress steps
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 20;
            LoadingManager.updateProgress('#create-progress', Math.min(progress, 90));
        }, 200);

        // Use enhanced AJAX wrapper with loading states
        makeAjaxRequest({
            url: "/wishlists",
            method: "POST",
            data: data,
            buttonSelector: createBtn,
            panelSelector: "#create-form",
            originalButtonText: originalText,
            successCallback: function(res) {
                // Complete progress
                clearInterval(progressInterval);
                LoadingManager.updateProgress('#create-progress', 100);

                setTimeout(() => {
                    $('#create-progress').fadeOut();
                    LoadingManager.hideProgress('#create-progress');
                }, 1000);

                // Enhanced success message with more details and icon
                flash_message(`<i class="fa fa-check-circle"></i> Success: Wishlist '${res.name}' created successfully with ID ${res.id}!`, 'success');

                // Clear the form after successful creation
                clear_form('create');

                // Auto-refresh the view tab if it contains results
                if ($("#results-body tr").length > 1) { // More than just the "no results" row
                    setTimeout(() => {
                        $("#list-all-btn").trigger('click');
                    }, 500); // Small delay to let user see the success message
                }
            },
            errorCallback: function(errorMessage, xhr) {
                // Clear progress on error
                clearInterval(progressInterval);
                LoadingManager.updateProgress('#create-progress', 100);
                LoadingManager.showProgress('#create-progress', 100, { color: 'error' });

                setTimeout(() => {
                    $('#create-progress').fadeOut();
                    LoadingManager.hideProgress('#create-progress');
                }, 2000);

                // Enhanced error handling with specific status codes
                if (xhr.status === 400) {
                    errorMessage = "Invalid input data. Please check your entries and try again.";
                } else if (xhr.status === 409) {
                    errorMessage = "A wishlist with this name already exists for this customer.";
                } else if (xhr.status === 500) {
                    errorMessage = "Server error occurred. Please try again later.";
                } else if (xhr.status === 0) {
                    errorMessage = "Network error. Please check your connection and try again.";
                }

                flash_message(`<i class="fa fa-exclamation-circle"></i> ${errorMessage}`, 'error');
            }
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
        const wishlist_id = $("#search_wishlist_id").val().trim();

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

    // Modal save changes functionality
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

        // Use enhanced AJAX wrapper
        makeAjaxRequest({
            url: `/wishlists/${wishlist_id}`,
            method: "PUT",
            data: data,
            buttonSelector: "#save-changes-btn",
            originalButtonText: "Save Changes",
            successCallback: function(res) {
                flash_message(`<i class="fa fa-check-circle"></i> Success: Wishlist '${res.name}' updated successfully!`, 'success');

                // Enhanced modal cleanup
                $("#updateModal").modal('hide');
                setTimeout(function() {
                    forceModalCleanup();
                }, 300);

                // Refresh the results
                setTimeout(() => {
                    $("#list-all-btn").click();
                }, 500);
            },
            errorCallback: function(errorMessage, xhr) {
                if (xhr.status === 400) {
                    errorMessage = "Invalid input data. Please check your entries and try again.";
                } else if (xhr.status === 404) {
                    errorMessage = "Wishlist not found. It may have been deleted by another user.";
                } else if (xhr.status === 409) {
                    errorMessage = "A wishlist with this name already exists for this customer.";
                } else if (xhr.status === 500) {
                    errorMessage = "Server error occurred. Please try again later.";
                }
                flash_message(`<i class="fa fa-exclamation-circle"></i> ${errorMessage}`, 'error');
            }
        });
    });

    $("#search-btn").click(function () {
        const customer_id = $("#search_customer_id").val().trim();
        const name = $("#search_name").val().trim();
        const is_public = $("#search_is_public").val();
        let hasError = false;
        if (customer_id && isNaN(customer_id)) {
            $("#search_customer_id").addClass("has-error");
            hasError = true;
        } else {
        $("#search_customer_id").removeClass("has-error");
        } if (name && !/^[a-zA-Z0-9 ]+$/.test(name)) {
            $("#search_name").addClass("has-error");
            hasError = true;
        } else {
             $("#search_name").removeClass("has-error");
        } if (hasError) {
            flash_message("Please fix the highlighted search fields", "error");
            return;
        }
        
        let queryParams = [];
        if (customer_id) queryParams.push(`customer_id=${encodeURIComponent(customer_id)}`);
        if (name) queryParams.push(`name=${encodeURIComponent(name)}`);
        if (is_public) queryParams.push(`is_public=${is_public}`);

        const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';

        // Clear any previous results immediately
        clear_results_table();
        $("#flash_message").fadeOut();

        // Enhanced loading states for search
        const $searchBtn = $(this);
        const originalText = $searchBtn.html();

        LoadingManager.showButtonLoading($searchBtn, {
            loadingText: 'Searching...',
            spinnerClass: 'loading-spinner loading-spinner-white'
        });

        LoadingManager.showTableLoading('#results-table', 3);
        LoadingManager.showPanelLoading('#results-panel', {
            loadingText: 'Searching wishlists...'
        });

        const ajax = $.ajax({
            type: "GET",
            url: `/wishlists${queryString}`,
            contentType: "application/json"
        });

        ajax.done(function (res) {
            clear_results_table();
            update_results_table(res);
            flash_message(`<i class="fa fa-check-circle"></i> Success: Found ${res.length} wishlist(s)`, 'success');
        });

        ajax.fail(function (res) {
            clear_results_table();
            let errorMessage = "Error performing search";
            if (res.responseJSON && res.responseJSON.message) {
                errorMessage = res.responseJSON.message;
            }
            flash_message(`<i class="fa fa-exclamation-circle"></i> ${errorMessage}`, 'error');
        });

        ajax.always(function() {
            LoadingManager.hideButtonLoading($searchBtn, originalText);
            LoadingManager.hideTableLoading('#results-table');
            LoadingManager.hidePanelLoading('#results-panel');
        });
    });

    $("#list-all-btn").click(function () {
        $("#flash_message").fadeOut();

        // Enhanced loading states for list all
        const $listBtn = $(this);
        const originalText = $listBtn.html();

        LoadingManager.showButtonLoading($listBtn, {
            loadingText: 'Loading...',
            spinnerClass: 'loading-spinner loading-spinner-white'
        });

        LoadingManager.showTableLoading('#results-table', 5);
        LoadingManager.showPanelLoading('#results-panel', {
            loadingText: 'Loading all wishlists...'
        });

        const ajax = $.ajax({
            type: "GET",
            url: "/wishlists",
            contentType: "application/json"
        });

        ajax.done(function (res) {
            update_results_table(res);
            flash_message(`<i class="fa fa-check-circle"></i> Success: Listed ${res.length} wishlist(s)`, 'success');
        });

        ajax.fail(function (res) {
            clear_results_table();
            let errorMessage = "Error listing wishlists";
            if (res.responseJSON && res.responseJSON.message) {
                errorMessage = res.responseJSON.message;
            }
            flash_message(`<i class="fa fa-exclamation-circle"></i> ${errorMessage}`, 'error');
        });

        ajax.always(function() {
            LoadingManager.hideButtonLoading($listBtn, originalText);
            LoadingManager.hideTableLoading('#results-table');
            LoadingManager.hidePanelLoading('#results-panel');
        });
    });

    $("#view-clear-btn").click(function () {
        // Clear search fields
        $("#search_wishlist_id").val('');
        $("#search_customer_id").val('');
        $("#search_name").val('');
        $("#search_is_public").val('');

        clear_results_table();
        $("#flash_message").fadeOut();
    });




    // ****************************************
    //  A C T I O N S   F U N C T I O N A L I T Y
    // ****************************************

    // Make Public
    $("#make-public-btn").click(function () {
        const wishlistId = $("#action_wishlist_id").val().trim();
        if (!wishlistId) {
            flash_message("Please enter a Wishlist ID", "error");
            return;
        }
        $("#flash_message").fadeOut();

        const btn = $(this);
        const originalText = btn.html();

        LoadingManager.showButtonLoading(btn, {
            loadingText: 'Publishing...',
            spinnerClass: 'loading-spinner loading-spinner-white'
        });

        $.ajax({
            type: "POST",
            url: `/wishlists/${wishlistId}/publish`,  // :contentReference[oaicite:0]{index=0}
            contentType: "application/json"
        })
        .done(function (res) {
            flash_message(res.message, "success");
            $("#action-status-result").text(`Wishlist ${res.wishlist_id} is now Public.`);
        })
        .fail(function (res) {
            const err = res.responseJSON && res.responseJSON.message
                ? res.responseJSON.message
                : `Error publishing wishlist ${wishlistId}.`;
            flash_message(err, "error");
        })
        .always(function () {
            LoadingManager.hideButtonLoading(btn, originalText);
        });
    });

    // Make Private
    $("#make-private-btn").click(function () {
        const wishlistId = $("#action_wishlist_id").val().trim();
        if (!wishlistId) {
            flash_message("Please enter a Wishlist ID", "error");
            return;
        }
        $("#flash_message").fadeOut();

        const btn = $(this);
        const originalText = btn.html();

        LoadingManager.showButtonLoading(btn, {
            loadingText: 'Unpublishing...',
            spinnerClass: 'loading-spinner loading-spinner-white'
        });

        $.ajax({
            type: "POST",
            url: `/wishlists/${wishlistId}/unpublish`,  // :contentReference[oaicite:1]{index=1}
            contentType: "application/json"
        })
        .done(function (res) {
            flash_message(res.message, "success");
            $("#action-status-result").text(`Wishlist ${res.wishlist_id} is now Private.`);
        })
        .fail(function (res) {
            const err = res.responseJSON && res.responseJSON.message
                ? res.responseJSON.message
                : `Error unpublishing wishlist ${wishlistId}.`;
            flash_message(err, "error");
        })
        .always(function () {
            LoadingManager.hideButtonLoading(btn, originalText);
        });
    });

    // Query Status
    $("#query-status-btn").click(function () {
        const wishlistId = $("#action_wishlist_id").val().trim();
        if (!wishlistId) {
            flash_message("Please enter a Wishlist ID", "error");
            return;
        }
        $("#flash_message").fadeOut();

        const btn = $(this);
        const originalText = btn.html();

        LoadingManager.showButtonLoading(btn, {
            loadingText: 'Querying...',
            spinnerClass: 'loading-spinner loading-spinner-white'
        });

        $.ajax({
            type: "GET",
            url: `/wishlists/${wishlistId}`,  // :contentReference[oaicite:2]{index=2}
            contentType: "application/json"
        })
        .done(function (res) {
            const statusText = res.is_public ? "Public" : "Private";
            flash_message(`Wishlist ${res.id} is currently ${statusText}.`, "info");
            $("#action-status-result").text(`Status: ${statusText}`);
        })
        .fail(function (res) {
            const err = res.responseJSON && res.responseJSON.message
                ? res.responseJSON.message
                : `Error retrieving wishlist ${wishlistId}.`;
            flash_message(err, "error");
        })
        .always(function () {
            LoadingManager.hideButtonLoading(btn, originalText);
        });
    });




    // ****************************************
    //  R E S U L T S   T A B L E   F U N C T I O N S
    // ****************************************

    function update_results_table(wishlists) {
        const tbody = $("#results-body");
        const countBadge = $("#results-count");
        tbody.empty();

        if (wishlists.length === 0) {
            tbody.append(`
                <tr>
                    <td colspan="7" class="text-center text-muted">
                        <i class="fa fa-info-circle"></i> No wishlists found
                    </td>
                </tr>
            `);
            countBadge.text('0');
            return;
        }

        countBadge.text(wishlists.length);

        wishlists.forEach(wishlist => {
            const row = `
                <tr>
                    <td>${wishlist.id}</td>
                    <td><strong>${wishlist.name}</strong></td>
                    <td>${wishlist.customer_id}</td>
                    <td>${wishlist.description || '<em>No description</em>'}</td>
                    <td>
                        <span class="label label-${wishlist.is_public ? 'success' : 'default'}">
                            <i class="fa fa-${wishlist.is_public ? 'globe' : 'lock'}"></i>
                            ${wishlist.is_public ? 'Public' : 'Private'}
                        </span>
                    </td>
                    <td>${format_date(wishlist.created_at)}</td>
                    <td>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-info" onclick="view_wishlist_items(${wishlist.id})" title="View Items in this wishlist">
                                <i class="fa fa-shopping-cart"></i> Items
                            </button>
                            <button class="btn btn-sm btn-warning" onclick="edit_wishlist(${wishlist.id})" title="Edit this wishlist">
                                <i class="fa fa-edit"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="delete_wishlist(${wishlist.id}, '${wishlist.name}')" title="Delete this wishlist">
                                <i class="fa fa-trash"></i> Delete
                            </button>
                        </div>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });
    }

    function clear_results_table() {
        const tbody = $("#results-body");
        const countBadge = $("#results-count");
        tbody.empty();
        tbody.append(`
            <tr>
                <td colspan="7" class="text-center text-muted">
                    <i class="fa fa-info-circle"></i> No results to display
                </td>
            </tr>
        `);
        countBadge.text('0');
    }

    // ****************************************
    //  G L O B A L   F U N C T I O N S
    // ****************************************

    // Enhanced global functions for new UI
    window.view_wishlist = function (wishlist_id) {
        $("#search_wishlist_id").val(wishlist_id);
        $("#retrieve-btn").click();
    };

    // Switch to items tab and load wishlist items
    window.view_wishlist_items = function (wishlist_id) {
        // Switch to items tab
        $('#items-tab').tab('show');

        // Load the wishlist
        $("#item_wishlist_id").val(wishlist_id);
        $("#load-wishlist-btn").click();
    };

    // Edit wishlist using modal with enhanced loading
    window.edit_wishlist = function (wishlist_id) {
        // Clear any existing messages
        $("#flash_message").fadeOut();

        // Show loading state in modal
        $("#updateModal").modal({
            backdrop: true,
            keyboard: true,
            show: true
        });

        // Show loading overlay in modal
        LoadingManager.showPanelLoading('#updateModal .modal-content', {
            loadingText: 'Loading wishlist data...',
            spinnerSize: 'loading-spinner-lg'
        });

        // Use enhanced AJAX wrapper
        makeAjaxRequest({
            url: `/wishlists/${wishlist_id}`,
            method: "GET",
            successCallback: function(wishlist) {
                // Hide loading overlay
                LoadingManager.hidePanelLoading('#updateModal .modal-content');

                // Populate modal form
                $("#update_id").val(wishlist.id);
                $("#update_name").val(wishlist.name);
                $("#update_customer_id").val(wishlist.customer_id);
                $("#update_description").val(wishlist.description || '');
                $("#update_is_public").val(wishlist.is_public.toString());

                // Ensure modal is properly displayed
                setTimeout(() => {
                    $("#updateModal").addClass('show');
                    $('body').addClass('modal-open');
                }, 100);
            },
            errorCallback: function(errorMessage) {
                LoadingManager.hidePanelLoading('#updateModal .modal-content');
                $("#updateModal").modal('hide');
                flash_message(`<i class="fa fa-exclamation-circle"></i> Error loading wishlist: ${errorMessage}`, 'error');
            }
        });
    };

    // Delete wishlist with confirmation and loading states
    window.delete_wishlist = function (wishlist_id, wishlist_name) {
        if (!confirm(`Are you sure you want to delete the wishlist "${wishlist_name}"?\n\nThis will permanently remove the wishlist and all its items. This action cannot be undone.`)) {
            return;
        }

        // Show loading overlay on results panel during deletion
        LoadingManager.showPanelLoading('#results-panel', {
            loadingText: `Deleting "${wishlist_name}"...`,
            spinnerSize: 'loading-spinner-lg'
        });

        const ajax = $.ajax({
            type: "DELETE",
            url: `/wishlists/${wishlist_id}`,
            contentType: "application/json"
        });

        ajax.done(function (res) {
            flash_message(`<i class="fa fa-check-circle"></i> Success: Wishlist "${wishlist_name}" deleted successfully`, 'success');
            // Refresh the results
            $("#list-all-btn").click();
        });

        ajax.fail(function (res) {
            let errorMessage = "Error deleting wishlist";
            if (res.responseJSON && res.responseJSON.message) {
                errorMessage = res.responseJSON.message;
            }
            flash_message(`<i class="fa fa-exclamation-circle"></i> ${errorMessage}`, 'error');
        });

        ajax.always(function() {
            LoadingManager.hidePanelLoading('#results-panel');
        });
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

    // Enhanced modal event handlers to prevent backdrop issues
    $('#updateModal').on('show.bs.modal', function () {
        // Ensure modal is properly positioned and clickable
        $(this).css('z-index', 1050);
        $('.modal-backdrop').css('z-index', 1040);
    });

    $('#updateModal').on('hidden.bs.modal', function () {
        // Comprehensive cleanup when modal is closed
        $('body').removeClass('modal-open');
        $('.modal-backdrop').remove();

        // Force remove any lingering backdrop elements
        $('.modal-backdrop').each(function() {
            $(this).remove();
        });

        // Reset body overflow
        $('body').css('overflow', '');
        $('body').css('padding-right', '');

        // Ensure page is clickable
        $('body').off('click.bs.modal.data-api');
    });

    // Additional cleanup for save changes button
    $(document).on('click', '#save-changes-btn', function() {
        // After save operation, ensure modal cleanup
        setTimeout(function() {
            forceModalCleanup();
        }, 500);
    });

    // Additional cleanup for cancel/close buttons
    $(document).on('click', '[data-dismiss="modal"], .modal .close', function() {
        setTimeout(function() {
            forceModalCleanup();
        }, 300);
    });

    // Force modal cleanup function
    function forceModalCleanup() {
        $('body').removeClass('modal-open');
        $('.modal-backdrop').remove();
        $('body').css('overflow', '');
        $('body').css('padding-right', '');
        $('#updateModal').removeClass('show');
        $('#updateModal').css('display', 'none');
        $('body').off('click.bs.modal.data-api');

        // Additional cleanup for any lingering modal states
        $('.modal').removeClass('show');
        $('.modal').css('display', 'none');
        $('body').removeClass('modal-open');
    }

    // Global escape key handler for modal cleanup
    $(document).keydown(function(e) {
        if (e.keyCode === 27) { // ESC key
            if ($('#updateModal').hasClass('show') || $('.modal-backdrop').length > 0) {
                setTimeout(function() {
                    forceModalCleanup();
                }, 100);
            }
        }
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
    //  D E L E T E   F U N C T I O N A L I T Y
    // ****************************************
    let selectedWishlistForDelete = null;

    $("#delete-lookup-btn").click(function () {
        const customer_id = $("#delete_customer_id").val().trim();

        if (!customer_id) {
            flash_message("Please enter a Customer ID", 'error');
            return;
        }

        $("#flash_message").fadeOut();

        const ajax = $.ajax({
            type: "GET",
            url: `/wishlists?customer_id=${encodeURIComponent(customer_id)}`,
            contentType: "application/json"
        });

        ajax.done(function (res) {
            if (res.length === 0) {
                $("#delete-wishlist-selection").fadeOut();
                $("#delete-wishlist-details").fadeOut();
                flash_message(`No wishlists found for customer ID '${customer_id}'`, 'error');
                return;
            }

            // Show wishlist selection
            let wishlistsHtml = '<h5>Select a wishlist to delete:</h5>';
            wishlistsHtml += '<div class="list-group">';
            
            res.forEach(function(wishlist) {
                wishlistsHtml += `
                    <button type="button" class="list-group-item list-group-item-action" 
                            onclick="select_wishlist_for_delete(${wishlist.id}, '${wishlist.name}')">
                        <strong>${wishlist.name}</strong><br>
                        <small>ID: ${wishlist.id} | ${wishlist.is_public ? 'Public' : 'Private'} | ${wishlist.description || 'No description'}</small>
                    </button>
                `;
            });
            
            wishlistsHtml += '</div>';
            $("#delete-wishlists-list").html(wishlistsHtml);
            $("#delete-wishlist-selection").fadeIn();
            $("#delete-wishlist-details").fadeOut();
            
            flash_message("Success: Found wishlists for customer", 'success');
        });

        ajax.fail(function (res) {
            $("#delete-wishlist-selection").fadeOut();
            $("#delete-wishlist-details").fadeOut();
            flash_message(`Customer with ID '${customer_id}' could not be found`, 'error');
        });
    });

    // Make this function globally accessible
    window.select_wishlist_for_delete = function(wishlist_id, wishlist_name) {
        selectedWishlistForDelete = wishlist_id;
        
        const ajax = $.ajax({
            type: "GET",
            url: `/wishlists/${wishlist_id}`,
            contentType: "application/json"
        });

        ajax.done(function (res) {
            $("#delete-name").text(res.name);
            $("#delete-customer-id").text(res.customer_id);
            $("#delete-visibility").text(res.is_public ? 'Public' : 'Private');
            $("#delete-created").text(format_date(res.created_at));
            $("#delete-description").text(res.description || 'No description');
            
            load_wishlist_items_for_delete(wishlist_id);
            $("#delete-wishlist-details").fadeIn();
            flash_message("Success: Wishlist selected for deletion", 'success');
        });

        ajax.fail(function (res) {
            flash_message("Error loading wishlist details", 'error');
        });
    };

    function load_wishlist_items_for_delete(wishlist_id) {
        const ajax = $.ajax({
            type: "GET",
            url: `/wishlists/${wishlist_id}/items`,
            contentType: "application/json"
        });

        ajax.done(function (res) {
            $("#delete-items-count").text(res.length);
            
            if (res.length === 0) {
                $("#delete-items-container").html('<p class="text-muted">No items in this wishlist</p>');
            } else {
                let itemsHtml = '<table class="table table-striped table-condensed">';
                itemsHtml += '<thead><tr><th>Product Name</th><th>Category</th><th>Price</th><th>Quantity</th></tr></thead><tbody>';
                
                res.forEach(function(item) {
                    itemsHtml += `<tr>
                        <td>${item.product_name}</td>
                        <td>${item.category || 'N/A'}</td>
                        <td>$${item.price || '0.00'}</td>
                        <td>${item.quantity || 1}</td>
                    </tr>`;
                });
                
                itemsHtml += '</tbody></table>';
                $("#delete-items-container").html(itemsHtml);
            }
        });

        ajax.fail(function (res) {
            $("#delete-items-count").text('Error loading');
            $("#delete-items-container").html('<p class="text-danger">Error loading items</p>');
        });
    }

    $("#delete-confirm-btn").click(function () {
        if (!selectedWishlistForDelete) {
            flash_message("No wishlist selected for deletion", 'error');
            return;
        }
        
        const wishlist_name = $("#delete-name").text();
        
        if (!confirm(`Are you sure you want to delete the wishlist "${wishlist_name}"? This will permanently remove the wishlist and all its items. This action cannot be undone.`)) {
            return;
        }
        
        $("#flash_message").fadeOut();
        
        const ajax = $.ajax({
            type: "DELETE",
            url: `/wishlists/${selectedWishlistForDelete}`,
            contentType: "application/json"
        });

        ajax.done(function (res) {
            flash_message("Success: Wishlist deleted successfully", 'success');
            clear_delete_form();
        });

        ajax.fail(function (res) {
            let errorMessage = "Error deleting wishlist";
            if (res.responseJSON && res.responseJSON.message) {
                errorMessage = res.responseJSON.message;
            }
            flash_message(errorMessage, 'error');
        });
    });

    $("#delete-cancel-btn").click(function () {
        clear_delete_form();
    });

    function clear_delete_form() {
        $("#delete_customer_id").val('');
        $("#delete-wishlist-selection").fadeOut();
        $("#delete-wishlist-details").fadeOut();
        selectedWishlistForDelete = null;
        $("#flash_message").fadeOut();
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
