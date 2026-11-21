# Proyecto 3: Verificación Lógica de Seguridad de un Robot Doméstico

Sistema de verificación formal mediante **Inferencia por Enumeración** y **Resolución por Refutación** en Python.

## Instalación y ejecución

### 1. Linux

1. **Clonar el repositorio y entrar al directorio:**
   ```bash
   git clone [https://github.com/JhosuaS/proyecto-3-robot-seguridad](https://github.com/JhosuaS/proyecto-3-robot-seguridad)
   cd proyecto-3-robot-seguridad
   ```
2. **Crear y activar el entorno virtual:**

```Bash
python3 -m venv venv
source venv/bin/activate
```
3. **Instalar dependencias**:

```Bash
pip install -r requirements.txt
```
4. **Ejecutar el programa**:

```Bash
python3 -m src.main
```
### 2. Windows
1. **Clonar el repositorio y entrar al directorio (en PowerShell o CMD):**

```PowerShell
git clone [https://github.com/JhosuaS/proyecto-3-robot-seguridad](https://github.com/JhosuaS/proyecto-3-robot-seguridad)
cd proyecto-3-robot-seguridad
```

2. **Crear y activar el entorno virtual:**
```PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
(Si PowerShell bloquea la ejecución de scripts, ejecuta primero: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser)
```

```DOS
python -m venv venv
venv\Scripts\activate.bat
```
3. **Instalar dependencias**:

```PowerShell
pip install -r requirements.txt
```

4. **Ejecutar el programa**:

```PowerShell
python -m src.main
```
### 3. Google Colab
1. **Crear un nuevo notebook en Google Colab**.

2. **Clonar el repositorio y ubicarse en la carpeta del proyecto (en una celda de código):**

```Python
!git clone [https://github.com/JhosuaS/proyecto-3-robot-seguridad](https://github.com/JhosuaS/proyecto-3-robot-seguridad)
%cd proyecto-3-robot-seguridad
```
3. **Instalar dependencias**:

```Python
!pip install -r requirements.txt
```
4. **Ejecutar el programa**:

```Python
!python3 -m src.main
```
---

> **Si al ejecutar `python3 -m src.main` o `python -m src.main` aparece `ModuleNotFoundError: No module named 'src'`:** se debe añadir `PYTHONPATH=.` antes del comando en Linux/Colab (`PYTHONPATH=. python3 -m src.main`) o `$env:PYTHONPATH="."` en PowerShell.
