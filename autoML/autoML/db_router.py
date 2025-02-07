class AuthRouter:
    route_app_labels = {'auth', 'contenttypes', 'sessions', 'admin'}

    def db_for_read(self, model, **hints):
        """Redirige les lectures vers le bon schéma"""
        if model._meta.app_label in self.route_app_labels:
            return 'default'  # Utilise auth_schema
        return 'users_data'  # Utilise user_data_schema pour les autres données

    def db_for_write(self, model, **hints):
        """Redirige les écritures vers le bon schéma"""
        if model._meta.app_label in self.route_app_labels:
            return 'default'  # Utilise auth_schema
        return 'users_data'  # Utilise user_data_schema pour les autres données

    def allow_relation(self, obj1, obj2, **hints):
        """Autorise les relations uniquement entre les schémas corrects"""
        if obj1._state.db == obj2._state.db:
            return True
        # Permettre les relations entre tables dans le même schéma
        if {obj1._meta.app_label, obj2._meta.app_label} in [
            {'auth', 'auth'},  # Relations dans le schéma auth
            {'user_data', 'user_data'},  # Relations dans le schéma user_data
        ]:
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Gère les migrations dans les schémas appropriés"""
        if app_label in self.route_app_labels:
            return db == 'default'  # Les applications liées à auth vont dans auth_schema
        return db == 'users_data'  # Les autres applications vont dans user_data_schema
