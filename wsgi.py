from app import app  # Adjust this based on where your Flask app instance is defined

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001, debug=True)
