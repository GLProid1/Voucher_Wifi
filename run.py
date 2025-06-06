from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)  # Set debug=True for development, False for production