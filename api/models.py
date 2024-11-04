from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'Category'
    categoryId = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(255), nullable=False)

    products = db.relationship('Product', secondary='Cat_Prod', backref=db.backref('categories', lazy=True))

class User(db.Model):
    __tablename__ = 'User'
    userId = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(255), nullable=False, unique=True)
    passwdHash = db.Column(db.String(255), nullable=False)
    firstName = db.Column(db.String(255), nullable=False)
    lastName = db.Column(db.String(255), nullable=False)
    houseFlatNo = db.Column(db.String(255))
    street = db.Column(db.String(255))
    city = db.Column(db.String(255))
    pincode = db.Column(db.String(10))
    dateJoined = db.Column(db.DateTime, nullable=False)
    isVerified = db.Column(db.Boolean, default=False)

    listed_products = db.relationship('Product', backref='product_owner', lazy=True, cascade='all, delete-orphan')
    bids = db.relationship('Bid', backref='bidder', lazy=True)
    reviews = db.relationship('Review', backref='reviewer', lazy=True, cascade='all, delete-orphan')
    messages_sent = db.relationship('Messages', foreign_keys='Messages.sellerId', backref='seller', lazy=True, cascade='all, delete-orphan')
    messages_received = db.relationship('Messages', foreign_keys='Messages.receiverId', backref='receiver', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')

class Product(db.Model):
    __tablename__ = 'Product'
    productId = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    condition = db.Column(db.Enum('new', 'used', 'refurbished'), nullable=False)
    initialBid = db.Column(db.Numeric(10, 2), nullable=False)
    currentBidPrice = db.Column(db.Numeric(10, 2))
    status = db.Column(db.Enum('active', 'sold', 'expired'), nullable=False)
    startTime = db.Column(db.DateTime, nullable=False)
    endTime = db.Column(db.DateTime, nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('User.userId'), nullable=False)

    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')
    bids = db.relationship('Bid', backref='product', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='product', lazy=True)
    messages = db.relationship('Messages', backref='product', lazy=True, cascade='all, delete-orphan')

class ProductImage(db.Model):
    __tablename__ = 'Product_img'
    imageId = db.Column(db.Integer, primary_key=True)
    productId = db.Column(db.Integer, db.ForeignKey('Product.productId'), nullable=False)
    imageURL = db.Column(db.String(255), nullable=False)

class CatProd(db.Model):
    __tablename__ = 'Cat_Prod'
    categoryId = db.Column(db.Integer, db.ForeignKey('Category.categoryId'), primary_key=True)
    productId = db.Column(db.Integer, db.ForeignKey('Product.productId'), primary_key=True)

class Bid(db.Model):
    __tablename__ = 'Bid'
    bidId = db.Column(db.Integer, primary_key=True)
    bidAmount = db.Column(db.Numeric(10, 2), nullable=False)
    bidTime = db.Column(db.DateTime, nullable=False)
    isWinningBid = db.Column(db.Boolean, default=False)
    userId = db.Column(db.Integer, db.ForeignKey('User.userId'), nullable=False)
    productId = db.Column(db.Integer, db.ForeignKey('Product.productId'), nullable=False)

class Order(db.Model):
    __tablename__ = 'Order'
    orderId = db.Column(db.Integer, primary_key=True)
    orderDate = db.Column(db.DateTime, nullable=False)
    orderStatus = db.Column(db.Enum('pending', 'confirmed', 'shipped', 'delivered', 'cancelled'), nullable=False)
    paymentTime = db.Column(db.DateTime)
    paymentStatus = db.Column(db.Enum('unpaid', 'paid'), nullable=False)
    paymentMethod = db.Column(db.Enum('credit_card', 'debit_card', 'paypal', 'bank_transfer'), nullable=False)
    totalAmount = db.Column(db.Numeric(10, 2), nullable=False)
    transactionId = db.Column(db.String(255))
    userId = db.Column(db.Integer, db.ForeignKey('User.userId'), nullable=False)
    productId = db.Column(db.Integer, db.ForeignKey('Product.productId'), nullable=False)

    shipment = db.relationship('Shipment', backref='order', uselist=False, cascade='all, delete-orphan')

class Shipment(db.Model):
    __tablename__ = 'Shipment'
    shippingId = db.Column(db.Integer, primary_key=True)
    shippingMethod = db.Column(db.String(255), nullable=False)
    trackingNumber = db.Column(db.String(255))
    carrierName = db.Column(db.String(255))
    shippingStatus = db.Column(db.Enum('pending', 'shipped', 'in_transit', 'delivered'), nullable=False)
    shippingCost = db.Column(db.Numeric(10, 2))
    estimatedDeliveryDate = db.Column(db.Date)
    houseFlatNo = db.Column(db.String(255), nullable=False)
    street = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    orderId = db.Column(db.Integer, db.ForeignKey('Order.orderId'), nullable=False)

class Review(db.Model):
    __tablename__ = 'Review'
    reviewId = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    reviewDate = db.Column(db.DateTime, nullable=False)
    productId = db.Column(db.Integer, db.ForeignKey('Product.productId'), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('User.userId'), nullable=False)

class Messages(db.Model):
    __tablename__ = 'Messages'
    messageId = db.Column(db.Integer, primary_key=True)
    sentTime = db.Column(db.DateTime, nullable=False)
    readTime = db.Column(db.DateTime)
    messageContent = db.Column(db.Text, nullable=False)
    productId = db.Column(db.Integer, db.ForeignKey('Product.productId'))
    sellerId = db.Column(db.Integer, db.ForeignKey('User.userId'))
    receiverId = db.Column(db.Integer, db.ForeignKey('User.userId'))
