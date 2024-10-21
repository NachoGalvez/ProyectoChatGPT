import datetime
from django.conf import settings
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin

class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            # No hacer nada si el usuario no está autenticado
            return

        # Obtén el tiempo límite de inactividad desde settings.py
        max_inactive_time = getattr(settings, 'SESSION_COOKIE_AGE', 1800)
        
        # Obtén la última actividad del usuario desde la sesión
        last_activity = request.session.get('last_activity')

        if last_activity:
            now = datetime.datetime.now()
            last_activity_time = datetime.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S.%f')
            # Si el tiempo de inactividad excede el límite, cerrar la sesión
            if (now - last_activity_time).total_seconds() > max_inactive_time:
                logout(request)
                return

        # Actualizar el timestamp de la última actividad
        request.session['last_activity'] = str(datetime.datetime.now())