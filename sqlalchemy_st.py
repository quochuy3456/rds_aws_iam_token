import boto3
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import event
from urllib.parse import quote_plus
import time

Base = automap_base()

mysql_attr_ssl_ca = "./rds-ca-2019-root.pem"
region_name = "ap-northeast-1"
host = "database-1.cgjasvizzmcb.ap-northeast-1.rds.amazonaws.com"
port = 3306
user = "rds_iam_user"
passwd = "Quochuydo!1994"

ssl_args = {'ssl': {'ca': mysql_attr_ssl_ca}}


def get_authentication_token():
    client = boto3.client('rds', region_name=region_name)
    token = client.generate_db_auth_token(DBHostname=host,
                                          Port=port,
                                          DBUsername=user,
                                          Region=region_name)
    iam_token = quote_plus(token)
    return iam_token


mysql_connection_url = 'mysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(user, get_authentication_token(), host,
                                                                       str(port), "isoar")
engine = create_engine(mysql_connection_url,
                       connect_args=ssl_args,
                       pool_recycle=10)

session_mysql = Session(engine, autoflush=True)
Base.prepare(engine, reflect=True)


@event.listens_for(engine, "do_connect")
def provide_token(dialect, conn_rec, cargs, cparams):
    print("cparams: ", cparams)
    print("dialect: ", dialect)
    print("conn_rec: ", conn_rec)
    print("cargs: ", cargs)
    cparams.update({'passwd': get_authentication_token()})


def run():
    while True:
        tenant_code = session_mysql.query(Base.classes.tenant).get(1).company_id
        session_mysql.close()
        print(tenant_code)
        time.sleep(2)


run()
