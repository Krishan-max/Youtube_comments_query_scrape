from app import app  # Adjust this based on where your Flask app instance is defined

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Default to 8000 if not set
    app.run(host='0.0.0.0', port=port)
