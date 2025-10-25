
import lancedb
import uuid
from datetime import datetime

DB_PATH = "data/measurements"

def init_db():
    """Initializes the database and creates the table if it doesn't exist."""
    db = lancedb.connect(DB_PATH)
    if "measurements" not in db.table_names():
        schema = {
            "id": str,
            "joint": str,
            "exercise": str,
            "timestamp": str,
            "min_angle": float,
            "max_angle": float,
            "data": list,
        }
        db.create_table("measurements", schema=schema)

def save_measurement(joint, exercise, data):
    """Saves a new measurement to the database."""
    db = lancedb.connect(DB_PATH)
    table = db.open_table("measurements")
    
    new_measurement = {
        "id": str(uuid.uuid4()),
        "joint": joint,
        "exercise": exercise,
        "timestamp": datetime.now().isoformat(),
        "min_angle": min(data),
        "max_angle": max(data),
        "data": data,
    }
    table.add([new_measurement])

def get_measurements(page=1, per_page=10, joint=None, exercise=None, date=None):
    """Retrieves measurements with pagination and filtering."""
    db = lancedb.connect(DB_PATH)
    table = db.open_table("measurements")
    
    query = table.search()
    
    if joint:
        query = query.where(f"joint = '{joint}'")
    if exercise:
        query = query.where(f"exercise = '{exercise}'")
    if date:
        query = query.where(f"timestamp LIKE '{date}%'")
        
    total_items = query.to_df().shape[0]
    
    results = query.limit(per_page).offset((page - 1) * per_page).to_df()
    
    return {
        "data": results.to_dict("records"),
        "total": total_items,
        "page": page,
        "per_page": per_page,
    }

def get_measurement_by_id(measurement_id):
    """Retrieves a single measurement by its ID."""
    db = lancedb.connect(DB_PATH)
    table = db.open_table("measurements")
    
    results = table.search().where(f"id = '{measurement_id}'").to_df()
    
    if not results.empty:
        return results.to_dict("records")[0]
    return None
