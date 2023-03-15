import os
import json

# from dotenv import load_dotenv
# load_dotenv()

bestbuy_api_key = os.environ.get("API_KEY_BESTBUY")

bestbuy_sql_u = os.environ.get("bestbuy_sql_u")
bestbuy_sql_p = os.environ.get("bestbuy_sql_p")
bestbuy_sql_server_name = os.environ.get("bestbuy_sql_server_name")
bestbuy_sql_db_name = os.environ.get("bestbuy_sql_db_name")
bestbuy_sql_odbc_string = f"Driver={{ODBC Driver 17 for SQL Server}};Server=tcp:{bestbuy_sql_server_name}.database.windows.net,1433;Database={bestbuy_sql_db_name};Uid={bestbuy_sql_u};Pwd={bestbuy_sql_p};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60;"
bestbuy_sql_odbc_string_local = os.environ.get("bestbuy_sql_odbc_string_local")

email_host = os.environ.get("email_host")
email_port = os.environ.get("email_port")
email_sender = os.environ.get("email_sender")
email_user = os.environ.get("email_user")
email_password = os.environ.get("email_password")
email_distribution = [os.environ.get("email_distribution").split(",")[0], os.environ.get("email_distribution").split(",")[1]]

last_update_date = os.environ.get("last_update_date")