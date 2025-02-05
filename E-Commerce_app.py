from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Table, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from marshmallow import Schema, fields, ValidationError
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import bcrypt

# Initialize Flask app
app = Flask(__name__)

# JWT Configuration
app.config['JWT_PERSONAL_KEY'] = '<YOUR_PERSONAL_KEY_HERE>'
jwt = JWTManager(app)

# MySQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://<USERNAME>:<PASSWORD>@localhost/ecommerce_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Creating Base Model
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy and Marshmallow
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

# Define the association table
order_product_association = Table('order_product', Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    extend_existing=True
)

# Models defined
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    address = Column(String(250))
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(150))
    orders = relationship('Order', back_populates='user')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(50), default='pending')
    user = relationship('User', back_populates='orders')
    products = relationship('Product', secondary=order_product_association, 
                            back_populates='orders')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    product_name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    orders = relationship('Order', secondary=order_product_association, 
                          back_populates='products')

# ============= Schemas ===============

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    address = fields.Str()
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    order_date = fields.DateTime()
    user_id = fields.Int(required=True)
    status = fields.Str()

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    product_name = fields.Str(required=True)
    price = fields.Float(required=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# ============= Routes ===============
# Authentication - Login
@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    user = db.session.query(User).filter_by(email=email).first()  
    if user and user.check_password(password):
        access_token = create_access_token(identity=email)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad email or password"}), 401

# Users Endpoints with JWT authentication
@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = db.session.query(User).paginate(page=page, per_page=per_page, error_out=False)  
    users = pagination.items
    return jsonify({
        'users': users_schema.dump(users),
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@app.route('/users/', methods=['GET'])
@jwt_required()
def get_user(id):
    user = db.session.query(User).get(id)  
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_schema.dump(user))

@app.route('/users', methods=['POST'])
def add_user():
    try:
        data = user_schema.load(request.json)
        user = User(name=data['name'], address=data.get('address', ''), email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify(user_schema.dump(user)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route('/users/', methods=['PUT'])
@jwt_required()
def update_user(id):
    user = db.session.query(User).get(id)  
    if user is None:
        return jsonify({"error": "User not found"}), 404
    try:
        data = user_schema.load(request.json, partial=True)
        user.name = data.get('name', user.name)
        user.address = data.get('address', user.address)
        user.email = data.get('email', user.email)
        if 'password' in data:
            user.set_password(data['password'])
        db.session.commit()
        return jsonify(user_schema.dump(user))
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route('/users/', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = db.session.query(User).get(id)  
    if user is None:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return '', 204

# Order Endpoints
@app.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(email=user_id).first()  
    if not user:
        return jsonify({"msg": "User not found"}), 404
    new_order = Order(user_id=user.id)
    db.session.add(new_order)
    db.session.commit()
    return jsonify(order_schema.dump(new_order)), 201

@app.route('/orders//add_product/', methods=['POST'])
@jwt_required()
def add_product_to_order(order_id, product_id):
    order = db.session.query(Order).get(order_id) 
    product = db.session.query(Product).get(product_id)  
    
    if product not in order.products:
        order.products.append(product)
        db.session.commit()
        return jsonify({"message": "Product added to order"}), 200
    return jsonify({"message": "Product already in order"}), 400

@app.route('/orders//remove_product', methods=['DELETE'])
@jwt_required()
def remove_product_from_order(order_id):
    order = db.session.query(Order).get(order_id)  
    product_id = request.json['product_id']
    product = db.session.query(Product).get(product_id)  
    if product in order.products:
        order.products.remove(product)
        db.session.commit()
        return jsonify({"message": "Product removed from order"}), 200
    return jsonify({"message": "Product not found in this order"}), 404

@app.route('/orders/user/', methods=['GET'])
@jwt_required()
def get_user_orders(user_id):
    user = db.session.query(User).get(user_id)  
    return jsonify(orders_schema.dump(user.orders))

@app.route('/orders//products', methods=['GET'])
@jwt_required()
def get_order_products(order_id):
    order = db.session.query(Order).get(order_id)  
    return jsonify(products_schema.dump(order.products))

# Products Endpoints
@app.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = db.session.query(Product).paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    return jsonify({
        'products': products_schema.dump(products),
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@app.route('/products/', methods=['GET'])
@jwt_required()
def get_product(id):
    product = db.session.query(Product).get(id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product_schema.dump(product))

@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    try:
        data = product_schema.load(request.json)
        new_product = Product(product_name=data['product_name'], price=data['price'])
        db.session.add(new_product)
        db.session.commit()
        return jsonify(product_schema.dump(new_product)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route('/products/', methods=['PUT'])
@jwt_required()
def update_product(id):
    product = db.session.query(Product).get(id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    try:
        data = product_schema.load(request.json, partial=True)
        product.product_name = data.get('product_name', product.product_name)
        product.price = data.get('price', product.price)
        db.session.commit()
        return jsonify(product_schema.dump(product))
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route('/products/', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    product = db.session.query(Product).get(id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    db.session.delete(product)
    db.session.commit()
    return '', 204

# ======== Bonus Endpoints for Order Management ==========
@app.route('/orders//cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    order = db.session.query(Order).get(order_id)  
    order.status = 'cancelled'
    db.session.commit()
    return jsonify({"message": "Order cancelled"}), 200

@app.route('/orders//ship', methods=['POST'])
@jwt_required()
def ship_order(order_id):
    order = db.session.query(Order).get(order_id)  
    order.status = 'shipped'
    db.session.commit()
    return jsonify({"message": "Order shipped"}), 200

# Final touch to make it run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)