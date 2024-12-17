from app.db.session import SessionLocal  # Replace with your actual session import
from app.db import models, crud
from IPython import embed

# Initialize the session
db = SessionLocal()

# Provide helpful startup context
print("Interactive Application Console")
print("Available objects:")
print("- db: SQLAlchemy session instance")
print("- models: All your database models")
print("- crud: All your CRUD functions")

# Start the interactive console
if __name__ == "__main__":
    globals().update(locals())
    try:
        # Start interactive console
        embed()
    finally:
        db.close()
        print("Session closed")
