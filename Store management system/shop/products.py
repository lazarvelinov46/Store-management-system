from flask import Blueprint, request, Response, jsonify;
from models import database, Product, Category,ProductCategory,ProductOrder,Order;
from configuration import Configuration
from sqlalchemy import and_,or_,func;
from functools import wraps;
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request;
import io;
import csv;

productBlueprint = Blueprint ( "products", __name__ );

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

@productBlueprint.route ( "/update", methods = ["POST"] )
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

@productBlueprint.route ( "/product_statistics", methods = ["GET"] )
@roleCheck(role='owner')
def getProductStatistics ():
    productids=[]
    productids=database.session.query(Product.id,Product.name).all();
    sold=[]
    waiting=[]
    ret=[];
    for p in productids:
        s=database.session.query(func.sum(0+ProductOrder.quantity)).filter(and_(
            ProductOrder.productId==p[0],ProductOrder.orderId==Order.id,Order.status=="COMPLETE")).all();
        w=database.session.query(func.sum(0+ProductOrder.quantity)).filter(and_(
            ProductOrder.productId==p[0],ProductOrder.orderId==Order.id,or_(Order.status=="PENDING",Order.status=="CREATED"))).all();
        rets=0
        retw=0
        if(s[0][0]):
            rets=int(s[0][0]);
        if(w[0][0]):
            retw=int(w[0][0]);
        ret.append(
            {
                "name":p[1],
                "sold":rets,
                "waiting":retw
            }
        )
    return jsonify(statistics=ret),200;

@productBlueprint.route ( "/search", methods = ["GET"] )
@roleCheck(role='customer')
def getProduct ():
    name=request.args.get('name','');
    categ=request.args.get('category','')
    #asdf
    cats=[];
    prods=[];
    cats = Category.query.join(ProductCategory).join(Product).filter \
        (and_(Category.categoryName.like(f"%{categ}%"),Product.name.like(f"%{name}%"))).all();
    categoriesRet=[];
    for c in cats:
        categoriesRet.append(c.categoryName);
    print(categoriesRet);
    prods=Product.query.join(ProductCategory).join(Category).filter \
        (and_(Category.categoryName.like(f"%{categ}%"),Product.name.like(f"%{name}%"))).all();
    productsRet=[];
    for p in prods:
        prodcats=[]
        for cat in p.categories:
            prodcats.append(cat.categoryName);
        print(prodcats)
        productsRet.append({
            'categories':prodcats,
            'id':p.id,
            'name':p.name,
            'price':p.price
        })
    retval={
        'categories':categoriesRet,
        'products':productsRet
    }
    return jsonify(retval),200;

