from app import app

# Import routes after app is created
try:
    import routes
    print("✅ Routes loaded successfully")
except ImportError as e:
    print(f"❌ Error loading routes: {e}")