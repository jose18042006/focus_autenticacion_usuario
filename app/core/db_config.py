import os
from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin, SQLAlchemyAsyncConfig

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
)
db_config = SQLAlchemyAsyncConfig(
    connection_string= DATABASE_URL
)

db_plugin = SQLAlchemyPlugin(config=db_config)

