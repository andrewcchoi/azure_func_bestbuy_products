import os
import json

# from dotenv import load_dotenv
# load_dotenv()

user = os.getlogin()
bestbuy_api_key = os.environ.get("API_KEY_BESTBUY")
path = os.environ.get("path_dl").format(user)
path_test = os.environ.get("path_test").format(user)
bestbuy_cosmosdb_end_point = os.environ.get("bestbuy_cosmosdb_end_point")
bestbuy_cosmosdb_primary_key = os.environ.get("bestbuy_cosmosdb_primary_key")
bestbuy_cosmosdb_connection_string = f"AccountEndpoint={bestbuy_cosmosdb_end_point};AccountKey={bestbuy_cosmosdb_primary_key};"
bestbuy_sql_p = os.environ.get("bestbuy_sql_p")
bestbuy_sql_u = os.environ.get("bestbuy_sql_u")
bestbuy_sql_server_name = os.environ.get("bestbuy_sql_server_name")
bestbuy_sql_db_name = os.environ.get("bestbuy_sql_db_name")
bestbuy_sql_odbc_string = f"Driver={{ODBC Driver 17 for SQL Server}};Server=tcp:{bestbuy_sql_server_name}.database.windows.net,1433;Database={bestbuy_sql_db_name};Uid={bestbuy_sql_u};Pwd={bestbuy_sql_p};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60;"
bestbuy_sql_odbc_string_local = os.environ.get("bestbuy_sql_odbc_string_local")
bestbuy_sql_schema_path = os.environ.get("bestbuy_sql_schema_path").format(user)

vault = os.environ.get("vault").format(user)
email_host = os.environ.get("email_host")
email_port = os.environ.get("email_port")
email_user = os.environ.get("email_user")
email_sender = os.environ.get("email_sender")
with open(vault) as f:
    secrets = json.loads(f.read())

email_password = secrets["secrets"]["privateemail"][email_user][0]
email_distribution = [os.environ.get("email_distribution").split(",")[0], os.environ.get("email_distribution").split(",")[1]]

last_update_date = os.environ.get("last_update_date")