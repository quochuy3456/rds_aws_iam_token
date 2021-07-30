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
# user = "rds_iam_user"
user = "admin"
passwd = "Quochuydo!1994"

ssl_args = {'ssl': {'ca': mysql_attr_ssl_ca}}

mark_aa = 0
client = boto3.client('rds', region_name=region_name)


def get_authentication_token():
    token = client.generate_db_auth_token(DBHostname=host,
                                          Port=port,
                                          DBUsername=user,
                                          Region=region_name)
    iam_token = quote_plus(token)
    print(iam_token)
    return passwd


mysql_connection_url = 'mysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(user, get_authentication_token(), host,
                                                                       str(port), "isoar")
engine = create_engine(mysql_connection_url,
                       connect_args=ssl_args,
                       pool_recycle=6)

session_mysql = Session(engine, autoflush=True)
Base.prepare(engine, reflect=True)


@event.listens_for(engine, "do_connect")
def provide_token(dialect, conn_rec, cargs, cparams):
    print("cparams: ", cparams)
    print("Lỗi ở đây !!")
    cparams['passwd'] = get_authentication_token()
    print("Lỗi ở đây ??")


def run():
    time_count = 0
    while True:
        print("Lỗi ở đây")
        tenant_code = session_mysql.query(Base.classes.tenant).get(1).company_id
        print("Lỗi ở đây này")
        session_mysql.close()
        print(tenant_code)
        time_count += 1
        print(time_count)
        time.sleep(2)


run()
