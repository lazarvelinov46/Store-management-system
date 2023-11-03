from configuration import Configuration;
from flask import Flask,Blueprint, request, Response, jsonify;
from functools import wraps;
from models import database, Product, Category,ProductCategory,ProductOrder,Order;
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request;
from sqlalchemy import and_,or_,func,desc;
import requests;
import io;
import csv;

application = Flask ( __name__ );
application.config.from_object (Configuration )
jwt=JWTManager(application)

#application.register_blueprint ( productBlueprint, url_prefix = "/products" );
#application.register_blueprint(categoryBlueprint,url_prefix='/categories');

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

@application.route ( "/update", methods = ["POST"] )
@roleCheck(role='owner')
def updateProduct ():
    file=request.files.get("file",None);
    if(not file):
        return jsonify({'message':'Field file is missing.'}),400;
    content = file.stream.read ( ).decode ( "utf-8" );
    stream = io.StringIO ( content );
    reader = csv.reader ( stream );
    line=0;
    for row in reader:
        prodid=-1;
        if(len(row)!=3):
            print(row);
            res='Incorrect number of values on line '+str(line)+'.';
            return jsonify({'message':res}),400;
        try:
            prover=float(row[2]);
        except ValueError:
            res='Incorrect price on line '+str(line)+'.';
            return jsonify({'message':res}),400;
        if(not prover or prover<0):
            res='Incorrect price on line '+str(line)+'.';
            return jsonify({'message':res}),400;
        line=line+1;
    stream = io.StringIO(content);
    reader = csv.reader(stream);
    products = [ ];
    line=-1;
    for row in reader:
        name=row[1];
        temp=Product.query.filter(Product.name==name).first();
        if(temp):
            res='Product '+name+' already exists.';
            return jsonify({'message':res}),400;

    stream = io.StringIO ( content );
    reader = csv.reader ( stream );
    for row in reader:
        prodid=-1;

        categories=row[0];
        categoryList=categories.split("|");
        catIds=[];

        print(categoryList);
        for cat in categoryList:
            check=Category.query.filter(Category.categoryName==cat).first();
            if(not(check)):
                addCat=Category(categoryName=cat,delivered=0);
                print(addCat);
                database.session.add(addCat);
                database.session.flush();
                catIds.append(addCat.id);
                database.session.commit();
            else:
                catIds.append(check.id);
        product=Product(name=row[1],price=float(row[2]));
        database.session.add(product);
        database.session.flush();
        prodid=product.id;
        database.session.commit();
        for catid in catIds:
            pc=ProductCategory(productId=prodid,categoryId=catid);
            database.session.add(pc);
            database.session.commit();

        line=line+1;
    return Response("",status=200);

@application.route ( "/product_statistics", methods = ["GET"] )
@roleCheck(role='owner')
def getProductStatistics ():
    productids=[]
    productids=database.session.query(Product.id,Product.name).all();
    sold=[]
    waiting=[]
    ret=[];
    for p in productids:
        s=database.session.query(func.sum(ProductOrder.quantity)).filter(and_(
            ProductOrder.productId==p[0],ProductOrder.orderId==Order.id,Order.status=="COMPLETE")).all();
        w=database.session.query(func.sum(ProductOrder.quantity)).filter(and_(
            ProductOrder.productId==p[0],ProductOrder.orderId==Order.id,or_(Order.status=="PENDING",Order.status=="CREATED"))).all();
        rets=0
        retw=0
        if(s[0][0]):
            rets=int(s[0][0]);
        if(w[0][0]):
            retw=int(w[0][0]);
        if(rets==0 and retw==0):
            continue;
        ret.append(
            {
                "name":p[1],
                "sold":rets,
                "waiting":retw
            }
        )
    return jsonify(statistics=ret),200;

@application.route ( "/product_statisticss", methods = ["GET"] )
@roleCheck(role='owner')
def getProductStatisticss ():
    url = "http://sparkapp:5005/product_statistics"
    response = requests.get(url)
    if response.status_code==200:
        return response.json();
    return jsonify({'response':response.status_code});

@application.route ( "/category_statisticss", methods = ["GET"] )
@roleCheck(role='owner')
def getCategoryStatisticss ():
    categoriesDelivered=database.session.query(Category.categoryName).order_by(
        desc(Category.delivered),Category.categoryName
    ).all();
    catret=[]
    for c in categoriesDelivered:
        catret.append(c[0]);
    return jsonify(statistics=catret),200;

@application.route ( "/category_statistics", methods = ["GET"] )
@roleCheck(role='owner')
def getCategoryStatistics ():
    url = "http://sparkapp:5005/category_statistics"
    response = requests.get(url)
    return response.json();

if (__name__ == "__main__"):
    database.init_app ( application );
    application.run ( debug = True,host = "0.0.0.0",port=5000 );
