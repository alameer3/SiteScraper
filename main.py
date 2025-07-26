from app import app
import simple_routes  # noqa: F401

# Register Website Cloner Pro API and Routes
try:
    from api.endpoints.website_cloner_api import cloner_api
    app.register_blueprint(cloner_api)
    
    from routes.website_cloner_routes import register_cloner_routes
    register_cloner_routes(app)
    
    print("✅ Website Cloner Pro integration completed successfully")
except Exception as e:
    print(f"⚠️ Failed to register Website Cloner Pro integration: {e}")