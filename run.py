import logging

logging.basicConfig(level=logging.INFO)


from my_project import app
if __name__ == "__main__":
    app.run()
