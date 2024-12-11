from app.db.session import SessionLocal  # Replace with your actual session import
from app.db import models  # Import your SQLAlchemy models
from IPython import embed

# Initialize the session
session = SessionLocal()

# Provide helpful startup context
print("Interactive Application Console")
print("Available objects:")
print("- session: SQLAlchemy session instance")
print("- Models: All your database models")

# Start the interactive console
if __name__ == "__main__":
    globals().update(locals())
    try:
        # Start interactive console
        embed()
    finally:
        session.close()
        print("Session closed")
