import requests
import json
import time

API_URL = "http://localhost:8000"

print("Iniciando inyección de datos de prueba realista (Seed)...")
time.sleep(2) # Dar tiempo por si el server recién levanta

# 1. Crear Usuarios
usuarios_data = [
    {"nombre": "Empresa Constructora 'El Buen Cimiento'", "rol": "MAESTRO"},
    {"nombre": "Juan Pérez (Propietario)", "rol": "CLIENTE"},
    {"nombre": "Ingenieros & Asociados (Mecánica)", "rol": "MAESTRO"},
    {"nombre": "María Gómez (Arquitecta Inversora)", "rol": "CLIENTE"}
]

usuarios = []
print("\n--- Creando Usuarios ---")
for data in usuarios_data:
    res = requests.post(f"{API_URL}/usuarios/", json=data)
    if res.status_code == 200:
        usuarios.append(res.json())
        print(f"✅ Creado: {data['nombre']} ({data['rol']})")
    else:
        print(f"❌ Error al crear: {data['nombre']}")

maestro_1 = usuarios[0]['id']
cliente_1 = usuarios[1]['id']
maestro_2 = usuarios[2]['id']
cliente_2 = usuarios[3]['id']

# 2. Agregar Saldo a los Clientes
print("\n--- Fondeando Billeteras Virtuales de Clientes ---")
requests.post(f"{API_URL}/usuarios/{cliente_1}/agregar_saldo?monto=150000")
print(f"💸 Agregados $150,000 USD a la billetera de Juan Pérez")

requests.post(f"{API_URL}/usuarios/{cliente_2}/agregar_saldo?monto=85000")
print(f"💸 Agregados $85,000 USD a la billetera de María Gómez")


# 3. Crear Contratos/Proyectos
print("\n--- Redactando Contratos Inteligentes ---")
contratos_data = [
    {
        "titulo": "Construcción Casa de Campo (Fase Obra Gris)",
        "descripcion": "Levantamiento de muros, techado y obra negra en parcela 14.",
        "cliente_id": cliente_1,
        "maestro_id": maestro_1
    },
    {
        "titulo": "Instalación Eléctrica Industrial",
        "descripcion": "Cableado estructurado y tableros para nuevo galpón comercial.",
        "cliente_id": cliente_2,
        "maestro_id": maestro_2
    }
]

contratos = []
for data in contratos_data:
    res = requests.post(f"{API_URL}/contratos/", json=data)
    if res.status_code == 200:
        contratos.append(res.json())
        print(f"✅ Contrato Redactado: '{data['titulo']}'")

contrato_casa = contratos[0]['id']
contrato_electrico = contratos[1]['id']

# 4. Crear Hitos
print("\n--- Dividiendo en Hitos de Pago ---")

hitos_casa = [
    {"descripcion": "Excavación y Cimientos", "monto_asignado": 25000},
    {"descripcion": "Levantamiento de paredes (Planta Baja)", "monto_asignado": 35000},
    {"descripcion": "Instalación de techo y losa", "monto_asignado": 40000}
]

hitos_electricos = [
    {"descripcion": "Instalación de bandejas portacables y tuberías", "monto_asignado": 15000},
    {"descripcion": "Armado de tablero principal", "monto_asignado": 20000}
]

for hito in hitos_casa:
    requests.post(f"{API_URL}/contratos/{contrato_casa}/hitos/", json=hito)
print("✅ Hitos añadidos a la Casa de Campo")

for hito in hitos_electricos:
    requests.post(f"{API_URL}/contratos/{contrato_electrico}/hitos/", json=hito)
print("✅ Hitos añadidos a la Instalación Eléctrica")

# 5. Fondear el primer proyecto automáticamente para demostrar estado avanzado
print("\n--- Simulando Fondeo del Contrato 1 por parte del Cliente ---")
res = requests.post(f"{API_URL}/contratos/{contrato_casa}/fondear")
if res.status_code == 200:
    print("🔒 $100,000 Bloqueados exitosamente en la bóveda Escrow de la Casa de Campo")

print("\n🚀 ¡BASE DE DATOS POBLADA EXITOSAMENTE! 🚀")
print("Puedes ingresar al Dashboard y hacer login con cualquiera de los usuarios.")
