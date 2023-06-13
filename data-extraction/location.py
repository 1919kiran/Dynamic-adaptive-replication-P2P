import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType


def ipv4_to_32bit_int(ipv4):
    a, b, c, d = [int(x) for x in ipv4.split('.')]
    return (a << 24) + (b << 16) + (c << 8) + d


def interleave_bits(x, y):
    z = 0
    for i in range(16):
        z |= (x & 1 << i) << i | (y & 1 << i) << (i + 1)
    return z


def z_curve_mapping(ipv4):
    ip_int = ipv4_to_32bit_int(ipv4)
    x = ip_int & 0xAAAAAAAA
    y = ip_int & 0x55555555
    x = (x | (x >> 1)) & 0x33333333
    x = (x | (x >> 2)) & 0x0F0F0F0F
    x = (x | (x >> 4)) & 0x00FF00FF
    x = (x | (x >> 8)) & 0x0000FFFF
    y = (y | (y >> 1)) & 0x33333333
    y = (y | (y >> 2)) & 0x0F0F0F0F
    y = (y | (y >> 4)) & 0x00FF00FF
    y = (y | (y >> 8)) & 0x0000FFFF
    morton_number = interleave_bits(x, y)
    lat = (morton_number / (2 ** 32 - 1)) * 180 - 90
    lng = (morton_number % (2 ** 32 - 1)) * 360 / (2 ** 32 - 1) - 180
    return round(lat, 5), round(lng, 5)


spark = SparkSession.builder \
    .appName("Add Lat and Lon to DataFrame") \
    .getOrCreate()

schema = StructType([
    StructField("src_ip", StringType(), True),
    StructField("dest_ip", StringType(), True),
    StructField("timestamp", StringType(), True)
])

input_file = "requests.csv"

df = spark.read.csv(input_file, header=True, schema=schema)


def safe_z_curve_mapping(src_ip):
    try:
        lat, lon = z_curve_mapping(src_ip)
        return lat, lon
    except Exception as e:
        return None, None


safe_z_curve_mapping_udf = udf(safe_z_curve_mapping, returnType=StructType([
    StructField("lat", DoubleType(), True),
    StructField("lon", DoubleType(), True)
]))

df_with_lat_lon = df.withColumn("lat_lon", safe_z_curve_mapping_udf(col("src_ip")))
df_with_lat_lon = df_with_lat_lon.select("src_ip", "dest_ip", "timestamp", "lat_lon.lat", "lat_lon.lon")

df_filtered = df_with_lat_lon.dropna()
df = df_filtered.drop("src_ip")

df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')
time_diff = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()
df['timestamp_delta'] = time_diff

output_dir = "output"
df = df.repartition(1)
df.write.csv(output_dir, header=True, mode="overwrite")

spark.stop()
