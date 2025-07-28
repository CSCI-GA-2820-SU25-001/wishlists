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
Error handlers

Flask-RESTX handles most HTTP errors automatically and returns JSON responses.
This file only contains custom business logic error handlers.
"""

from flask import current_app as app  # Import Flask application
from service.wishlist import DataValidationError
from . import status

# NOTE: We can't import api here due to circular imports, so we register
# these in routes.py instead. This file is kept minimal since Flask-RESTX
# automatically handles most HTTP errors (400, 404, 405, 415, 500, etc.)
# and returns proper JSON responses.

######################################################################
# Custom Business Logic Error Handlers
######################################################################
# These are registered in routes.py with @api.errorhandler()


def handle_data_validation_error(error):
    """Handles Value Errors from bad data"""
    message = str(error)
    app.logger.error(message)
    return {
        "status_code": status.HTTP_400_BAD_REQUEST,
        "error": "Bad Request",
        "message": message,
    }, status.HTTP_400_BAD_REQUEST
