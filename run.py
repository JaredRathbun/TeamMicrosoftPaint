from stemdatadashboard import init_app

if __name__ == '__main__':
    # Starts the main app.
    app = init_app()
    app.run(debug=app.config['DEBUG'])