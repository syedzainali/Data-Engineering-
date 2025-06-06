#!/usr/bin/env python
# coding: utf-8
import os
import argparse
import pandas as pd
from time import time
from sqlalchemy import create_engine

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    parquet_name = 'output.parquet'
    csv_name = 'output.csv'

    
    os.system(f"wget {url} -O {parquet_name}")
    #os.system(f"curl -o {parquet_name} {url}")
    #os.system(f"wget {url} -o {csv_name}")
    


    df_parquet = pd.read_parquet(parquet_name, engine='pyarrow')
    df_parquet.to_csv(csv_name, index=False)

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
 
    df_iter = pd.read_csv(csv_name, iterator= True, chunksize=100000)

    df= next(df_iter)

    df.tpep_pickup_datetime  = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(n=0).to_sql(name=table_name , con=engine , if_exists='replace')

    df.to_sql(name=table_name , con=engine , if_exists='append')

    while True:
        t_start = time()

        df= next(df_iter)

        df.tpep_pickup_datetime  = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

        df.to_sql(name=table_name , con=engine , if_exists='append')

        t_end = time()

        print('Inserted another chunk....., took %.3f seconds' % (t_end - t_start))

if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='Ingest CSV ata to Postgres')

    #user , passwrod, host, port, databse name, table name, url of the csv

    parser.add_argument('--user' , help= 'user name for postgres') 
    parser.add_argument('--password' , help= 'user password for postgres') 
    parser.add_argument('--host' , help= 'host for postgres') 
    parser.add_argument('--port' , help= 'port for postgres') 
    parser.add_argument('--db' , help= 'database name for postgres')
    parser.add_argument('--table_name' , help= 'name of the table wehre we will write the results to')
    parser.add_argument('--url' , help= 'url of the scv file')

    args = parser.parse_args()
    
    main(args)

























