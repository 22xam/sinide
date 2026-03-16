"""
SINIDE - Selector de Institución
Carga la sesión iniciada previamente, extrae las instituciones disponibles
y muestra un menú interactivo en consola para elegir con cuál trabajar.

Uso:
    python scripts/seleccionar_institucion.py
"""

import os
import sys
import json
import requests
import questionary
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SESSION_FILE = PROJECT_ROOT / "session.json"
CONTEXT_FILE = PROJECT_ROOT / "contexto_elegido.json"


def check_session():
    """Verifica si existe una sesión válida guardada y extrae el token."""
    if not SESSION_FILE.exists():
        print("❌ Error: No se encontró session.json.")
        print("   Primero debés ejecutar el login: python scripts/login.py")
        sys.exit(1)
        
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            session_data = json.load(f)
            
        jwt_token = None
        
        # Buscar en localStorage
        if "storage_state" in session_data and "origins" in session_data["storage_state"]:
            for origin in session_data["storage_state"]["origins"]:
                if "sge.salta.gob.ar" in origin.get("origin", ""):
                    for item in origin.get("localStorage", []):
                        if item.get("name") == "jwt" or item.get("name") == "token":
                            jwt_token = item.get("value", "").strip('"')
                            break
                            
        # Buscar en cookies
        if not jwt_token and "cookies" in session_data:
            for cookie in session_data["cookies"]:
                if cookie.get("name") == "jwt" or cookie.get("name") == "token" or cookie.get("name") == "X-Auth-Token":
                    jwt_token = cookie.get("value")
                    break
                    
        return jwt_token
        
    except Exception as e:
        print(f"❌ Error al leer la sesión: {e}")
        sys.exit(1)


def fetch_institutions(token):
    """Obtiene las instituciones (Unidades de Servicio) disponibles desde la API."""
    url = "https://sge.salta.gob.ar/api/roles/usuario"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "X-Auth-Token": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401 or response.status_code == 403:
            print(f"❌ La sesión ha expirado (HTTP {response.status_code}).")
            print("   Por favor ejecuta nuevamemte: python scripts/login.py")
            sys.exit(1)
        else:
            print(f"❌ Error de la API al obtener instituciones: {response.status_code}")
            print(f"   Detalle: {response.text[:200]}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        sys.exit(1)


def main():
    print("=" * 60)
    print("🏫 SINIDE - Selector de Institución (Unidad de Servicio)")
    print("=" * 60)
    print("🔄 Verificando sesión...")
    
    token = check_session()
    
    if not token:
        print("❌ Error: No se pudo extraer el token de autenticación de session.json.")
        print("   Por favor vuelve a iniciar sesión con: python scripts/login.py")
        sys.exit(1)
        
    print("🔗 Conectando a la API de SGE Salta...")
    response_data = fetch_institutions(token)
    
    elements = response_data.get("elements", [])
    if not elements:
        print("\n❌ No se encontraron roles o instituciones asignadas a este usuario.")
        sys.exit(1)

    print(f"\n✅ Se encontraron {len(elements)} instituciones/roles asociadas a tu cuenta")
    
    # Preparamos las opciones para el menú de Questionary
    choices = []
    
    for i, acceso in enumerate(elements):
        us_node = acceso.get("unidadServicio", {})
        
        inst_name = us_node.get("nombre", "Institución Desconocida")
        cue = us_node.get("cueanexo", "")
        rol_name = acceso.get("nombre", "Acceso")
        
        display_text = f"{inst_name}"
        details_arr = []
        if cue:
            details_arr.append(f"CUE: {cue}")
        if rol_name:
            details_arr.append(f"Rol: {rol_name}")
            
        if details_arr:
            display_text += f"\n   ↳ {' | '.join(details_arr)}"
            
        # Formatear el value que se guardará en contexto
        context_data = {
            "institucion_nombre": inst_name,
            "unidad_servicio_id": us_node.get("id"),
            "cue": cue,
            "rol_nombre": rol_name,
            "rol_id": acceso.get("id"),
            "jurisdiccion_id": acceso.get("jurisdiccion", {}).get("id"),
            "token": token,
            "raw_data": acceso
        }
            
        choices.append(questionary.Choice(title=display_text, value=context_data))

    if not choices:
        print("\n❌ No hay instituciones disponibles para seleccionar.")
        sys.exit(1)
        
    # Mostramos el menú interactivo
    selected_context = questionary.select(
        "Seleccione la institución y rol con el que desea trabajar:",
        choices=choices,
        use_indicator=True,
        instruction="(Usá las flechas ⬆⬇ para moverte, Enter para seleccionar)"
    ).ask()

    if selected_context:
        print("\n" + "=" * 60)
        print(f"👉 Institución seleccionada: {selected_context['institucion_nombre']}")
        print(f"👉 Rol activo: {selected_context['rol_nombre']}")
        print("=" * 60)
        
        # Guardamos el contexto elegido
        with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
            json.dump(selected_context, f, ensure_ascii=False, indent=2)
            
        print(f"💾 Contexto de trabajo guardado en: {CONTEXT_FILE}")
        print("Ya estás listo para ejecutar las automatizaciones principales.")
    else:
        print("\n❌ Selección cancelada.")

if __name__ == "__main__":
    main()
