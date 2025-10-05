import sys
import os

# Add dataPipeline to the Python path to find the db_handler
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
data_pipeline_path = os.path.join(project_root, 'dataPipeline')
sys.path.append(data_pipeline_path)

from db_handler.connect import get_db_connection

# This function can be used as a dependency in FastAPI routes
def get_db():
    db = get_db_connection()
    try:
        yield db
    finally:
        if db:
            db.close()