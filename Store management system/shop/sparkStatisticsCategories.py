from pyspark.sql import SparkSession

import os
from pyspark.sql.functions import desc

PRODUCTION = True if ("PRODUCTION" in os.environ) else False
DATABASE_URL = os.environ["DATABASE_URL"] if ("DATABASE_URL" in os.environ) else "localhost"

builder = SparkSession.builder.appName("PySpark categoryStatistics")

if (not PRODUCTION):
    builder = builder.master("local[*]") \
        .config(
        "spark.driver.extraClassPath",
        "mysql-connector-j-8.0.33.jar"
    )

spark = builder.getOrCreate()

categories_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_URL}:3306/shopDatabase") \
    .option("dbtable", "shopDatabase.categories") \
    .option("user", "root") \
    .option("password", "root") \
    .load()


result=categories_data_frame.orderBy(desc(categories_data_frame['delivered']),categories_data_frame['categoryName']);

names=result.select('categoryName').collect()
print('podaci')
for n in names:
    print(n);
    print('|');
print('podaci');
spark.stop();

# people_data_frame.show ( )
# result = people_data_frame.filter ( people_data_frame["gender"] == "Male" ).collect ( )
# print ( result )
