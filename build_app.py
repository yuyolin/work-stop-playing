# -*- coding: utf-8 -*-
import os
import sys
import shutil
import subprocess
from pathlib import Path

APP_NAME = "工作！！别他妈玩了！"
ROOT = Path(__file__).resolve().parent
APP_FILE = ROOT / "app.pyw"
ICON_ICO = ROOT / "icon.ico"
ICON_PNG = ROOT / "icon.png"


def run(cmd):
    print()
    print(">", " ".join(str(x) for x in cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def desktop_path():
    """Get the real Windows Desktop path, including redirected/OneDrive desktops."""
    if os.name == "nt":
        try:
            import ctypes

            CSIDL_DESKTOPDIRECTORY = 0x0010
            SHGFP_TYPE_CURRENT = 0
            buf = ctypes.create_unicode_buffer(260)
            result = ctypes.windll.shell32.SHGetFolderPathW(
                None,
                CSIDL_DESKTOPDIRECTORY,
                None,
                SHGFP_TYPE_CURRENT,
                buf,
            )
            if result == 0 and buf.value:
                return Path(buf.value)
        except Exception:
            pass

    return Path.home() / "Desktop"


def main():
    print("=" * 58)
    print("Work Timer EXE Builder")
    print("=" * 58)

    if os.name != "nt":
        print("[ERROR] This builder must be run on Windows.")
        return 1

    print("[1/5] Checking Python...")
    print(sys.version)

    print("[2/5] Installing/checking PyInstaller...")
    run([sys.executable, "-m", "pip", "install", "pyinstaller"])

    print("[3/5] Cleaning old build files...")
    for folder in [ROOT / "build", ROOT / "dist"]:
        if folder.exists():
            shutil.rmtree(folder, ignore_errors=True)

    spec = ROOT / f"{APP_NAME}.spec"
    if spec.exists():
        try:
            spec.unlink()
        except Exception:
            pass

    print("[4/5] Building EXE with your icon...")
    sep = ";" if os.name == "nt" else ":"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        f"--name={APP_NAME}",
        f"--icon={ICON_ICO}",
        f"--add-data={ICON_PNG}{sep}.",
        f"--add-data={ICON_ICO}{sep}.",
        str(APP_FILE),
    ]
    run(cmd)

    exe = ROOT / "dist" / f"{APP_NAME}.exe"
    if not exe.exists():
        print("[ERROR] PyInstaller finished but EXE was not found:")
        print(exe)
        return 1

    print("[5/5] Copying EXE to Desktop...")
    desktop = desktop_path()
    desktop.mkdir(parents=True, exist_ok=True)
    target = desktop / exe.name
    shutil.copy2(exe, target)

    try:
        subprocess.run(
            ["ie4uinit.exe", "-show"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass

    print()
    print("=" * 58)
    print("SUCCESS")
    print("=" * 58)
    print("Desktop EXE:")
    print(target)
    print()
    print("Use the .exe on your Desktop.")
    print("Do not use the old .pyw file as the final app.")

    try:
        subprocess.Popen(["explorer.exe", str(desktop)])
    except Exception:
        pass

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 58)
        print("BUILD FAILED")
        print("=" * 58)
        print("Exit code:", e.returncode)
        print("Command:", e.cmd)
        print()
        print("Please send a screenshot of this window.")
        raise SystemExit(e.returncode)
    except Exception as e:
        print()
        print("=" * 58)
        print("BUILD FAILED")
        print("=" * 58)
        print(type(e).__name__ + ":", e)
        print()
        print("Please send a screenshot of this window.")
        raise
