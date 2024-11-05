import mysql.connector
import os
from dotenv import load_dotenv

# Function to create a connection to the MySQL database
def create_connection():
    try:
        load_dotenv()
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def create_tables():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        queries = [
            '''
            CREATE TABLE IF NOT EXISTS Category (
                categoryId INT AUTO_INCREMENT PRIMARY KEY,
                categoryName VARCHAR(255) NOT NULL
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS User (
                userId INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                phone VARCHAR(15),
                email VARCHAR(255) NOT NULL UNIQUE,
                passwdHash VARCHAR(255) NOT NULL,
                firstName VARCHAR(255) NOT NULL,
                lastName VARCHAR(255) NOT NULL,
                houseFlatNo VARCHAR(255),
                street VARCHAR(255),
                city VARCHAR(255),
                pincode VARCHAR(10),
                dateJoined DATETIME NOT NULL,
                isVerified BOOLEAN DEFAULT FALSE
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Product (
                productId INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                `condition` ENUM('new', 'used', 'refurbished') NOT NULL,
                initialBid DECIMAL(10, 2) NOT NULL,
                currentBidPrice DECIMAL(10, 2),
                status ENUM('live', 'sold', 'upcoming') NOT NULL,
                startTime DATETIME NOT NULL,
                endTime DATETIME NOT NULL,
                userId INT,
                FOREIGN KEY (userId) REFERENCES User(userId)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Product_img (
                imageId INT AUTO_INCREMENT PRIMARY KEY,
                productId INT,
                imageURL VARCHAR(255) NOT NULL,
                FOREIGN KEY (productId) REFERENCES Product(productId)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Cat_Prod (
                categoryId INT,
                productId INT,
                PRIMARY KEY (categoryId, productId),
                FOREIGN KEY (categoryId) REFERENCES Category(categoryId),
                FOREIGN KEY (productId) REFERENCES Product(productId)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Bid (
                bidId INT AUTO_INCREMENT PRIMARY KEY,
                bidAmount DECIMAL(10, 2) NOT NULL,
                bidTime DATETIME NOT NULL,
                isWinningBid BOOLEAN DEFAULT FALSE,
                userId INT,
                productId INT,
                FOREIGN KEY (userId) REFERENCES User(userId),
                FOREIGN KEY (productId) REFERENCES Product(productId)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS `Order` (
                orderId INT AUTO_INCREMENT PRIMARY KEY,
                orderDate DATETIME NOT NULL,
                orderStatus ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled') NOT NULL,
                paymentTime DATETIME,
                paymentStatus ENUM('unpaid', 'paid') NOT NULL,
                paymentMethod ENUM('credit_card', 'debit_card', 'paypal', 'bank_transfer') NOT NULL,
                totalAmount DECIMAL(10, 2) NOT NULL,
                transactionId VARCHAR(255),
                userId INT,
                productId INT,
                FOREIGN KEY (userId) REFERENCES User(userId),
                FOREIGN KEY (productId) REFERENCES Product(productId)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Shipment (
                shippingId INT AUTO_INCREMENT PRIMARY KEY,
                shippingMethod VARCHAR(255) NOT NULL,
                trackingNumber VARCHAR(255),
                carrierName VARCHAR(255),
                shippingStatus ENUM('pending', 'shipped', 'in_transit', 'delivered') NOT NULL,
                shippingCost DECIMAL(10, 2),
                estimatedDeliveryDate DATE,
                houseFlatNo VARCHAR(255) NOT NULL,
                street VARCHAR(255) NOT NULL,
                city VARCHAR(255) NOT NULL,
                pincode VARCHAR(10) NOT NULL,
                orderId INT,
                FOREIGN KEY (orderId) REFERENCES `Order`(orderId)
            )
            '''
        ]

        for query in queries:
            cursor.execute(query)

        connection.commit()
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    
    finally:
        cursor.close()
        connection.close()
