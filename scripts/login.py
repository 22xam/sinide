"""
SINIDE - Script de Login Automatizado
Automatiza el inicio de sesión en SGE Salta (https://sge.salta.gob.ar)
usando Playwright.

Uso:
    python scripts/login.py                 # modo headless (sin ventana)
    python scripts/login.py --headed        # modo con ventana visible
    python scripts/login.py --headed --slow  # modo lento para debug
"""

import os
import sys
import time
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


# Cargar variables de entorno desde .env en la raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH)

# Constantes
DEFAULT_URL = "https://sge.salta.gob.ar/ui3/login"
SESSION_FILE = PROJECT_ROOT / "session.json"
TIMEOUT_MS = 60000  # 60 segundos de timeout (más margen para Altcha PoW)


def parse_args():
    """Parsear argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Login automatizado en SGE Salta"
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Ejecutar con ventana visible del navegador"
    )
    parser.add_argument(
        "--slow",
        action="store_true",
        help="Modo lento (500ms entre acciones) para debug"
    )
    return parser.parse_args()


def get_credentials():
    """Obtener credenciales desde variables de entorno."""
    cuil = os.getenv("SGE_CUIL")
    password = os.getenv("SGE_PASSWORD")
    url = os.getenv("SGE_URL", DEFAULT_URL)

    if not cuil or not password:
        print("❌ Error: No se encontraron las credenciales.")
        print("   Asegurate de crear el archivo .env con:")
        print("   SGE_CUIL=tu_cuil")
        print("   SGE_PASSWORD=tu_contraseña")
        print(f"   Buscando en: {ENV_PATH}")
        sys.exit(1)

    return cuil, password, url


def save_session(cookies, storage_state):
    """Guardar cookies y estado de sesión en archivo JSON."""
    session_data = {
        "cookies": cookies,
        "storage_state": storage_state
    }
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)
    print(f"💾 Sesión guardada en: {SESSION_FILE}")


def login(headed=False, slow=False):
    """
    Ejecutar el proceso de login en SGE Salta.

    Args:
        headed: Si True, muestra la ventana del navegador.
        slow: Si True, agrega delays entre acciones (para debug).
    """
    cuil, password, url = get_credentials()

    print("=" * 50)
    print("🔐 SINIDE - Login Automatizado SGE Salta")
    print("=" * 50)
    print(f"📍 URL: {url}")
    print(f"👤 CUIL: {cuil[:4]}{'*' * (len(cuil) - 6)}{cuil[-2:]}")
    print(f"🖥️  Modo: {'Con ventana' if headed else 'Headless'}")
    print("=" * 50)

    with sync_playwright() as p:
        # Configurar opciones del navegador
        launch_options = {
            "headless": not headed,
        }
        if slow:
            launch_options["slow_mo"] = 500

        # Iniciar navegador
        print("\n🚀 Iniciando navegador...")
        browser = p.chromium.launch(**launch_options)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/133.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        try:
            # 1. Navegar a la página de login
            print("📄 Navegando a la página de login...")
            page.goto(url, wait_until="networkidle", timeout=TIMEOUT_MS)
            print("   ✅ Página cargada")

            # 2. Esperar a que el formulario esté listo
            print("⏳ Esperando formulario de login...")
            page.wait_for_selector("#user", state="visible", timeout=TIMEOUT_MS)
            print("   ✅ Formulario visible")

            # 3. Completar CUIL (simular tipeo humano)
            print("📝 Completando CUIL...")
            cuil_input = page.locator("#user")
            cuil_input.click()
            cuil_input.fill("")  # limpiar campo
            cuil_input.type(cuil, delay=50)  # tipeo con delay humano
            print("   ✅ CUIL ingresado")

            # Pequeña pausa para Angular digest
            time.sleep(0.5)

            # 4. Completar Contraseña (simular tipeo humano)
            print("🔑 Completando contraseña...")
            password_input = page.locator("#password")
            password_input.click()
            password_input.fill("")  # limpiar campo
            password_input.type(password, delay=50)  # tipeo con delay humano
            print("   ✅ Contraseña ingresada")

            # Espera para que Angular procese los campos y Altcha se prepare
            time.sleep(1)

            # 5. Click en botón de login y capturar respuesta de la API
            print("🖱️  Haciendo click en Ingresar...")
            print("⏳ Esperando respuesta del servidor (puede tardar por Altcha PoW)...")

            # Interceptar la respuesta de /api/auth
            with page.expect_response(
                lambda response: "/api/auth" in response.url,
                timeout=TIMEOUT_MS
            ) as response_info:
                login_btn = page.locator("#login-btn")
                login_btn.click()

            # Analizar la respuesta de la API
            api_response = response_info.value
            status_code = api_response.status
            print(f"   📡 API respondió con status: {status_code}")

            if status_code == 200:
                # Login exitoso via API
                try:
                    response_body = api_response.json()
                    print(f"   ✅ Autenticación exitosa via API")

                    # Extraer token si está en la respuesta
                    auth_token = api_response.headers.get("x-auth-token", "")
                    if auth_token:
                        print(f"   🔑 X-Auth-Token: {auth_token[:30]}...")
                except Exception:
                    response_body = {}

                # Esperar a que Angular redirija después del login
                print("⏳ Esperando redirección post-login...")
                try:
                    page.wait_for_url(
                        lambda url: "login" not in url,
                        timeout=TIMEOUT_MS,
                        wait_until="networkidle"
                    )
                except PlaywrightTimeout:
                    # A veces la URL no cambia inmediatamente
                    time.sleep(3)

                current_url = page.url
                print(f"   📍 URL actual: {current_url}")

                # Capturar cookies y estado de sesión
                cookies = context.cookies()
                storage_state = context.storage_state()
                save_session(cookies, storage_state)

                # Mostrar info de la sesión
                print("\n🍪 Cookies capturadas:")
                for cookie in cookies:
                    is_auth = any(
                        kw in cookie["name"].lower()
                        for kw in ["auth", "session", "token", "jwt"]
                    )
                    marker = " 🔐" if is_auth else ""
                    print(f"   - {cookie['name']}{marker}")

                print(f"\n✅ ¡LOGIN EXITOSO!")
                return True

            elif status_code == 401 or status_code == 403:
                print(f"\n❌ Credenciales incorrectas (HTTP {status_code})")
                try:
                    error_body = api_response.json()
                    if isinstance(error_body, dict):
                        msg = error_body.get("message", error_body.get("error", ""))
                        if msg:
                            print(f"   Mensaje: {msg}")
                except Exception:
                    pass
                return False

            else:
                print(f"\n❌ Error del servidor (HTTP {status_code})")
                try:
                    error_body = api_response.text()
                    print(f"   Respuesta: {error_body[:200]}")
                except Exception:
                    pass
                return False

        except PlaywrightTimeout as e:
            print(f"\n❌ Timeout: No se recibió respuesta a tiempo.")
            print("   Posibles causas:")
            print("   - El servidor no responde")
            print("   - Altcha PoW no se pudo resolver")
            print("   - Problemas de conexión")
            # Captura screenshot para debug
            try:
                screenshot_path = PROJECT_ROOT / "error_screenshot.png"
                page.screenshot(path=str(screenshot_path))
                print(f"   📸 Screenshot guardado en: {screenshot_path}")
            except Exception:
                pass
            return False

        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            # Captura screenshot para debug
            try:
                screenshot_path = PROJECT_ROOT / "error_screenshot.png"
                page.screenshot(path=str(screenshot_path))
                print(f"   📸 Screenshot guardado en: {screenshot_path}")
            except Exception:
                pass
            return False

        finally:
            # Cerrar navegador
            if headed and slow:
                print("\n⏸️  Modo debug: El navegador permanece abierto.")
                print("   Presioná Enter para cerrar...")
                input()
            context.close()
            browser.close()
            print("\n🔒 Navegador cerrado.")


def main():
    """Punto de entrada principal."""
    args = parse_args()
    success = login(headed=args.headed, slow=args.slow)

    if success:
        print("\n" + "=" * 50)
        print("✅ Proceso completado exitosamente")
        print(f"📁 Sesión guardada en: {SESSION_FILE}")
        print("=" * 50)
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("❌ El login falló")
        print("   Verificá tus credenciales en el archivo .env")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    main()
