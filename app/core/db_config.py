import os
from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin, SQLAlchemyAsyncConfig

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://neondb_owner:npg_zWwlKLbHC7o1@ep-polished-wave-aq8tm0sf-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)
db_config = SQLAlchemyAsyncConfig(
    connection_string= DATABASE_URL
)

db_plugin = SQLAlchemyPlugin(config=db_config)

