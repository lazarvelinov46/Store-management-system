from flask_sqlalchemy import SQLAlchemy;

database = SQLAlchemy ( );

class ProductCategory(database.Model):
    id = database.Column ( database.Integer, primary_key = True );
    productId=database.Column(database.Integer,database.ForeignKey("products.id"),nullable=False);
    categoryId=database.Column(database.Integer,database.ForeignKey("categories.id"),nullable=False);
class ProductOrder(database.Model):
    id=database.Column(database.Integer,primary_key=True);
    productId=database.Column(database.Integer,database.ForeignKey("products.id"),nullable=False);
    orderId=database.Column(database.Integer,database.ForeignKey("orders.id"),nullable=False);
    quantity=database.Column(database.Integer,nullable=False);
    price=database.Column(database.Float,nullable=False);
class Product ( database.Model ):
    __tablename__ = "products";
    id = database.Column ( database.Integer, primary_key = True );
    name=database.Column(database.String(256),nullable=False);
    price=database.Column(database.Float, nullable=False);

    categories=database.relationship("Category",secondary = ProductCategory.__table__,back_populates="products");
    orders=database.relationship("Order",secondary = ProductOrder.__table__,back_populates="products");


class Category(database.Model):
    __tablename__="categories";
    id=database.Column(database.Integer,primary_key=True);
    categoryName=database.Column(database.String(256),nullable=False);
    delivered=database.Column(database.Integer,nullable=False);
    products=database.relationship("Product",secondary = ProductCategory.__table__,back_populates="categories");

class Order ( database.Model ):
    __tablename__ = "orders";
    id = database.Column ( database.Integer, primary_key = True );
    price = database.Column ( database.Float, nullable = False );
    status = database.Column(database.String(20), nullable=False);
    timestamp=database.Column(database.DateTime,nullable=False);
    email=database.Column(database.String(256),nullable=False);

    products=database.relationship("Product",secondary = ProductOrder.__table__,back_populates="orders");

    def __repr__ ( self ):
        return "({}, {}, {}, {})".format ( self.id, self.title, str ( self.tags ), str ( self.comments ) );

