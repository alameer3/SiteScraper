from app import app

# Register routes
try:
    import simple_routes  # noqa: F401
    print("✅ Simple routes imported successfully")
except Exception as e:
    print(f"⚠️ Failed to import simple routes: {e}")

# Register API and Routes if available
try:
    from api.endpoints.website_cloner_api import cloner_api
    app.register_blueprint(cloner_api)
    print("✅ Website Cloner API registered successfully")
except Exception as e:
    print(f"⚠️ Failed to register Website Cloner API: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)