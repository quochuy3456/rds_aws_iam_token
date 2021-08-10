import boto3
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import event
from urllib.parse import quote_plus
import time

Base = automap_base()

########## Config ##################
mysql_attr_ssl_ca = "/var/app/isoar/rds-ca-2019-root.pem"
region_name = "ap-northeast-1"
host = "isoar-dev-ual-db.ctbfofok8p3r.ap-northeast-1.rds.amazonaws.com"
port = 3306
user = "isoarusr"
database_name = "isoar_dev_ntq_db"
####################################


ssl_args = {'ssl': {'ca': mysql_attr_ssl_ca}}
client = boto3.client('rds', region_name=region_name)

# GEN token
def get_authentication_token():
    token = client.generate_db_auth_token(DBHostname=host,
                                          Port=port,
                                          DBUsername=user,
                                          Region=region_name)
    iam_token = quote_plus(token)
    return iam_token


token = get_authentication_token()

mysql_connection_url = 'mysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(user, token, host,
                                                                       str(port), database_name)

# Create engine
engine = create_engine(mysql_connection_url,
                       connect_args=ssl_args,
                       pool_recycle=6)

session_mysql = Session(engine, autoflush=True)
Base.prepare(engine, reflect=True)


# Check and update token before give connection
@event.listens_for(engine, "do_connect")
def provide_token(dialect, conn_rec, cargs, cparams):
    print("cparams: ", cparams)
    cparams['passwd'] = get_authentication_token()


# Run test (get connection
def run():
    while True:
        tenant_code = session_mysql.query(Base.classes.tenants).get(1).tenant_id
        session_mysql.close()
        print(tenant_code)
        time.sleep(2)

run()
