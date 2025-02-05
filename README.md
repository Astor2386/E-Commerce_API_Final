# E-Commerce  API
Project Summary
This project consists of building an API for an e-commerce platform, utilizing Flask for the web framework, SQLAlchemy for object-relational mapping, Marshmallow for data transformation, and MySQL for data persistence.
It encompasses full CRUD operations for Users, Orders, and Products, alongside JWT token authentication for endpoint security.

# Key Functionalities
- User Operations: Creation, retrieval, updating, and deletion of user profiles.
- Order Handling: Managing orders, including product associations.
- Product Operations: CRUD functionalities for products.
- JWT Auth: JSON Web Token authentication to secure user operations.
# Bonus Features:
- *Enhanced order control (cancellation and shipping).
- *Pagination in user and potentially product listings.
- *JWT for safeguarding user interactions.

# Getting Started
## Requirements
-Runs on Python 3
-MySQL server setup
-Visual Studio Code

## Setup Instructions
Note: This project requires setup as described below to run correctly.

1. # Clone the Project:
git clone -      https://github.com/Astor2386/E-Commerce_API_Final.git
cd E-Commerce_API
Virtual Environment Creation:
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
Install Required Packages:
# pip install the following in cmd prompt / bash-
pip install Flask
pip install Flask-SQLAlchemy
pip install Flask-Marshmallow
pip install marshmallow-sqlalchemy
pip install mysql-connector-python
pip install Flask-JWT-Extended
pip install bcrypt

# Database Setup:
Establish a database named ecommerce_api 
## in MySQL:
CREATE DATABASE ecommerce_api;
Modify SQLALCHEMY_DATABASE_URI in app.py with your MySQL credentials:
python-
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:<YOUR PASSWORD>@localhost/ecommerce_api'
Launch Application:
bash-
python app.py

# Project Architecture
app.py: Main application file including Flask setup, model definitions, schemas, and routing.

# Data Models:
Users: Handles user data with secure password management.
Orders: Manages order details, timestamps, and user connections.
Products: Oversees product data.
Order-Product Link: Facilitates a many-to-many relationship.

# Data Serialization:
Marshmallow schemas for converting between Python objects and JSON.

# API Endpoints:
Offers CRUD functionalities with JWT authentication protecting user-specific routes.

# JWT Security
Configuration Overview
JWT authentication is configured with a secret key for signing tokens. Instructions for setting this up are included in the code comments.
(Super important to go through this process slowly, you must get an JWT token to advance!)

# Usage Instructions
Login: Use the /login endpoint to obtain a JWT token.
Protected Routes: Include the token in the Authorization header of requests to protected routes.
(Click Authorization tab, select bearer token, insert token)

# Testing with Postman
Use Postman to test API endpoints:
Set up a POST request to /login to get an authentication token.
Use the token in the Authorization header for subsequent requests to test CRUD operations for Users, Orders, and Products.
Reminder: (Click Authorization tab, select bearer token, insert token)
Here's how to interact with the Product endpoints:
GET /products: To retrieve all products or paginated results.

GET /products/<id>: To fetch a specific product.
(If there are no products, feel free to skip ahead to POST /products)

POST /products: To add a new product. click body, raw, json
-example-
{
  "product_name": "New Product",
  "price": 30.00
}
PUT /products/<id>: To update an existing product.

DELETE /products/<id>: To delete a product.


# Extra Notes:
The project code will not run directly without setting up the environment as described. It's very sensitive to all steps.
If an error is made, it's best to CTRL +C the terminal, and re-run the it.
This README provides all necessary setup instructions to replicate the development environment.

-END
