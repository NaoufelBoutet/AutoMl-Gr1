from django.apps import AppConfig

class YourAppConfig(AppConfig):
    name = 'main'  # Remplace 'your_app' par le nom de ton app
    def ready(self):
        import main.signals