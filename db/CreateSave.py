import pandas as pd
from sqlalchemy import create_engine

'''
infile = r'path/to/file.csv'
db = 'a001_db'
db_tbl_name = 'a001_rd004_db004'
user, password, host, port, database
'''

'''
Load a csv file into a dataframe; if csv does not have headers, use the headers arg to create a list of headers; rename unnamed columns to conform to mysql column requirements
'''
def csv_to_df(infile, headers = []):
    if len(headers) == 0:
        df = pd.read_csv(infile)
    else:
        df = pd.read_csv(infile, header = None)
        df.columns = headers
    for r in range(10):
        try:
            df.rename( columns={'Unnamed: {0}'.format(r):'Unnamed{0}'.format(r)}, inplace=True )
        except:
            pass
    return df

'''
Create a mapping of df dtypes to mysql data types (not perfect, but close enough)
'''
def dtype_mapping():
    return {'object' : 'TEXT',
        'int64' : 'INT',
        'float64' : 'FLOAT',
        'datetime64' : 'DATETIME',
        'bool' : 'TINYINT',
        'category' : 'TEXT',
        'timedelta[ns]' : 'TEXT'}
'''
Create a sqlalchemy engine
'''
def mysql_engine(user, password, host, port, database):
    engine = create_engine("mysql://{0}:{1}@{2}:{3}/{4}?charset=utf8".format(user, password, host, port, database))
    return engine

'''
Create a mysql connection from sqlalchemy engine
'''
def mysql_conn(engine):
    conn = engine.raw_connection()
    return conn
'''
Create sql input for table names and types
'''
def gen_tbl_cols_sql(df):
    dmap = dtype_mapping()
    # sql = "pi_db_uid INT AUTO_INCREMENT PRIMARY KEY"
    sql=""
    # df = df.rename(columns = {"" : "nocolname"})
    hdrs = df.dtypes.index
    hdrs_list = [(hdr, str(df[hdr].dtype)) for hdr in hdrs]
    for i, hl in enumerate(hdrs_list):
        sql += " ,{0} {1}".format(hl[0], dmap[hl[1]])
    return sql

'''
Create a mysql table from a df
'''
def create_mysql_tbl_schema(df, conn, db, tbl_name):
    tbl_cols_sql = gen_tbl_cols_sql(df)
    sql = "USE {0}; CREATE TABLE {1} ({2})".format(db, tbl_name, tbl_cols_sql)
    cur = conn.cursor()
    cur.execute(sql)
    cur.close()
    conn.commit()

'''
Write df data to newly create mysql table
'''
def df_to_mysql(df, engine, tbl_name):
    df.to_sql(tbl_name, engine, if_exists='replace')

if __name__ == '__main__':
    df = csv_to_df(infile)
    create_mysql_tbl_schema(df, mysql_conn(mysql_engine()), db, db_tbl_name)
    df_to_mysql(df, mysql_engine(), db_tbl_name)