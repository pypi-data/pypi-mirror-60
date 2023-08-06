from fastavro import reader
import boto3
import pandas as pd
import io
from tqdm import tqdm
import s3fs
import pyarrow.parquet as pq

TABLE = "TABLE"


def byte_avro_to_pandas_df(byte_stream, verbose=True, output_format=TABLE):
    avro_reader = reader(byte_stream)
    data = []
    it = tqdm(avro_reader) if verbose else avro_reader
    for record in it:
        if output_format == TABLE:
            data.append(record["after"])
        else:
            data.append(record)
    return pd.DataFrame(data)


def get_all_s3_objects(s3, **base_kwargs):
    continuation_token = None
    count = 1
    while True:
        print(count)
        count += 1
        list_kwargs = dict(MaxKeys=1000, **base_kwargs)
        if continuation_token:
            list_kwargs["ContinuationToken"] = continuation_token
        response = s3.list_objects_v2(**list_kwargs)
        yield response
        if not response.get("IsTruncated"):  # At the end of the list?
            break
        continuation_token = response.get("NextContinuationToken")


def read_parquet_file_from_s3(s3_path):

    s3 = s3fs.S3FileSystem()
    # read all parquet file
    df = pq.ParquetDataset(s3_path, filesystem=s3).read_pandas().to_pandas()
    return df

