from flask import Blueprint, request;
from shop.models import database, Product,Statistic;
import io;

statisticBlueprint = Blueprint ( "statistics", __name__ );


@statisticBlueprint.route ( "/product_statistics", methods = ["GET"] )
def getProductStatistics ():
    productStatistics=[]
    productStatistics=Statistic.query.all();

