class AuthRouter:
    route_app_labels = {'auth', 'contenttypes', 'sessions', 'admin'}

    def db_for_read(self, model, **hints):
        """Redirige les lectures vers le bon schéma"""
        if model._meta.app_label in self.route_app_labels:
            return 'default'  # Utilise auth_schema
        return 'user_data'  # Utilise user_data_schema pour les autres données

    def db_for_write(self, model, **hints):
        """Redirige les écritures vers le bon schéma"""
        if model._meta.app_label in self.route_app_labels:
            return 'default'  # Utilise auth_schema
        return 'user_data'  # Utilise user_data_schema pour les autres données

    def allow_relation(self, obj1, obj2, **hints):
        """Autorise les relations uniquement entre les schémas corrects"""
        # Vérifie si les deux objets sont dans la même base de données (schéma)
        if obj1._state.db == obj2._state.db:
            return True

        if {'auth', 'main'}.issubset({obj1._meta.app_label, obj2._meta.app_label}):
            return True

        if {'user_data', 'main'}.issubset({obj1._meta.app_label, obj2._meta.app_label}):
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Gère les migrations dans les schémas appropriés"""
        if app_label in self.route_app_labels:
            return db == 'default'  # Les applications liées à auth vont dans auth_schema
        return db == 'user_data'  # Les autres applications vont dans user_data_schema
