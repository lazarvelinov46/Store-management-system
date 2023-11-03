from flask import Blueprint, request, Response, jsonify;
from models import database, Product, Category,ProductCategory,Order,ProductOrder;
from datetime import datetime;
from sqlalchemy import and_;
import io;
import csv;
from functools import wraps;
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request;

orderBlueprint = Blueprint ( "orders", __name__ );

def roleCheck ( role ):
    def innerRole ( function ):
        @wraps ( function )
        def decorator ( *arguments, **keywordArguments ):
            verify_jwt_in_request ( );
            claims = get_jwt ( );
            if ( ( "roles" in claims ) and ( role in claims["roles"] ) ):
                return function ( *arguments, **keywordArguments );
            else:
                return jsonify({'msg':"Missing Authorization Header"}),401;

        return decorator;

    return innerRole;



@orderBlueprint.route ( "/order", methods = ["POST"] )
@roleCheck(role='customer')
def uploadOrder ():
    requests=request.json.get("requests","");
    if(requests==""):
        return jsonify(message="Field requests is missing."),400;
    email=get_jwt_identity();
    prices=[];
    quantities=[]
    productids=[];
    totalPrice=0;
    i=0;
    for r in requests:
        id=r.get('id','');
        if(id==''):
            retstr="Product id is missing for request number "+str(i)+'.';
            return jsonify(message=retstr),400;
        quant=r.get('quantity','')
        if(quant==''):
            retstr="Product quantity is missing for request number "+str(i)+'.';
            return jsonify(message=retstr),400;
        try:
            id=int(id);
        except ValueError:
            retstr="Invalid product id for request number "+str(i)+'.';
            return jsonify(message=retstr),400;
        if(not id or id<0):
            retstr="Invalid product id for request number "+str(i)+'.';
            return jsonify(message=retstr),400;
        try:
            quant=int(quant);
        except ValueError:
            retstr = "Invalid product quantity for request number " + str(i) + '.';
            return jsonify(message=retstr), 400;
        if(not quant or quant<0):
            retstr="Invalid product quantity for request number "+str(i)+'.';
            return jsonify(message=retstr),400;
        product=Product.query.filter(Product.id==id).first();
        if(not product):
            retstr="Invalid product for request number "+str(i)+'.';
            return jsonify(message=retstr),400;
        prices.append(product.price*quant);
        quantities.append(quant);
        productids.append(id);
        totalPrice=totalPrice+product.price*quant;

        i=i+1;

    order=Order(price=totalPrice, status="CREATED", timestamp=datetime.now(), email=email);
    database.session.add(order);
    database.session.commit();

    idord=order.id;
    i=0
    for r in requests:
        orderProd=ProductOrder(productId=productids[i],orderId=idord,quantity=quantities[i],price=prices[i]);
        database.session.add(orderProd);
        database.session.commit();
        i=i+1;
    return jsonify({'id':idord}),200

@orderBlueprint.route("/status",methods=["GET"])
@roleCheck(role='customer')
def getOrders():
    email=get_jwt_identity();
    orders=[];
    orders=Order.query.filter(Order.email==email).all();
    ordersjson=[];
    for o in orders:
        productsjson=[];
        products=database.session.query(Product.id,Product.name,Product.price,ProductOrder.quantity)\
        .filter(and_(ProductOrder.orderId==o.id,
                     Product.id==ProductOrder.productId)).all();
        for p in products:
            categories=database.session.query(Category.categoryName).filter(and_(*[
                ProductCategory.productId==int(p[0]),
                ProductCategory.categoryId==Category.id
            ])).all();
            catput=[];
            i=0
            for c in categories:
                catput.append(c[0])
                print(c[0]);
                i=i+1;
            print(catput)
            temp={
                "categories":catput,
                "name":p[1],
                "price":p[2],
                "quantity":p[3]
            }
            productsjson.append(temp);
        ordtemp={
            "products":productsjson,
            "price":o.price,
            "status":o.status,
            "timestamp":o.timestamp.isoformat()
        }
        ordersjson.append(ordtemp);
    return jsonify(orders=ordersjson),200;

@orderBlueprint.route("/delivered",methods=["POST"])
@roleCheck(role='customer')
def setDelivered():
    email=get_jwt_identity();
    id=request.json.get("id","");
    if(id==""):
        return jsonify(message="Missing order id."),400;
    try:
        id = int(id);
    except ValueError:
        return jsonify(message="Invalid order id."),400;
    if(not id or id<0):
        return jsonify(message="Invalid order id."),400;
    order=Order.query.filter(Order.email==email,Order.id==id).first();
    if(not order or order.status!="PENDING"):
        return jsonify(message="Invalid order id."),400;
    order.status="COMPLETE";
    productids=database.session.query(Product.id,ProductOrder.quantity).filter(and_(
        id==ProductOrder.orderId,
        Product.id==ProductOrder.productId
    )).all();
    for p in productids:
        cat=Category.query.filter(and_(
            p[0]==ProductCategory.productId,
            ProductCategory.categoryId==Category.id
        )).all();
        for c in cat:
            print(int(p[1]))
            c.delivered=c.delivered+int(p[1]);
            database.session.commit();
    print(productids);
    database.session.commit();
    return Response("",status=200);

@orderBlueprint.route("/orders_to_deliver",methods=["GET"])
@roleCheck(role='courier')
def getUndelivered():
    ordersInfo=database.session.query(Order.id,Order.email).filter(Order.status=="CREATED").all();
    ordersjson=[];
    for o in ordersInfo:
        jtemp={
            "id":o[0],
            "email":o[1]
        }
        ordersjson.append(jtemp);
    return jsonify(orders=ordersjson),200;

@orderBlueprint.route("/pick_up_order",methods=["POST"])
@roleCheck(role='courier')
def setPending():
    id = request.json.get("id", "");
    if (id == ""):
        return jsonify(message="Missing order id."), 400;
    try:
        id = int(id);
    except ValueError:
        return jsonify(message="Invalid order id."), 400;
    if (not id or id < 0):
        return jsonify(message="Invalid order id."), 400;
    order = Order.query.filter(Order.id == id).first();
    if (not order or order.status != "CREATED"):
        return jsonify(message="Invalid order id."), 400;
    order.status="PENDING";
    database.session.commit();
    return Response("",status=200);