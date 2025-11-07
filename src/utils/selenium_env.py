import os
import shutil
import subprocess
import sys
import platform

try:
    import winreg  # Windows registry access
except Exception:
    winreg = None


def _read_registry_chrome_version():
    """Lee la versión de Chrome desde el registro de Windows sin abrir la UI.
    Devuelve la versión (por ejemplo '142.0.7444.61') o None si no se encuentra.
    """
    if platform.system() != "Windows" or winreg is None:
        return None
    # Intentar en usuario actual
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon", 0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(key, "version")
        winreg.CloseKey(key)
        if val:
            return str(val)
    except Exception:
        pass
    # Intentar en máquina (64-bit)
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Google\Chrome\BLBeacon", 0, winreg.KEY_READ | getattr(winreg, "KEY_WOW64_64KEY", 0))
        val, _ = winreg.QueryValueEx(key, "version")
        winreg.CloseKey(key)
        if val:
            return str(val)
    except Exception:
        pass
    # Intentar en máquina (32-bit / Wow6432Node)
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Google\Chrome\BLBeacon", 0, winreg.KEY_READ | getattr(winreg, "KEY_WOW64_32KEY", 0))
        val, _ = winreg.QueryValueEx(key, "version")
        winreg.CloseKey(key)
        if val:
            return str(val)
    except Exception:
        pass
    return None


def _get_chrome_version():
    """Obtiene la versión de Chrome sin abrir la UI si es posible.
    Prioriza lectura del registro en Windows y cae a '--version' solo si es necesario.
    """
    # 1) Intentar leer del registro en Windows
    reg_ver = _read_registry_chrome_version()
    if reg_ver:
        return reg_ver

    # 2) Último recurso: ejecutar chrome --version
    exe = os.environ.get("CHROME_EXECUTABLE")
    candidates = []
    if exe:
        candidates.append(exe)
    # Common install path
    candidates.append(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    # Try PATH shim
    candidates.append(shutil.which("chrome") or shutil.which("chrome.exe"))

    for path in candidates:
        if not path:
            continue
        try:
            out = subprocess.check_output([path, "--version"], stderr=subprocess.STDOUT, text=True)
            parts = out.strip().split()
            ver = next((p for p in parts if p and p[0].isdigit()), None)
            if ver:
                return ver
        except Exception:
            continue
    return None


def _get_chromedriver_version():
    """Get chromedriver version if a chromedriver exists in PATH."""
    path = shutil.which("chromedriver")
    if not path:
        return None, None
    try:
        out = subprocess.check_output([path, "--version"], stderr=subprocess.STDOUT, text=True)
        # e.g. 'ChromeDriver 141.0.7390.123 (... )'
        parts = out.strip().split()
        ver = next((p for p in parts if p[0].isdigit()), None)
        return ver, path
    except Exception:
        return None, path


def preflight_check():
    """Advertir si el chromedriver en PATH no coincide con Chrome.

    - Si TELELINKER_NO_PREFLIGHT está activo, la comprobación se omite.
    - En Windows se intenta leer la versión de Chrome del registro para evitar abrir la UI.
    - Si hay chromedriver en PATH incompatible, se muestra advertencia.
    """
    # Siempre realizar la comprobación; sin bypass por variable de entorno

    cd_ver, cd_path = _get_chromedriver_version()
    if not cd_path:
        return  # no chromedriver in PATH -> fine

    chrome_ver = _get_chrome_version()
    if not chrome_ver or not cd_ver:
        # Cannot compare versions; just warn about PATH chromedriver presence
        print(f"⚠️ Se detectó chromedriver en PATH: {cd_path}. Si ocurre un error de compatibilidad, desinstala chromedriver (scoop uninstall chromedriver) para usar Selenium Manager.")
        return

    # Compare major family (first number)
    try:
        chrome_major = chrome_ver.split(".")[0]
        cd_major = cd_ver.split(".")[0]
        if chrome_major != cd_major:
            print(
                "⚠️ Incompatibilidad detectada: Chrome "
                f"{chrome_ver} vs ChromeDriver {cd_ver} en {cd_path}. "
                "Recomendado: 'scoop uninstall chromedriver' para permitir que Selenium Manager gestione el driver compatible."
            )
    except Exception:
        # Best-effort warning
        print(f"⚠️ Verifica compatibilidad: Chrome {chrome_ver} vs ChromeDriver {cd_ver} en {cd_path}.")