import sys
import subprocess
import questionary
from pathlib import Path

# Paths to the scripts
PROJECT_ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

def run_script(script_name, args=None):
    """Ejecuta un script secundario usando el mismo intérprete de Python."""
    if args is None:
        args = []
    
    script_path = SCRIPTS_DIR / script_name
    cmd = [sys.executable, str(script_path)] + args
    
    try:
        # Ejecutar el proceso y esperar a que finalice
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ El script {script_name} terminó con un error (Código: {e.returncode})")
    except KeyboardInterrupt:
        print(f"\n❌ Ejecución cancelada por el usuario.")

def main():
    while True:
        print("\n" + "="*55)
        print("🔰 MENÚ PRINCIPAL - SGE SALTA AUTOMATIZACIÓN 🔰")
        print("="*55)
        
        try:
            opcion = questionary.select(
                "Seleccioná la tarea que deseas realizar:",
                choices=[
                    questionary.Choice("🔐 1. Iniciar sesión en SGE (Login y captura de sesión)", "login"),
                    questionary.Choice("🏫 2. Seleccionar Unidad de Servicio y Rol (Contexto)", "institucion"),
                    questionary.Separator("---"),
                    questionary.Choice("👋 Salir", "salir")
                ],
                use_indicator=True,
                instruction="(Usá las flechas ⬆⬇ para moverte, Enter para seleccionar)"
            ).ask()
        except KeyboardInterrupt:
            print("\n¡Hasta luego! 👋")
            break
        
        # Opcion cancelada con Ctrl+C o la seleccionada es Salir 
        if not opcion or opcion == "salir":
            print("\n¡Hasta luego! 👋")
            break
            
        elif opcion == "login":
            modo = questionary.select(
                "¿Cómo querés ejecutar el inicio de sesión?",
                choices=[
                    questionary.Choice("👁️  Visible (Abre y muestra el proceso del navegador)", "visible"),
                    questionary.Choice("👻 Oculto (Proceso rápido en segundo plano)", "oculto")
                ]
            ).ask()
            
            args = []
            if modo == "visible":
                args.extend(["--headed"])
            
            print("\n🚀 Ejecutando Login...\n")
            run_script("login.py", args)
            
        elif opcion == "institucion":
            print("\n🏫 Buscando listado de instituciones...\n")
            run_script("seleccionar_institucion.py")
            
        # Pausa antes de limpiar y volver al menú
        input("\nPresioná Enter para continuar al menú principal...")
        
        # Limpiar la consola (opcional)
        print("\033[H\033[J", end="") # Código ANSI para limpiar la pantalla en terminales modernas

if __name__ == '__main__':
    # Habilitar soporte de colores nativo de win10+
    import os
    if os.name == 'nt':
        os.system('color')
    main()
