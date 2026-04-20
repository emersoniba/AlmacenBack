from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from .models import LoginAttempt
from django.db import models

class LoginRateLimiter:
    """
    Limitador de intentos de login para prevenir ataques de fuerza bruta
    """
    
    # Configuración por defecto
    MAX_ATTEMPTS = 5  # Máximo de intentos fallidos
    BLOCK_TIME_MINUTES = 15  # Tiempo de bloqueo en minutos
    WINDOW_MINUTES = 15  # Ventana de tiempo para contar intentos
    
    @classmethod
    def get_client_ip(cls, request):
        """Obtener IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @classmethod
    def register_attempt(cls, request, username, success=False):
        """Registrar un intento de login"""
        try:
            LoginAttempt.objects.create(
                username=username,
                ip_address=cls.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                success=success
            )
        except Exception as e:
            print(f"Error registrando intento: {e}")
    
    @classmethod
    def get_failed_attempts(cls, username, ip_address):
        """Obtener número de intentos fallidos recientes"""
        since_time = timezone.now() - timedelta(minutes=cls.WINDOW_MINUTES)
        
        # Contar intentos fallidos por username o IP
        attempts = LoginAttempt.objects.filter(
            success=False,
            attempt_time__gte=since_time
        ).filter(
            # Intentos desde la misma IP O con el mismo username
            models.Q(username=username) | models.Q(ip_address=ip_address)
        )
        
        return attempts.count()
    
    @classmethod
    def is_blocked(cls, username, ip_address):
        """Verificar si el usuario/IP está bloqueado"""
        since_time = timezone.now() - timedelta(minutes=cls.WINDOW_MINUTES)
        
        failed_attempts = LoginAttempt.objects.filter(
            success=False,
            attempt_time__gte=since_time
        ).filter(
            models.Q(username=username) | models.Q(ip_address=ip_address)
        ).count()
        
        print(f"Intentos fallidos para {username}: {failed_attempts}")  # Debug
        
        if failed_attempts >= cls.MAX_ATTEMPTS:
            last_attempt = LoginAttempt.objects.filter(
                success=False,
                attempt_time__gte=since_time
            ).filter(
                models.Q(username=username) | models.Q(ip_address=ip_address)
            ).order_by('-attempt_time').first()
            
            if last_attempt:
                time_since_last = timezone.now() - last_attempt.attempt_time
                if time_since_last.total_seconds() < (cls.BLOCK_TIME_MINUTES * 60):
                    remaining = cls.BLOCK_TIME_MINUTES - (time_since_last.total_seconds() / 60)
                    print(f"Usuario {username} bloqueado. Tiempo restante: {remaining}")  # Debug
                    return True, round(remaining)
        
        return False, 0
    
    @classmethod
    def get_remaining_attempts(cls, username, ip_address):
        """Obtener intentos restantes"""
        failed_attempts = cls.get_failed_attempts(username, ip_address)
        return max(0, cls.MAX_ATTEMPTS - failed_attempts)
    
    @classmethod
    def get_wait_time(cls, username, ip_address):
        """Obtener tiempo de espera restante en minutos"""
        is_blocked, remaining = cls.is_blocked(username, ip_address)
        if is_blocked:
            return remaining
        return 0