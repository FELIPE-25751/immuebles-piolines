"""
Script de utilidades para InmueblesApp
Ejecutar con: python manage.py shell < utils.py
"""

from core.models import Usuario, PerfilUsuario
from inmuebles.models import Inmueble, ImagenInmueble
from contratos.models import Contrato
from pagos.models import Pago
from mantenimientos.models import Mantenimiento
from notificaciones.models import Notificacion
from datetime import datetime, timedelta
from decimal import Decimal

def crear_datos_prueba():
    """Crea datos de prueba para demostración"""
    
    print("Creando datos de prueba...")
    
    # Crear propietario
    try:
        propietario = Usuario.objects.create_user(
            username='propietario1',
            email='propietario@test.com',
            password='password123',
            first_name='Juan',
            last_name='Propietario',
            tipo_usuario='propietario',
            cedula='1000000001',
            telefono='3001234567',
            ciudad='Bogotá'
        )
        print(f"✓ Propietario creado: {propietario.username}")
    except:
        propietario = Usuario.objects.get(username='propietario1')
        print(f"- Propietario ya existe: {propietario.username}")
    
    # Crear inquilino
    try:
        inquilino = Usuario.objects.create_user(
            username='inquilino1',
            email='inquilino@test.com',
            password='password123',
            first_name='María',
            last_name='Inquilina',
            tipo_usuario='inquilino',
            cedula='1000000002',
            telefono='3007654321',
            ciudad='Bogotá'
        )
        print(f"✓ Inquilino creado: {inquilino.username}")
    except:
        inquilino = Usuario.objects.get(username='inquilino1')
        print(f"- Inquilino ya existe: {inquilino.username}")
    
    # Crear inmuebles
    inmuebles_data = [
        {
            'titulo': 'Apartamento Centro Histórico',
            'descripcion': 'Hermoso apartamento en el centro de la ciudad, cerca de todo.',
            'categoria': 'apartamento',
            'direccion': 'Calle 10 #15-20',
            'ciudad': 'Bogotá',
            'barrio': 'La Candelaria',
            'area': Decimal('85.50'),
            'habitaciones': 3,
            'banos': 2,
            'parqueaderos': 1,
            'precio_arriendo': Decimal('1500000'),
            'precio_administracion': Decimal('200000'),
            'deposito_seguridad': Decimal('1500000'),
            'amoblado': True,
            'mascotas_permitidas': False,
        },
        {
            'titulo': 'Casa Campestre Norte',
            'descripcion': 'Casa amplia con jardín, perfecta para familias.',
            'categoria': 'casa',
            'direccion': 'Carrera 7 #145-30',
            'ciudad': 'Bogotá',
            'barrio': 'Usaquén',
            'area': Decimal('150.00'),
            'habitaciones': 4,
            'banos': 3,
            'parqueaderos': 2,
            'precio_arriendo': Decimal('2500000'),
            'precio_administracion': Decimal('150000'),
            'deposito_seguridad': Decimal('2500000'),
            'amoblado': False,
            'mascotas_permitidas': True,
        },
        {
            'titulo': 'Apartamento Moderno Chapinero',
            'descripcion': 'Moderno apartamento con excelente vista.',
            'categoria': 'apartamento',
            'direccion': 'Calle 63 #7-20',
            'ciudad': 'Bogotá',
            'barrio': 'Chapinero',
            'area': Decimal('65.00'),
            'habitaciones': 2,
            'banos': 2,
            'parqueaderos': 1,
            'precio_arriendo': Decimal('1800000'),
            'precio_administracion': Decimal('250000'),
            'deposito_seguridad': Decimal('1800000'),
            'amoblado': True,
            'mascotas_permitidas': True,
        }
    ]
    
    for data in inmuebles_data:
        inmueble, created = Inmueble.objects.get_or_create(
            propietario=propietario,
            titulo=data['titulo'],
            defaults=data
        )
        if created:
            print(f"✓ Inmueble creado: {inmueble.titulo}")
            inmueble.save_to_firebase()
        else:
            print(f"- Inmueble ya existe: {inmueble.titulo}")
    
    print("\n✓ Datos de prueba creados exitosamente!")
    print("\nCredenciales de acceso:")
    print("========================")
    print("Propietario:")
    print("  Usuario: propietario1")
    print("  Contraseña: password123")
    print("\nInquilino:")
    print("  Usuario: inquilino1")
    print("  Contraseña: password123")
    print("\nAdmin:")
    print("  Accede a /admin con tu superusuario")


def estadisticas():
    """Muestra estadísticas de la base de datos"""
    print("\n=== ESTADÍSTICAS DE LA BASE DE DATOS ===\n")
    print(f"Usuarios: {Usuario.objects.count()}")
    print(f"  - Propietarios: {Usuario.objects.filter(tipo_usuario='propietario').count()}")
    print(f"  - Inquilinos: {Usuario.objects.filter(tipo_usuario='inquilino').count()}")
    print(f"\nInmuebles: {Inmueble.objects.count()}")
    print(f"  - Disponibles: {Inmueble.objects.filter(estado='disponible').count()}")
    print(f"  - Arrendados: {Inmueble.objects.filter(estado='arrendado').count()}")
    print(f"\nContratos: {Contrato.objects.count()}")
    print(f"  - Activos: {Contrato.objects.filter(estado='activo').count()}")
    print(f"\nPagos: {Pago.objects.count()}")
    print(f"  - Pendientes: {Pago.objects.filter(estado='pendiente').count()}")
    print(f"  - Pagados: {Pago.objects.filter(estado='pagado').count()}")
    print(f"\nMantenimientos: {Mantenimiento.objects.count()}")
    print(f"\nNotificaciones: {Notificacion.objects.count()}")


def limpiar_base_datos():
    """CUIDADO: Elimina todos los datos excepto superusuarios"""
    respuesta = input("¿Estás seguro de que quieres eliminar todos los datos? (si/no): ")
    if respuesta.lower() != 'si':
        print("Operación cancelada")
        return
    
    print("Eliminando datos...")
    Notificacion.objects.all().delete()
    Mantenimiento.objects.all().delete()
    Pago.objects.all().delete()
    Contrato.objects.all().delete()
    ImagenInmueble.objects.all().delete()
    Inmueble.objects.all().delete()
    Usuario.objects.filter(is_superuser=False).delete()
    
    print("✓ Base de datos limpiada (superusuarios preservados)")


# Menú interactivo
if __name__ == "__main__":
    print("\n=== UTILIDADES INMUEBLESAPP ===\n")
    print("1. Crear datos de prueba")
    print("2. Ver estadísticas")
    print("3. Limpiar base de datos")
    print("4. Salir")
    
    opcion = input("\nSelecciona una opción: ")
    
    if opcion == "1":
        crear_datos_prueba()
    elif opcion == "2":
        estadisticas()
    elif opcion == "3":
        limpiar_base_datos()
    else:
        print("Saliendo...")
