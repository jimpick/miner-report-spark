#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

r"""
 Counts words in UTF8 encoded, '\n' delimited text received from the network.
 Usage: structured_network_wordcount.py <hostname> <port>
   <hostname> and <port> describe the TCP server that Structured Streaming
   would connect to receive data.
To run this on your local machine, you need to first run a Netcat server
    `$ nc -lk 9999`
 and then run the example
    `$ bin/spark-submit examples/src/main/python/sql/streaming/structured_network_wordcount.py
    localhost 9999`
"""
import sys
import time

from pyspark.sql import SparkSession
from pyspark.sql.functions import date_format
from pyspark.sql.functions import window
from pyspark.sql.types import StructType

if __name__ == "__main__":
    spark = SparkSession\
        .builder\
        .appName("MinerPowerStaging")\
        .getOrCreate()

    schema = StructType() \
        .add("epoch", "long") \
        .add("timestamp", "timestamp") \
        .add("tipSet", "string") \
        .add("miner", "string") \
        .add("rawBytePower", "double") \
        .add("qualityAdjPower", "double")

    # Create DataFrame representing the stream of input lines from connection to host:port
    minerPower = spark \
        .readStream \
        .schema(schema) \
        .json('input-staging') \
        .withWatermark("timestamp", "1 second")

        #.option('cleanSource', 'archive') \
        #.option('sourceArchiveDir', 'archive-staging') \

    minerPower = minerPower.withColumn(
        "date", minerPower.timestamp.astype('date'))

    # Generate running word count
    # wordCounts = words.groupBy('word').count()

    numberOfRecords = minerPower.groupBy().count()

    #averagePowerHourly = minerPower.groupBy(
    #    minerPower.miner,
    #    minerPower.date,
    #    window(minerPower.timestamp, '1 hour')
    #).avg("rawBytePower", "qualityAdjPower")

    #averagePowerDaily = minerPower.groupBy(
    #    minerPower.miner,
    #    minerPower.date,
    #    window(minerPower.timestamp, '1 day')
    #).avg("rawBytePower", "qualityAdjPower")

    averagePowerMultiDay = minerPower.groupBy(
        minerPower.miner,
        window(minerPower.timestamp, '2 day', '2 day')
        #window(minerPower.timestamp, '2 day')
    ).avg("rawBytePower", "qualityAdjPower")

    # Start running the query that prints the running counts to the console
    # def output_counts(df, epoch_id):
    #    df.coalesce(1).write.csv('output/word_counts', mode='overwrite')
    #    pass

    # query = minerPower\
    #    .writeStream\
    #    .outputMode('complete')\
    #    .foreachBatch(output_counts)\
    #    .start()

    #query = minerPower \
    #    .writeStream \
    #    .queryName("json") \
    #    .format("json") \
    #    .option("path", "output-staging/json") \
    #    .option("checkpointLocation", "checkpoint-staging/json") \
    #    .partitionBy("date", "miner") \
    #    .start()

    # .repartition(1) \

    # Start running the query that prints the running counts to the console
    query2 = numberOfRecords \
        .writeStream \
        .queryName("counter") \
        .outputMode('complete') \
        .format('console') \
        .start()

    #query3 = averagePowerHourly \
    #    .writeStream \
    #    .queryName("json_avg_power_hourly") \
    #    .format("json") \
    #    .option("path", "output-staging/json_avg_power_hourly") \
    #    .option("checkpointLocation", "checkpoint-staging/json_avg_power_hourly") \
    #    .partitionBy("date", "miner") \
    #    .start()

    #query4 = averagePowerDaily \
    #    .writeStream \
    #    .queryName("json_avg_power_daily") \
    #    .format("json") \
    #    .option("path", "output-staging/json_avg_power_daily") \
    #    .option("checkpointLocation", "checkpoint-staging/json_avg_power_daily") \
    #    .partitionBy("date", "miner") \
    #    .start()

    query5 = averagePowerMultiDay \
        .writeStream \
        .queryName("json_avg_power_multiday") \
        .format("json") \
        .option("path", "output-staging/json_avg_power_multiday") \
        .option("checkpointLocation", "checkpoint-staging/json_avg_power_multiday") \
        .partitionBy("window", "miner") \
        .start()

    while True:
        #print("json", query.lastProgress)
        print("total", query2.lastProgress)
        #print("json_avg_power_hourly", query3.lastProgress)
        #print("json_avg_power_daily", query4.lastProgress)
        #print("json_avg_power_multiday", query5.lastProgress)
        print()
        time.sleep(60)

    #query.awaitTermination()
    #query2.awaitTermination()
    #query3.awaitTermination()
    #query4.awaitTermination()
    #query5.awaitTermination()
