from flask import current_app


class StorageManager:

    def get_app(self):
        if current_app:
            return current_app._get_current_object()

        if hasattr(self, 'app'):
            return getattr(self, 'app')

        raise RuntimeError("No application found. Either work inside a view function or push an application context")
