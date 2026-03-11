from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario, Persona, Rol, UsuarioRol

class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__'
        read_only_fields = ['creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion']

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre']

class UsuarioRolSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)
    
    class Meta:
        model = UsuarioRol
        fields = ['id', 'usuario', 'rol', 'rol_nombre', 'fecha_asignacion']

class UsuarioSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer(read_only=True)
    persona_id = serializers.PrimaryKeyRelatedField(
        queryset=Persona.objects.all(), 
        source='persona',
        write_only=True,
        required=False,
        allow_null=True
    )
    roles = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'password',
            'persona', 'persona_id', 'roles', 'nombre_completo',
            'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }
    
    def get_roles(self, obj):
        usuario_roles = UsuarioRol.objects.filter(usuario=obj).select_related('rol')
        return [{'id': ur.rol.id, 'nombre': ur.rol.nombre} for ur in usuario_roles]
    
    def get_nombre_completo(self, obj):
        if obj.persona:
            return f"{obj.persona.nombres} {obj.persona.apellido_paterno or ''} {obj.persona.apellido_materno or ''}".strip()
        return obj.get_full_name()
    
    def create(self, validated_data):
        # Extraer password
        password = validated_data.pop('password', None)
        
        # Crear usuario usando create_user (hashea la contraseña automáticamente)
        usuario = Usuario.objects.create_user(**validated_data)
        
        # Si hay password, asegurarse de que se establezca
        if password:
            usuario.set_password(password)
            usuario.save()
        
        return usuario
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        # Actualizar otros campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    persona_id = serializers.PrimaryKeyRelatedField(
        queryset=Persona.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'persona_id']
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        persona_id = validated_data.pop('persona_id', None)
        password = validated_data.pop('password')
        
        # Crear usuario
        usuario = Usuario.objects.create_user(**validated_data)
        usuario.set_password(password)
        
        # Asignar persona si existe
        if persona_id:
            usuario.persona = persona_id
            usuario.save()
        else:
            usuario.save()
        
        return usuario

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        print(f"=== INTENTO DE LOGIN ===")
        print(f"Username recibido: '{username}'")
        print(f"Password recibido: '{password}'")
        
        if not username or not password:
            print("Faltan username o password")
            raise serializers.ValidationError("Debe proporcionar username y password")
        
        # Buscar usuario manualmente
        try:
            user_db = Usuario.objects.get(username=username)
            print(f"Usuario encontrado en BD: {user_db.username}")
            print(f"Usuario está activo: {user_db.is_active}")
            print(f"Password hash en BD: {user_db.password}")
            print(f"Verificación manual: {user_db.check_password(password)}")
        except Usuario.DoesNotExist:
            print(f"Usuario '{username}' NO existe en BD")
        
        # Autenticar con Django
        user = authenticate(username=username, password=password)
        print(f"Resultado authenticate(): {user}")
        
        if user:
            if not user.is_active:
                print("Usuario inactivo")
                raise serializers.ValidationError("Usuario inactivo")
            data['user'] = user
        else:
            print("Credenciales inválidas")
            raise serializers.ValidationError("Credenciales inválidas")
        
        return data

class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UsuarioSerializer()