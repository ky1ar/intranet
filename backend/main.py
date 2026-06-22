import logging

from application import app, socketio

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    socketio.run(app, host=app.config["API_HOST"], port=app.config["API_PORT"])
