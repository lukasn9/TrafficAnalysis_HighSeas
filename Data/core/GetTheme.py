import subprocess
import platform

def is_dark_mode_mac():
    try:
        result = subprocess.run(
            ["defaults", "read", "-g", "AppleInterfaceStyle"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.stdout.strip().lower() == "dark"
    except Exception:
        return False

def is_dark_mode_linux():
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        theme = result.stdout.strip().lower()
        return "dark" in theme
    except Exception:
        return False

def is_dark_mode_windows():
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
    except Exception as e:
        print(f"Failed to detect theme on Windows: {e}")
        return False

def is_dark_mode():
    system = platform.system()
    if system == "Windows":
        return is_dark_mode_windows()
    elif system == "Darwin":
        return is_dark_mode_mac()
    elif system == "Linux":
        return is_dark_mode_linux()
    return False