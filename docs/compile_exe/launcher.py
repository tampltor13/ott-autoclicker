import os, sys, subprocess, shutil

dir_path = os.path.dirname(os.path.abspath(sys.argv[0]))
script   = os.path.join(dir_path, "ott_autoclicker.py")

def find_python():
    # Check known install locations — avoids Windows Store stub
    candidates = []

    # Common per-user install paths
    local = os.environ.get("LOCALAPPDATA", "")
    for ver in ("313", "312", "311", "310", "39", "38"):
        ver_dot = ver[0] + "." + ver[1:] if len(ver) > 2 else ver[0] + "." + ver[1]
        candidates.append(os.path.join(local, "Programs", "Python", f"Python{ver}", "pythonw.exe"))
        candidates.append(os.path.join(local, "Programs", "Python", f"Python{ver}", "python.exe"))
        candidates.append(os.path.join("C:\\", f"Python{ver}", "pythonw.exe"))
        candidates.append(os.path.join("C:\\", f"Python{ver}", "python.exe"))

    for c in candidates:
        if os.path.exists(c):
            return c

    # Fallback: shutil.which (may hit Store stub, but try anyway)
    found = shutil.which("python") or shutil.which("python3")
    if found:
        # Try pythonw.exe next to it
        pythonw = os.path.join(os.path.dirname(found), "pythonw.exe")
        if os.path.exists(pythonw):
            return pythonw
        return found

    return "pythonw"

python = find_python()
subprocess.Popen([python, script], cwd=dir_path)
