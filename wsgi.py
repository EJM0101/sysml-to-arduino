from app import create_app

application = create_app()  # Note: 'application' est requis par Render

if __name__ == "__main__":
    application.run()