#\!/usr/bin/env python3
"""OTT AutoClicker – compatible with Python 3.9 / macOS system Tk"""
from __future__ import annotations
import os, sys, platform, time, threading, datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import urllib.request

# ── selenium (optional) ──────────────────────────────────────────────────────
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options as COptions
    from selenium.webdriver.edge.options  import Options as EOptions
    from selenium.webdriver.support.ui    import WebDriverWait
    from selenium.webdriver.support       import expected_conditions as EC
    from selenium.common.exceptions       import (TimeoutException,
                                                   NoSuchElementException,
                                                   WebDriverException)
    SEL = True
except ImportError:
    SEL = False

# ── webdriver-manager (optional fallback) ─────────────────────────────────────
try:
    from selenium.webdriver.chrome.service import Service as CService
    from selenium.webdriver.edge.service   import Service as EService
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    WDM = True
except ImportError:
    WDM = False

IS_MAC  = platform.system() == "Darwin"
VERSION = "1.0.4"

UPDATE_VERSION_URL = "https://raw.githubusercontent.com/tampltor13/ott-autoclicker/main/version.txt"
UPDATE_SCRIPT_URL  = "https://raw.githubusercontent.com/tampltor13/ott-autoclicker/main/ott_autoclicker.py"

PLATFORMS = {
    "Prime Video":     "https://www.primevideo.com",
    "Prime Video USA": "https://www.amazon.com/gp/video/sports",
    "Prime Video IT":  "https://www.primevideo.com",
    "Prime Video BR":  "https://www.primevideo.com",
    "Prime Video UK":  "https://www.amazon.co.uk/",
    "Prime Video DE":  "https://www.amazon.de/",
    "TOD":         "https://www.tod.tv",
    "Disney+":     "https://www.disneyplus.com/home",
    "Netflix":     "https://www.netflix.com",
    "Max":         "https://www.max.com",
    "Apple TV+":   "https://tv.apple.com",
    "Custom URL":  "",
}
# Predefined rules per platform: selector type + click targets (one per line)
PLATFORM_RULES = {
    "Prime Video": {
        "selector":      "XPath",
        "targets":       '//*[@data-automation-id="circular-playbutton" and contains(.,"Watch")]\n//*[@data-testid="play" and contains(.,"Watch")]',
        "refresh_first": True,
        "click_delay":   2000,
    },
    "Prime Video USA": {
        "selector":      "XPath",
        "targets":       '//*[@data-automation-id="circular-playbutton" and contains(.,"Watch")]\n//*[@data-testid="play" and contains(.,"Watch")]',
        "refresh_first": True,
        "click_delay":   2000,
    },
    "Prime Video IT": {
        "selector":      "XPath",
        "targets":       '//*[@data-automation-id="circular-playbutton" and contains(.,"Guarda")]\n//*[@data-testid="play" and contains(.,"Guarda")]',
        "refresh_first": True,
        "click_delay":   2000,
    },
    "Prime Video BR": {
        "selector":      "XPath",
        "targets":       '//*[@data-automation-id="circular-playbutton" and contains(.,"Assista")]\n//*[@data-testid="play" and contains(.,"Assista")]',
        "refresh_first": True,
        "click_delay":   2000,
    },
    "Prime Video UK": {
        "selector":      "XPath",
        "targets":       '//*[@data-automation-id="circular-playbutton" and contains(.,"Watch")]\n//*[@data-testid="play" and contains(.,"Watch")]',
        "refresh_first": True,
        "click_delay":   2000,
    },
    "Prime Video DE": {
        "selector":      "XPath",
        "targets":       '//*[@data-automation-id="circular-playbutton" and contains(.,"Watch")]\n//*[@data-testid="play" and contains(.,"Watch")]',
        "refresh_first": True,
        "click_delay":   2000,
    },
    "Disney+": {
        "selector":      "XPath",
        "targets":       '//*[@data-testid="playback-action-button" and contains(.,"CONTINUE")]',
        "refresh_first": True,
    },
    "TOD": {
        "selector":      "ID",
        "targets":       "watch_live_click",
        "refresh_first": False,
    },
}
SELECTOR_LABELS = ["Class Name", "CSS Selector", "ID", "XPath"]
BY_MAP = {
    "Class Name":   By.CLASS_NAME   if SEL else None,
    "CSS Selector": By.CSS_SELECTOR if SEL else None,
    "ID":           By.ID           if SEL else None,
    "XPath":        By.XPATH        if SEL else None,
}
PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_profiles")
MONO_FONT   = ("Menlo", 11) if IS_MAC else ("Consolas", 11)


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text   = text
        self.win    = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.win = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.text, justify="left",
                 background="#2b2b2b", foreground="#ffffff",
                 relief="flat", borderwidth=0,
                 font=("TkDefaultFont", 11), padx=8, pady=6,
                 wraplength=280).pack()

    def _hide(self, _event=None):
        if self.win:
            self.win.destroy()
            self.win = None


