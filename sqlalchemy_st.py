import boto3
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import event
from urllib.parse import quote_plus
import time

Base = automap_base()

mysql_attr_ssl_ca = "rds-combined-ca-bundle.pem"
region_name = "ap-northeast-1a"
host = "database-3.cgjasvizzmcb.ap-northeast-1.rds.amazonaws.com"
port = 3306
user = "rds_iam_user"
passwd = "Quochuydo!1994"

ssl_args = {'ssl': {'ca': mysql_attr_ssl_ca}}
client = boto3.client('rds', region_name=region_name)
token = client.generate_db_auth_token(DBHostname=host,
                                      Port=port,
                                      DBUsername=user,
                                      Region=region_name)
iam_token = quote_plus(token)
print("iam_token: ", iam_token)

"""
{
  "Version" : "2012-10-17",
  "Statement" :
  [
    {
      "Effect" : "Allow",
      "Action" : ["rds-db:connect"],
      "Resource" : ["arn:aws:rds-db:ap-northeast-1:521345806971:userdb:db-Z2DELENJR7BZC6X3H76KD6GUYI/rds_iam_user"]
    }
  ]
}

{
   "Version": "2012-10-17",
   "Statement": [
      {
         "Effect": "Allow",
         "Action": [
             "rds-db:connect"
         ],
         "Resource": [
             "arn:aws-cn:rds-db:ap-northeast-1:521345806971:dbuser:db-Z2DELENJR7BZC6X3H76KD6GUYI/rds_iam_user"
         ]
      }
   ]
}
"""


def get_authentication_token():
    return passwd


class Check:
    # mysql_connection_url = 'mysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(user, passwd, host,
    #                                                                        3306, "isoar")
    #
    # engine = create_engine(mysql_connection_url, pool_recycle=10)
    mysql_connection_url = 'mysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(user, iam_token, host,
                                                                           str(port), "isoar")
    engine = create_engine(mysql_connection_url,
                           connect_args=ssl_args,
                           pool_recycle=10)

    session_mysql = Session(engine, autoflush=True)
    # Base.prepare(engine, reflect=True)

    def __init__(self):
        self.sthhere = "here"

    @staticmethod
    @event.listens_for(engine, "do_connect")
    def provide_token(dialect, conn_rec, cargs, cparams):
        print("cparams: ", cparams)
        print("dialect: ", dialect)
        print("conn_rec: ", conn_rec)
        print("cargs: ", cargs)
        cparams['passwd'] = get_authentication_token()

    def run(self):
        while True:
            tenant_code = self.session_mysql.query(Base.classes.tenant).get(1).company_id
            self.session_mysql.close()
            print(tenant_code)
            time.sleep(12)


Check().run()
