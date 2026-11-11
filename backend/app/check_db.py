
from sqlalchemy import text
from app.core.database import engine


try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version()"))

        print("\nHER AI DATABASE CONNECTED!")
        print(result.scalar())

except Exception as error:
    print("\nDATABASE CONNECTION FAILED!")
    print(error)