class App:
    def __init__(self, root):
        self.root    = root
        self.driver  = None
        self.running = False
        self.thread  = None
        root.title(f"OTT AutoClicker  v{VERSION}")
        root.geometry("660x640")
        root.resizable(True, True)
        os.makedirs(PROFILE_DIR, exist_ok=True)
        self._build()
        threading.Thread(target=self._check_update, daemon=True).start()

    # ────────────────────────────────────────────────────────────────────────
    def _build(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=6, pady=6)

        t1 = ttk.Frame(nb); nb.add(t1, text="  Setup  ")
        t2 = ttk.Frame(nb); nb.add(t2, text="  Monitor  ")
        self._setup_tab(t1)
        self._monitor_tab(t2)

        status_bar = ttk.Frame(self.root, relief="sunken")
        status_bar.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_bar, textvariable=self.status_var).pack(
            anchor="w", padx=6, pady=2)

    # ── SETUP TAB ────────────────────────────────────────────────────────────
    def _setup_tab(self, parent):
        p = ttk.Frame(parent, padding=12)
        p.pack(fill="both", expand=True)

        r = 0
        # browser
        ttk.Label(p, text="Browser:").grid(row=r, column=0, sticky="w", pady=3)
        self.browser_var = tk.StringVar(value="Chrome")
        ttk.Combobox(p, textvariable=self.browser_var,
                     values=["Chrome","Edge"], state="readonly", width=10
                     ).grid(row=r, column=1, sticky="w", padx=8); r += 1

        # platform
        ttk.Label(p, text="Platform:").grid(row=r, column=0, sticky="w", pady=3)
        self.platform_var = tk.StringVar(value="")
        cb = ttk.Combobox(p, textvariable=self.platform_var,
                          values=list(PLATFORMS.keys()), state="readonly", width=16)
        cb.grid(row=r, column=1, sticky="w", padx=8)
        cb.bind("<<ComboboxSelected>>", self._platform_changed); r += 1

        # url
        ttk.Label(p, text="URL:").grid(row=r, column=0, sticky="w", pady=3)
        self.url_var = tk.StringVar(value="")
        ttk.Entry(p, textvariable=self.url_var, width=50).grid(
            row=r, column=1, columnspan=3, sticky="ew", padx=8); r += 1

        # buttons
        bf = ttk.Frame(p); bf.grid(row=r, column=0, columnspan=4,
                                    sticky="w", pady=(4,8)); r += 1
        ttk.Button(bf, text="Open Browser",  command=self.open_browser ).pack(side="left", padx=(0,4))
        ttk.Button(bf, text="Navigate →",    command=self.navigate     ).pack(side="left", padx=(0,4))
        ttk.Button(bf, text="Close Browser", command=self.close_browser).pack(side="left")

        ttk.Separator(p, orient="horizontal").grid(
            row=r, column=0, columnspan=4, sticky="ew", pady=4); r += 1

        # click targets
        ttk.Label(p, text="Click targets (one per line):").grid(
            row=r, column=0, columnspan=4, sticky="w", pady=(6,2)); r += 1
        self.targets_text = scrolledtext.ScrolledText(p, width=44, height=5,
                                                       font=MONO_FONT)
        self.targets_text.grid(row=r, column=0, columnspan=4, sticky="ew")
        self.targets_text.insert("1.0", "fbl-play-btn\n"); r += 1

        # selector type
        ttk.Label(p, text="Selector:").grid(row=r, column=0, sticky="w", pady=3)
        self.sel_var = tk.StringVar(value="Class Name")
        sf = ttk.Frame(p); sf.grid(row=r, column=1, columnspan=3, sticky="w", padx=8)
        for s in SELECTOR_LABELS:
            ttk.Radiobutton(sf, text=s, variable=self.sel_var,
                            value=s).pack(side="left", padx=2); r += 1

        # delays
        ttk.Label(p, text="Click delay (ms):").grid(row=r, column=0, sticky="w", pady=3)
        self.delay_var = tk.IntVar(value=1000)
        f_delay = ttk.Frame(p); f_delay.grid(row=r, column=1, sticky="w", padx=8)
        tk.Spinbox(f_delay, from_=0, to=30000, textvariable=self.delay_var,
                   width=8, bg="#3c3c3c", fg="#ffffff",
                   buttonbackground="#555555", insertbackground="#ffffff").pack(side="left")
        i1 = ttk.Label(f_delay, text=" ⓘ", foreground="#888888", cursor="hand2")
        i1.pack(side="left")
        Tooltip(i1, "Pause between clicks when you have multiple targets.\n"
                    "e.g. 800ms = waits 0.8s between each click.")

        ttk.Label(p, text="Page-load wait (s):").grid(row=r, column=2, sticky="w")
        self.load_var = tk.IntVar(value=5)
        f_load = ttk.Frame(p); f_load.grid(row=r, column=3, sticky="w")
        tk.Spinbox(f_load, from_=0, to=60, textvariable=self.load_var,
                   width=6, bg="#3c3c3c", fg="#ffffff",
                   buttonbackground="#555555", insertbackground="#ffffff").pack(side="left")
        i2 = ttk.Label(f_load, text=" ⓘ", foreground="#888888", cursor="hand2")
        i2.pack(side="left")
        Tooltip(i2, "Seconds to wait after refresh before looking for the element.\n"
                    "Gives the page time to load.\n"
                    "Increase if your internet is slow."); r += 1

        # refresh
        ttk.Label(p, text="Refresh every (s):").grid(row=r, column=0, sticky="w", pady=3)
        self.refresh_var = tk.IntVar(value=60)
        f_refresh = ttk.Frame(p); f_refresh.grid(row=r, column=1, sticky="w", padx=8)
        tk.Spinbox(f_refresh, from_=0, to=86400, textvariable=self.refresh_var,
                   width=8, bg="#3c3c3c", fg="#ffffff",
                   buttonbackground="#555555", insertbackground="#ffffff").pack(side="left")
        i3 = ttk.Label(f_refresh, text=" ⓘ", foreground="#888888", cursor="hand2")
        i3.pack(side="left")
        Tooltip(i3, "How many seconds to wait between page refreshes.\n"
                    "0 = do not refresh automatically.")
        self.refresh_first_var = tk.BooleanVar(value=False)
        f_rf = ttk.Frame(p); f_rf.grid(row=r, column=2, columnspan=2, sticky="w")
        ttk.Checkbutton(f_rf, text="Refresh BEFORE clicking",
                        variable=self.refresh_first_var).pack(side="left")
        i4 = ttk.Label(f_rf, text=" ⓘ", foreground="#888888", cursor="hand2")
        i4.pack(side="left")
        Tooltip(i4, "If checked: refreshes the page first, then looks for the button.\n"
                    "If unchecked: looks for the button first, refreshes at end of cycle."); r += 1

        ttk.Separator(p, orient="horizontal").grid(
            row=r, column=0, columnspan=4, sticky="ew", pady=6); r += 1

        ttk.Button(p, text="Test — highlight targets in browser",
                   command=self.test_targets).grid(
            row=r, column=0, columnspan=4, sticky="w"); r += 1

        p.columnconfigure(1, weight=1)
        p.columnconfigure(3, weight=1)

    # ── MONITOR TAB ──────────────────────────────────────────────────────────
    def _monitor_tab(self, parent):
        p = ttk.Frame(parent, padding=12)
        p.pack(fill="both", expand=True)

        now = datetime.datetime.now()
        r = 0

        ttk.Label(p, text="Start date:").grid(row=r, column=0, sticky="w", pady=3)
        self.start_date = tk.StringVar(value=now.strftime("%Y-%m-%d"))
        ttk.Entry(p, textvariable=self.start_date, width=11).grid(
            row=r, column=1, sticky="w", padx=8)
        ttk.Label(p, text="Time (HH:MM):").grid(row=r, column=2, sticky="w")
        self.start_time = tk.StringVar(value=now.strftime("%H:%M"))
        st_frame = ttk.Frame(p)
        st_frame.grid(row=r, column=3, sticky="w", padx=8)
        ttk.Entry(st_frame, textvariable=self.start_time, width=6).pack(side="left")
        ttk.Button(st_frame, text="Now", width=4,
                   command=self._set_start_now).pack(side="left", padx=(4, 0)); r += 1

        ttk.Label(p, text="End date:").grid(row=r, column=0, sticky="w", pady=3)
        self.end_date = tk.StringVar(value="")
        ttk.Entry(p, textvariable=self.end_date, width=11).grid(
            row=r, column=1, sticky="w", padx=8)
        ttk.Label(p, text="Time (HH:MM):").grid(row=r, column=2, sticky="w")
        self.end_time = tk.StringVar(value="")
        ttk.Entry(p, textvariable=self.end_time, width=6).grid(
            row=r, column=3, sticky="w", padx=8)
        ttk.Label(p, text="(leave empty = run indefinitely)", foreground="#888888").grid(
            row=r+1, column=1, columnspan=3, sticky="w", padx=8); r += 2


        ttk.Separator(p, orient="horizontal").grid(
            row=r, column=0, columnspan=4, sticky="ew", pady=6); r += 1

        bf = ttk.Frame(p); bf.grid(row=r, column=0, columnspan=4, sticky="w"); r += 1
        self.start_btn = ttk.Button(bf, text="▶  Start Monitoring",
                                    command=self.start_monitoring)
        self.start_btn.pack(side="left", padx=(0,6))
        self.stop_btn = ttk.Button(bf, text="■  Stop Monitoring",
                                   command=self.stop_monitoring, state="disabled")
        self.stop_btn.pack(side="left")

        ttk.Separator(p, orient="horizontal").grid(
            row=r, column=0, columnspan=4, sticky="ew", pady=6); r += 1

        ttk.Label(p, text="Log:").grid(row=r, column=0, sticky="w"); r += 1
        self.log_box = scrolledtext.ScrolledText(p, width=58, height=16,
                                                  state="disabled", font=MONO_FONT)
        self.log_box.grid(row=r, column=0, columnspan=4, sticky="nsew")
        self.log_box.tag_config("OK",    foreground="green")
        self.log_box.tag_config("WARN",  foreground="darkorange")
        self.log_box.tag_config("ERROR", foreground="red")
        self.log_box.tag_config("HEAD",  foreground="purple"); r += 1

        ttk.Button(p, text="Clear log", command=self._clear_log).grid(
            row=r, column=3, sticky="e", pady=4)

        p.rowconfigure(r-1, weight=1)
        p.columnconfigure(1, weight=1)
        p.columnconfigure(3, weight=1)

    # ── auto-update ───────────────────────────────────────────────────────────
    def _check_update(self):
        try:
            with urllib.request.urlopen(UPDATE_VERSION_URL, timeout=5) as r:
                remote = r.read().decode().strip()
            if remote != VERSION:
                self.root.after(0, lambda v=remote: self._prompt_update(v))
        except Exception:
            pass  # no internet or server down — silently skip

    def _prompt_update(self, remote_version):
        if messagebox.askyesno("Update available",
                f"New version {remote_version} is available (you have {VERSION}).\n\n"
                "Download and restart now?"):
            self._do_update()

    def _do_update(self):
        try:
            script_path = os.path.abspath(__file__)
            with urllib.request.urlopen(UPDATE_SCRIPT_URL, timeout=15) as r:
                new_code = r.read()
            with open(script_path, "wb") as f:
                f.write(new_code)
            messagebox.showinfo("Updated", "Update downloaded. Restarting…")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            messagebox.showerror("Update failed", str(e))

    # ── platform change ───────────────────────────────────────────────────────
    def _set_start_now(self):
        n = datetime.datetime.now()
        self.start_date.set(n.strftime("%Y-%m-%d"))
        self.start_time.set(n.strftime("%H:%M"))

    def _platform_changed(self, _event=None):
        name = self.platform_var.get()
        self.url_var.set(PLATFORMS.get(name, ""))
        rule = PLATFORM_RULES.get(name)
        if rule:
            self.sel_var.set(rule["selector"])
            self.targets_text.delete("1.0", "end")
            self.targets_text.insert("1.0", rule["targets"])
            if "refresh_first" in rule:
                self.refresh_first_var.set(rule["refresh_first"])
            if "click_delay" in rule:
                self.delay_var.set(rule["click_delay"])

    # ── helpers ───────────────────────────────────────────────────────────────
    def _targets(self):
        return [l.strip() for l in
                self.targets_text.get("1.0","end").splitlines() if l.strip()]

    def _by(self):
        return BY_MAP.get(self.sel_var.get(), By.CLASS_NAME if SEL else None)

    def _parse_dt(self, d, t):
        t = t.strip()
        fmt = "%Y-%m-%d %H:%M:%S" if len(t) == 8 else "%Y-%m-%d %H:%M"
        return datetime.datetime.strptime(f"{d} {t}", fmt)

    def _alive(self):
        if not self.driver: return False
        try: _ = self.driver.current_url; return True
        except Exception: return False

    def _set_status(self, txt):
        self.root.after(0, lambda t=txt: self.status_var.set(t))

    def log(self, msg, level="INFO"):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_box.config(state="normal")
        self.log_box.insert("end", f"[{ts}] {msg}\n", level)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0","end")
        self.log_box.config(state="disabled")

    # ── browser ───────────────────────────────────────────────────────────────
    def open_browser(self):
        if not SEL:
            messagebox.showerror("Missing","Install: pip3 install selenium"); return
        if self._alive():
            self.log("Browser already open. Use Navigate.", "WARN"); return

        browser = self.browser_var.get()
        url     = self.url_var.get().strip()
        pdir    = os.path.join(PROFILE_DIR, f"{browser.lower()}_profile")
        os.makedirs(pdir, exist_ok=True)
        self._set_status(f"Opening {browser}…")
        self.log(f"Opening {browser}  |  profile: {pdir}")

        def _go():
            try:
                if browser == "Chrome":
                    o = COptions()
                else:
                    o = EOptions()
                o.add_argument(f"--user-data-dir={pdir}")
                o.add_argument("--profile-directory=Default")
                o.add_argument("--disable-blink-features=AutomationControlled")
                o.add_argument("--disable-gpu")
                o.add_experimental_option("excludeSwitches", ["enable-automation"])
                o.add_experimental_option("useAutomationExtension", False)
                if browser == "Chrome":
                    self.driver = webdriver.Chrome(options=o)
                else:
                    edge_paths = [
                        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                    ]
                    for ep in edge_paths:
                        if os.path.exists(ep):
                            o.binary_location = ep
                            break
                    self.driver = webdriver.Edge(options=o)
                self.driver.set_window_size(550, 850)
                self.driver.execute_script(
                    "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
                if url:
                    self.driver.get(url)
                    self.root.after(0, lambda: self.log(f"Navigated to {url}", "OK"))
                self._set_status(f"{browser} open ✓")
                self.root.after(0, lambda: self.log(f"{browser} opened", "OK"))
            except Exception as e:
                self._set_status("Error"); err=str(e)
                self.root.after(0, lambda: self.log(f"Error: {err}", "ERROR"))
                self.root.after(0, lambda: messagebox.showerror("Browser Error", err))

        threading.Thread(target=_go, daemon=True).start()

    def navigate(self):
        if not self._alive():
            messagebox.showwarning("No browser","Open browser first."); return
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("No URL","Enter a URL."); return
        try:
            self.driver.get(url)
            self.log(f"Navigated to {url}", "OK")
        except Exception as e:
            self.log(f"Navigate error: {e}", "ERROR")

    def close_browser(self):
        if self.driver:
            try: self.driver.quit()
            except Exception: pass
            self.driver = None
        self.log("Browser closed.", "WARN")
        self._set_status("Browser closed")

    # ── test ─────────────────────────────────────────────────────────────────
    def test_targets(self):
        if not self._alive():
            messagebox.showwarning("No browser","Open the browser and navigate first."); return
        targets = self._targets()
        if not targets:
            messagebox.showwarning("No targets","Enter at least one selector."); return
        by = self._by()
        self.log("=== TEST ===", "HEAD")
        found = 0
        for t in targets:
            try:
                els = self.driver.find_elements(by, t)
                if els:
                    self.log(f"  ✓  '{t}'  →  {len(els)} element(s)", "OK"); found += 1
                    for el in els[:3]:
                        try:
                            self.driver.execute_script(
                                "arguments[0].style.outline='3px solid red'", el)
                        except Exception: pass
                else:
                    self.log(f"  ✗  '{t}'  →  not found on page", "ERROR")
            except Exception as e:
                self.log(f"  ✗  '{t}'  →  {e}", "ERROR")
        messagebox.showinfo("Test done",
            f"Found {found} of {len(targets)} target(s).\n"
            "Matched elements outlined in red in the browser.")

    # ── click / refresh ───────────────────────────────────────────────────────
    def _do_clicks(self):
        targets = self._targets(); by = self._by()
        load_s = self.load_var.get(); delay_ms = self.delay_var.get()
        if load_s > 0: time.sleep(load_s)
        ok = 0
        for t in targets:
            try:
                el = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable((by, t)))
                el.click(); self.log(f"  ✓  clicked '{t}'", "OK"); ok += 1
            except TimeoutException:
                self.log(f"  ✗  timeout: '{t}'", "WARN")
            except NoSuchElementException:
                self.log(f"  ✗  not found: '{t}'", "WARN")
            except Exception as e:
                self.log(f"  ✗  error '{t}': {e}", "ERROR")
            if delay_ms > 0: time.sleep(delay_ms / 1000)
        return ok, len(targets)

    def _do_refresh(self):
        try:
            self.driver.refresh()
            self.log("  ↺  refreshed")
        except Exception as e:
            self.log(f"  refresh failed: {e}", "ERROR")

    # ── monitoring ────────────────────────────────────────────────────────────
    def start_monitoring(self):
        if not SEL:
            messagebox.showerror("Missing","Install: pip3 install selenium"); return
        if not self._alive():
            messagebox.showwarning("No browser","Open browser first."); return
        if not self._targets():
            messagebox.showwarning("No targets","Enter at least one selector."); return
        try:
            s_dt = self._parse_dt(self.start_date.get(), self.start_time.get())
        except ValueError as e:
            messagebox.showerror("Date error",
                f"Use format YYYY-MM-DD and HH:MM:SS\n{e}"); return
        e_dt = None
        if self.end_date.get().strip() and self.end_time.get().strip():
            try:
                e_dt = self._parse_dt(self.end_date.get(), self.end_time.get())
                if s_dt >= e_dt:
                    messagebox.showerror("Date error", "End must be after start."); return
            except ValueError as e:
                messagebox.showerror("Date error",
                    f"Use format YYYY-MM-DD and HH:MM:SS\n{e}"); return
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        end_str = str(e_dt) if e_dt else "indefinitely"
        self.log(f"Monitoring from {s_dt} → {end_str}", "HEAD")
        self.thread = threading.Thread(target=self._loop,
                                       args=(s_dt, e_dt), daemon=True)
        self.thread.start()

    def stop_monitoring(self):
        self.running = False
        self.root.after(0, lambda: self.start_btn.config(state="normal"))
        self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
        self.log("Monitoring stopped.", "WARN"); self._set_status("Stopped")

    def _sleep(self, secs):
        for _ in range(max(1, int(secs * 10))):
            if not self.running: return False
            time.sleep(0.1)
        return True

    def _loop(self, s_dt, e_dt=None):
        refresh_s     = self.refresh_var.get()
        refresh_first = self.refresh_first_var.get()
        while self.running:
            now = datetime.datetime.now()
            if e_dt and now > e_dt:
                self.root.after(0, lambda: self.log("Schedule ended.", "OK"))
                self.root.after(0, self.stop_monitoring); break
            if now < s_dt:
                secs = int((s_dt - now).total_seconds())
                self._set_status(f"Waiting {secs}s until start…")
                self._sleep(1); continue
            self._set_status("Active — clicking")
            if not self._alive():
                self.root.after(0, lambda: self.log("Browser closed.", "ERROR"))
                self.root.after(0, self.stop_monitoring); break
            if refresh_first: self._do_refresh()
            self.root.after(0, lambda: self.log("── click cycle ──", "HEAD"))
            try:
                ok, tot = self._do_clicks()
                self.root.after(0, lambda o=ok, t=tot:
                    self.log(f"── {o}/{t} clicks OK ──", "OK"))
            except WebDriverException as e:
                err = str(e)
                self.root.after(0, lambda e=err: self.log(f"Browser error: {e}","ERROR"))
                self.root.after(0, self.stop_monitoring); break
            if ok > 0:
                self.root.after(0, lambda: self.log("Click succeeded — stopping.", "OK"))
                self.root.after(0, self.stop_monitoring); break
            if refresh_s > 0:
                self.root.after(0, lambda s=refresh_s:
                    self.log(f"Waiting {s}s before refresh…"))
                if not self._sleep(refresh_s): break
                if not refresh_first and self._alive(): self._do_refresh()
            else:
                self._sleep(1)
        self._set_status("Idle")


# ── entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not SEL:
        print("NOTE: selenium not installed — run:  pip3 install selenium")
    root = tk.Tk()
    try:
        App(root)
    except Exception as e:
        import traceback; traceback.print_exc()
        tk.Label(root, text=f"Error: {e}", fg="red",
                 font=("Courier",12), padx=16, pady=16).pack(expand=True)
    root.mainloop()
