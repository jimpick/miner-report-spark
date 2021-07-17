import os
import sys
import time

from pyspark.sql import SparkSession

if os.path.exists('src.zip'):
    sys.path.insert(0, 'src.zip')
else:
    sys.path.insert(0, './src')

from miner_power import miner_power
from miner_info import miner_info
from deals import deals
from client_names import client_names
from asks import asks
from dht_addrs import dht_addrs
from multiaddrs_ips import multiaddrs_ips

if __name__ == "__main__":
    spark = SparkSession\
        .builder\
        .appName("MinerReportStaging")\
        .getOrCreate()

    suffix = '-staging'

    #miner_power.process_miner_power(spark, suffix)

    #miner_info.process_miner_info(spark, suffix)

    #names = client_names.process_client_names(spark, suffix)

    #deals.process_deals(spark, names, suffix)

    #asks.process_asks(spark, suffix)

    #dht_addrs.process_dht_addrs(spark, suffix)

    multiaddrs_ips.process_multiaddrs_ips(spark, suffix)

    while True:
        for stream in spark.streams.active:
            message = stream.status['message']
            if message != "Waiting for data to arrive" and \
                    message != "Waiting for next trigger" and \
                    message.find("Getting offsets") == -1:
                print(stream.name, message)
        time.sleep(1)
