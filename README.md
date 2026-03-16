# 🏫 SGE Salta - SINIDE Automation Scripts

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-1.51.0-2EAD33.svg)
![Status](https://img.shields.io/badge/Status-Development-yellow.svg)

Este repositorio contiene un conjunto de herramientas y scripts automatizados diseñados en **Python**, cuyo objetivo es facilitar e integrar la operatoria en el **Sistema de Gestión Escolar (SGE) de la Provincia de Salta** (SINIDE).

Actualmente, las herramientas permiten interactuar con el sistema de forma desatendida mediante la resolución dinámica de desafíos anti-bot (Altcha Proof-of-Work), captura de sesiones (Tokens JWT y localStorage) e invocaciones a su API interna.

---

## 🌟 Características Actuales

1. **🔒 Login Automatizado Total**
   - El subsistema `scripts/login.py` utiliza [Playwright](https://playwright.dev/python/docs/intro) para instanciar un navegador (visible u oculto).
   - Simula interacciones orgánicas para el ingreso y espera el procesamiento criptográfico del sistema anti-bot Altcha.
   - Genera una persistencia segura de inicio de sesión (`session.json`) con cookies y JWT que evitan tener que iniciar sesión reiteradas veces.

2. **🏢 Selección de Contexto Dinámica**
   - El script secundario `scripts/seleccionar_institucion.py` se conecta nativamente a la API interna `/api/roles/usuario` reutilizando el token JWT.
   - Analiza los roles disponibles del agente que inició sesión y despliega un menú interactivo en la terminal.
   - Permite al usuario seleccionar su contexto laboral actual (por ej., *Director*, *Secretario*, y la Unidad de Servicio - *CUE*) salvando el estado en `contexto_elegido.json`.

3. **🎛️ Menú Centralizado Unificado**
   - Un archivo `main.py` dotado de una interfaz interactiva por terminal (CLI guiada por teclado) que concentra todos los procesos operativos y evita llamadas manuales.

---

## 🛠️ Requisitos Previos

- **Python 3.13** o superior.
- **Git** instalado localmente.
- Una cuenta válida en SGE Salta.

---

## 🚀 Instalación y Configuración

**1. Clonar el repositorio:**
```bash
git clone https://github.com/22xam/sinide.git
cd sinide
```

**2. Crear y activar el entorno virtual:**
```bash
# En Windows
python -m venv venv
.\venv\Scripts\activate

# En Linux / Mac
python3 -m venv venv
source venv/bin/activate
```

**3. Instalar las dependencias y el motor de navegación:**
```bash
pip install -r requirements.txt
playwright install chromium
```

**4. Configurar Credenciales Locales:**
Deberá crear un archivo `.env` tomando como base el archivo modelo provisto.
> ⚠️ **Nota de Seguridad:** NUNCA suba su archivo `.env` o `.json` al repositorio remoto. Estos archivos están ignorados por defecto.

```bash
cp .env.example .env
```
Edite el archivo `.env` e introduzca allí su CUIL y la Contraseña correspondiente.

---

## 📖 Uso General

El proyecto cuenta con un gestor interactivo central. Para ejecutar cualquier operación de este repositorio basta con iniciar el script principal:

```bash
python main.py
```

Al hacerlo, se le presentará el siguiente menú y podrá navegar con las flechas:
1. **Iniciar sesión en SGE**: Carga el navegador y resuelve la conexión y captura de tokens.
2. **Seleccionar Unidad de Servicio**: Elige en qué institución va a trabajar (obtenidas desde la API).

Las sesiones se resguardan de forma segura localmente acelerando enormemente futuros llamados.

---

## ⚖️ Responsabilidad y Licencia
Este proyecto fue creado netamente con fines educativos y de optimización de tiempos administrativos. Los autores no se responsabilizan por bloqueos, penalizaciones derivadas por parte de SGE o el indebido uso de los binarios automatizados. Conserve siempre resguardadas de manera óptima sus claves personales.
