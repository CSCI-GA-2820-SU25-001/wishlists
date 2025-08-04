# Wishlist Service

FIRE!

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![Build Status](https://github.com/CSCI-GA-2820-SU25-001/wishlists/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SU25-001/wishlists/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SU25-001/wishlists/branch/master/graph/badge.svg)](https://codecov.io/gh/CSCI-GA-2820-SU25-001/wishlists)
## Overview

A RESTful microservice for managing customer wishlists allows customers to create, manage, and organize their wishlists with items. This service provides a complete REST API for features such as creating wishlists, adding or removing items, and listing wishlist contents.

### Prerequisites
- Docker Desktop
- VS Code with Dev Containers and Remote extension
- Git

## Features

- Create customer wishlists
- Add items to wishlists
- Remove items from wishlists
- Update wishlist properties by name
- Update wishlist properties by item
- Delete the whole wishlists
- List certain items in wishlists
- List the whole wishlists

## API Endpoints

### Wishlists

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/wishlists` | Create a new wishlist |
| GET    | `/wishlists` | List all wishlists |
| GET    | `/wishlists?customer_id={id}` | List wishlists by customer ID |
| GET    | `/wishlists?name={name}` | List wishlists by name |
| GET    | `/wishlists/{id}` | Get a specific wishlist |
| PUT    | `/wishlists/{id}` | Update a wishlist |
| DELETE | `/wishlists/{id}` | Delete a wishlist |
| POST   | `/wishlists/{id}/clear` | Clear all items from a wishlist (Action) |

### Wishlist Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/wishlists/{id}/items` | Add an item |
| GET    | `/wishlists/{id}/items` | List all items |
| GET    | `/wishlists/{id}/items?{filters}` | List items with filtering |
| GET    | `/wishlists/{id}/items/{item_id}` | Get a specific item |
| PUT    | `/wishlists/{id}/items/{item_id}` | Update an item |
| DELETE | `/wishlists/{id}/items/{item_id}` | Remove an item |

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```
### Query Examples

The API supports filtering wishlists and items using query parameters:
#### Wishlist Filtering
1. **Filter Wishlists by Customer ID**
   ```bash
   GET /wishlists?customer_id=customer123
   ```

2. **Filter Wishlists by Name**
   ```bash
   GET /wishlists?name=Holiday%20Wishlist
   ```

#### Wishlist Item Filtering
3. **Search Items by Product Name**
   ```bash
   GET /wishlists/{id}/items?product_name=iPhone
   ```

4. **Filter Items by Category**
   ```bash
   GET /wishlists/{id}/items?category=Electronics
   ```

5. **Filter Items by Price Range**
   ```bash
   GET /wishlists/{id}/items?min_price=100&max_price=500
   ```

6. **Combine Multiple Filters**
   ```bash
   # Electronics items between $100-$500
   GET /wishlists/{id}/items?category=electronics&min_price=100&max_price=500

   # Food items under $25
   GET /wishlists/{id}/items?category=food&max_price=25

   # Specific iPhone in electronics category
   GET /wishlists/{id}/items?product_name=iPhone&category=electronics

   # All filters combined
   GET /wishlists/{id}/items?product_name=iPhone&category=electronics&min_price=100&max_price=1500
   ```

### Actions Section

The API supports the following actions beyond standard CRUD operations:

1. **Clear Wishlist**
   ```bash
   POST /wishlists/{id}/clear
   ```

### How to run

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd wishlist-service
   ```

2. **Open in VS Code and reopen in container:**
   ```bash
   code .
   ```

3. **Install dependencies:**
   ```bash
   make install
   ```

4. **Initialize the database:**
   ```bash
   flask db-create
   ```

5. **Run the service:**
   ```bash
   make run
   ```

   The service will run locally at `http://localhost:8080`

## Running Tests

1. **Run All Tests**
```bash
make test
```

2. **Test with Coverage**
```bash
pytest --cov=service --cov-fail-under=95
```

3. **Test models**
```bash
pytest tests/test_models.py
```

4. **Test routes**
```bash
pytest tests/test_routes.py
```

5. **Run linting**
```bash
make lint
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
