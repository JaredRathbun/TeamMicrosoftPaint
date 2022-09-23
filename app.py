from app import init_app

if __name__ == '__main__':
    app = init_app('dev.cfg')
    app.run('0.0.0.0', debug=app.config['DEBUG'])