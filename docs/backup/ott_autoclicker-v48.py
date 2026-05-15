#!/usr/bin/env python3
"""OTT AutoClicker – compatible with Python 3.9 / macOS system Tk"""
from __future__ import annotations
import os, sys, platform, time, threading, datetime, subprocess
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
                                                   WebDriverException,
                                                   ElementClickInterceptedException)
    from selenium.webdriver.common.action_chains import ActionChains
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
VERSION = "1.0.48"

UPDATE_VERSION_URL = "https://raw.githubusercontent.com/tampltor13/ott-autoclicker/main/version.txt"
UPDATE_SCRIPT_URL  = "https://raw.githubusercontent.com/tampltor13/ott-autoclicker/main/ott_autoclicker.py"
UPDATE_VBS_URL     = "https://raw.githubusercontent.com/tampltor13/ott-autoclicker/main/run.vbs"
CHANNELS_URL       = "https://raw.githubusercontent.com/tampltor13/ott-autoclicker/main/channels.csv"

PLATFORMS = {
    "Prime Video USA": "https://www.amazon.com/gp/video/sports",
    "Prime Video IT":  "https://www.primevideo.com",
    "Prime Video BR":  "https://www.primevideo.com",
    "Prime Video UK":  "https://www.amazon.co.uk/",
    "Prime Video DE":  "https://www.amazon.de/gp/video/sports",
    "Prime Video ES":  "https://www.primevideo.com",
    "Prime Video JP":  "https://www.amazon.co.jp/",
    "Prime Video MX": "https://www.primevideo.com",
    "Prime Video FR": "https://www.primevideo.com",
    "DAZN DE":      "https://www.dazn.com/en-DE/home",
    "DAZN ES":      "https://www.dazn.com/en-ES/home",
    "Peacock":      "https://www.peacocktv.com/watch/home",
    "Coupang Play": "https://www.coupangplay.com",
    "SPOTV Now JP": "https://spotvnow.jp/schedule/0",
    "NBA Docomo":  "https://nba.docomo.ne.jp/schedule",
    "Paramount+":  "https://www.paramountplus.com",
    "TOD":         "https://www.tod.tv",
    "Disney+":     "https://www.disneyplus.com/home",
    "Disney+ SE": "https://www.disneyplus.com/home",
    "Disney+ DK": "https://www.disneyplus.com/home",
    "Disney+ AR": "https://www.disneyplus.com/home",
    "Custom URL":  "",
}
# Predefined rules per platform: selector type + click targets (one per line)
PLATFORM_RULES = {
    "Prime Video USA": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
    },
    "Prime Video IT": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
    },
    "Prime Video BR": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
    },
    "Prime Video UK": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
    },
    "Prime Video DE": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
    },
    "Prime Video ES": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
    },
    "Prime Video JP": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
    },
    "Prime Video MX": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
    },
    "Prime Video FR": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
    },
    "Peacock": {
        "selector":      "XPath",
        "targets":       '//*[@data-testid="watch-button"]',
        "refresh_first": True,
        "click_delay":   2,
        "load_wait":     10,
    },
    "Coupang Play": {
        "selector":      "XPath",
        "targets":       '//*[@data-cy="playCtaButtonText"]',
        "refresh_first": True,
        "click_delay":   2,
    },
    "SPOTV Now JP": {
        "selector":           "XPath",
        "targets":            '//div[contains(@class,"match-column")]//div[contains(@class,"view-box live")]',
        "post_click_targets": '//button[contains(@class,"vue-confirm-btn live-btn")]',
        "post_click_wait":    3,   # wait before switching to new tab
        "post_switch_wait":   3,   # wait after switching, before clicking popup
        "prevent_new_window": True,
        "ctrl_click":         True,
        "refresh_first":      True,
        "click_delay":        2,
        "load_wait":          8,
        "browser_size":       (650, 550),
    },
    "NBA Docomo": {
        "selector":      "XPath",
        "targets":       '//video-js[contains(@class,"video-js")]',
        "refresh_first": True,
        "click_delay":   2,
        "scroll_after":  290,
        "load_wait":     5,
        "key_press":     " ",
    },
    "Paramount+": {
        "selector":      "XPath",
        "targets":       '//article[contains(@class,"live-event")]//a',
        "refresh_first": True,
        "click_delay":   2,
    },
    "Disney+": {
        "selector":      "XPath",
        "targets":       '//*[@data-testid="modal-action-button"]\n//*[@data-testid="playback-action-button"]',
        "refresh_first": True,
    },
    "Disney+ SE": {
        "selector":      "XPath",
        "targets":       '//*[@data-testid="modal-action-button"]\n//*[@data-testid="playback-action-button"]',
        "refresh_first": True,
    },
    "Disney+ DK": {
        "selector":      "XPath",
        "targets":       '//*[@data-testid="modal-action-button"]\n//*[@data-testid="playback-action-button"]',
        "refresh_first": True,
    },
    "Disney+ AR": {
        "selector":      "XPath",
        "targets":       '//*[@data-testid="modal-action-button"]\n//*[@data-testid="playback-action-button"]',
        "refresh_first": True,
        "load_wait":     10,
    },
    "TOD": {
        "selector":      "ID",
        "targets":       "watch_live_click",
        "refresh_first": False,
    },
    "DAZN DE": {
        "video_detect":    True,
        "video_detect_js": "const v = document.querySelector('video'); return !!(v && !v.paused && !v.error && v.currentTime > 0 && v.readyState >= 3);",
        "refresh_first":   True,
        "load_wait":       60,
        "freeze_recovery": "refresh_only",
    },
    "DAZN ES": {
        "video_detect":    True,
        "video_detect_js": "const v = document.querySelector('video'); return !!(v && !v.paused && !v.error && v.currentTime > 0 && v.readyState >= 3);",
        "refresh_first":   True,
        "load_wait":       60,
        "freeze_recovery": "refresh_only",
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


PREFS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prefs.json")

class App:
    def __init__(self, root):
        self.root    = root
        self.driver  = None
        self.running = False
        self.thread  = None
        root.title(f"OTT AutoClicker  v{VERSION}")
        self._load_geometry()
        root.resizable(True, True)
        root.protocol("WM_DELETE_WINDOW", self._on_close)
        os.makedirs(PROFILE_DIR, exist_ok=True)
        self._build()
        threading.Thread(target=self._check_update, daemon=True).start()
        threading.Thread(target=self._fetch_ip, daemon=True).start()

    def _load_prefs(self):
        try:
            import json
            with open(PREFS_FILE) as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_prefs(self, data):
        try:
            import json
            existing = self._load_prefs()
            existing.update(data)
            with open(PREFS_FILE, "w") as f:
                json.dump(existing, f)
        except Exception:
            pass

    def _load_geometry(self):
        prefs = self._load_prefs()
        self.root.geometry(prefs.get("geometry", "600x400+{}+{}".format(
            self.root.winfo_screenwidth() - 630, 40)))

    def _on_close(self):
        self._save_prefs({"geometry": self.root.geometry()})
        self.root.destroy()

    # ────────────────────────────────────────────────────────────────────────
    def _build(self):
        self._compact      = False
        self._full_geometry = None
        self._compact_log_var = tk.StringVar(value="")

        self._status_bar = ttk.Frame(self.root, relief="sunken")
        self._status_bar.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value="Ready")
        self._compact_btn = ttk.Button(self._status_bar, text="Compact Mode",
                                       command=self._toggle_compact)
        self._compact_btn.pack(side="right", padx=4, pady=1)
        ttk.Label(self._status_bar, textvariable=self.status_var).pack(
            anchor="w", padx=6, pady=2, side="left")

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=6, pady=6)

        t1 = ttk.Frame(self.nb); self.nb.add(t1, text="  Setup  ")
        t2 = ttk.Frame(self.nb); self.nb.add(t2, text="  Monitor  ")
        t_freeze = ttk.Frame(self.nb); self.nb.add(t_freeze, text="  Freeze  ")
        t3 = ttk.Frame(self.nb); self.nb.add(t3, text="  Inspector  ")
        t4 = ttk.Frame(self.nb); self.nb.add(t4, text="  Channels  ")
        self._setup_tab(t1)
        self._monitor_tab(t2)
        self._freeze_tab(t_freeze)
        self._inspector_tab(t3)
        self._channels_tab(t4)
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # compact mode frame (hidden by default)
        self._compact_frame = tk.Frame(self.root)
        tk.Label(self._compact_frame, textvariable=self.status_var,
                 font=("", 9, "bold"), anchor="w").pack(side="left", padx=(10, 4), pady=8)
        tk.Label(self._compact_frame, textvariable=self._compact_log_var,
                 font=("", 8), foreground="#888888", anchor="w").pack(
                     side="left", padx=4, pady=8, fill="x", expand=True)

    # ── SETUP TAB ────────────────────────────────────────────────────────────
    def _setup_tab(self, parent):
        p = ttk.Frame(parent, padding=12)
        p.pack(fill="both", expand=True)

        r = 0
        # IP address display
        self.ip_var = tk.StringVar(value="IP: …")
        ip_frame = ttk.Frame(p)
        ip_frame.grid(row=r, column=0, columnspan=4, sticky="w", pady=(0, 4))
        ttk.Label(ip_frame, textvariable=self.ip_var, foreground="#4fc3f7").pack(side="left")
        ttk.Button(ip_frame, text="↺", width=2,
                   command=lambda: threading.Thread(target=self._fetch_ip, daemon=True).start()
                   ).pack(side="left", padx=(6, 0))
        r += 1
        # browser + platform u istom redu
        ttk.Label(p, text="Browser:").grid(row=r, column=0, sticky="w", pady=3)
        self.browser_var = tk.StringVar(value="Chrome")
        ttk.Combobox(p, textvariable=self.browser_var,
                     values=["Chrome","Edge"], state="readonly", width=14
                     ).grid(row=r, column=1, sticky="w", padx=8)
        self.sys_profile_var = tk.BooleanVar(value=False)
        sp_cb = ttk.Checkbutton(p, text="Use system profile", variable=self.sys_profile_var,
                                command=self._on_sys_profile_toggle)
        sp_cb.grid(row=r, column=2, sticky="w", pady=3)
        i_sp = ttk.Label(p, text=" ⓘ", foreground="#888888", cursor="hand2")
        i_sp.grid(row=r, column=3, sticky="w")
        Tooltip(i_sp, "Use your real Chrome/Edge profile (already logged in).\n"
                      "Close the browser before opening it here.\n"
                      "Default (unchecked) uses the separate AutoClicker profile."); r += 1

        ttk.Label(p, text="Platform:").grid(row=r, column=0, sticky="w", pady=3)
        self.platform_var = tk.StringVar(value="")
        cb = ttk.Combobox(p, textvariable=self.platform_var,
                          values=list(PLATFORMS.keys()), state="readonly", width=22)
        cb.grid(row=r, column=1, columnspan=3, sticky="w", padx=8)
        cb.bind("<<ComboboxSelected>>", self._platform_changed); r += 1

        # url
        ttk.Label(p, text="URL:").grid(row=r, column=0, sticky="w", pady=3)
        self.url_var = tk.StringVar(value="")
        ttk.Entry(p, textvariable=self.url_var, width=50).grid(
            row=r, column=1, columnspan=3, sticky="ew", padx=8); r += 1

        # buttons — row 1
        bf = ttk.Frame(p); bf.grid(row=r, column=0, columnspan=4,
                                    sticky="w", pady=(4,0)); r += 1
        ttk.Button(bf, text="Open Browser",  command=self.open_browser ).pack(side="left", padx=(0,4))
        ttk.Button(bf, text="Navigate →",    command=self.navigate     ).pack(side="left", padx=(0,4))
        ttk.Button(bf, text="Close Browser", command=self.close_browser).pack(side="left", padx=(0,4))
        ttk.Button(bf, text="Test Target",   command=self.test_targets ).pack(side="left")
        # buttons — row 2
        bf2 = ttk.Frame(p); bf2.grid(row=r, column=0, columnspan=4,
                                      sticky="w", pady=(2,8)); r += 1
        self._muted = False
        self._mute_btn = ttk.Button(bf2, text="🔇 Mute", command=self._toggle_mute)
        self._mute_btn.pack(side="left", padx=(0,4))
        ttk.Button(bf2, text="💀 Kill Browser", command=self._kill_browser).pack(side="left")

        ttk.Separator(p, orient="horizontal").grid(
            row=r, column=0, columnspan=4, sticky="ew", pady=4); r += 1

        # click targets
        ttk.Label(p, text="Click targets (one per line):").grid(
            row=r, column=0, columnspan=4, sticky="w", pady=(6,2)); r += 1
        self.targets_text = scrolledtext.ScrolledText(p, width=44, height=3,
                                                       font=MONO_FONT)
        self.targets_text.grid(row=r, column=0, columnspan=4, sticky="ew")
        self.targets_text.insert("1.0", "fbl-play-btn\n"); r += 1

        # event keyword filter (shown only for Paramount+)
        self._kw_row = r
        self._kw_label = ttk.Label(p, text="Event keyword:")
        self._kw_label.grid(row=r, column=0, sticky="w", pady=3)
        self.event_kw_var = tk.StringVar(value="")
        self._kw_frame = ttk.Frame(p)
        self._kw_frame.grid(row=r, column=1, columnspan=3, sticky="ew", padx=8)
        ttk.Entry(self._kw_frame, textvariable=self.event_kw_var, width=30).pack(side="left")
        i_kw = ttk.Label(self._kw_frame, text=" ⓘ", foreground="#888888", cursor="hand2")
        i_kw.pack(side="left")
        Tooltip(i_kw, "Filter which event card to click by name.\n"
                      "e.g. 'Vissel Kobe' — clicks only the card that contains\n"
                      "that text. Leave empty to click the first live event.")
        self._kw_label.grid_remove()
        self._kw_frame.grid_remove()
        self.event_kw_var.trace_add("write", self._on_kw_changed)
        self._base_targets = ""
        self._key_press          = ""
        self._post_click_targets = []
        self._post_click_wait    = 3
        self._post_switch_wait   = 0
        self._prevent_new_window = False
        self._ctrl_click         = False
        self._video_detect       = False
        self._video_detect_js    = ""
        self._freeze_recovery    = "refresh_only"
        r += 1

        # selector type
        ttk.Label(p, text="Selector:").grid(row=r, column=0, sticky="w", pady=3)
        self.sel_var = tk.StringVar(value="Class Name")
        sf = ttk.Frame(p); sf.grid(row=r, column=1, columnspan=3, sticky="w", padx=8)
        for s in SELECTOR_LABELS:
            ttk.Radiobutton(sf, text=s, variable=self.sel_var,
                            value=s).pack(side="left", padx=2); r += 1

        # delays
        ttk.Label(p, text="Click delay (s):").grid(row=r, column=0, sticky="w", pady=3)
        self.delay_var = tk.IntVar(value=1)
        f_delay = ttk.Frame(p); f_delay.grid(row=r, column=1, sticky="w", padx=8)
        tk.Spinbox(f_delay, from_=0, to=300, textvariable=self.delay_var,
                   width=8, bg="#3c3c3c", fg="#ffffff",
                   buttonbackground="#555555", insertbackground="#ffffff").pack(side="left")
        i1 = ttk.Label(f_delay, text=" ⓘ", foreground="#888888", cursor="hand2")
        i1.pack(side="left")
        Tooltip(i1, "Pause between clicks when you have multiple targets.\n"
                    "e.g. 2 = waits 2s between each click.")

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

        # scroll after click + freeze detection (same row, left/right columns)
        ttk.Label(p, text="Scroll after click (px):").grid(row=r, column=0, sticky="w", pady=3)
        self.scroll_after_var = tk.IntVar(value=0)
        f_scroll = ttk.Frame(p); f_scroll.grid(row=r, column=1, sticky="w", padx=8)
        self.scroll_after_spin = tk.Spinbox(f_scroll, from_=0, to=5000, textvariable=self.scroll_after_var,
                   width=8, bg="#3c3c3c", fg="#ffffff",
                   buttonbackground="#555555", insertbackground="#ffffff")
        self.scroll_after_spin.pack(side="left")
        i5 = ttk.Label(f_scroll, text=" ⓘ", foreground="#888888", cursor="hand2")
        i5.pack(side="left")
        Tooltip(i5, "Pixels to scroll down after a successful click.\n"
                    "Use to bring the video player into view.\n"
                    "0 = no scroll.")
        self.freeze_detect_var = tk.BooleanVar(value=False)
        f_fd = ttk.Frame(p); f_fd.grid(row=r, column=2, columnspan=2, sticky="w")
        ttk.Checkbutton(f_fd, text="Freeze Detection",
                        variable=self.freeze_detect_var).pack(side="left")
        i_fd = ttk.Label(f_fd, text=" ⓘ", foreground="#888888", cursor="hand2")
        i_fd.pack(side="left")
        Tooltip(i_fd, "After a successful click, starts monitoring video playback.\n"
                      "Checks every 60s if video is still playing (via currentTime).\n"
                      "If frozen or errored, refreshes the page automatically.\n"
                      "Runs for 4 hours from monitoring start time."); r += 1

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

    # ── FREEZE TAB ───────────────────────────────────────────────────────────
    def _freeze_tab(self, parent):
        p = ttk.Frame(parent, padding=12)
        p.pack(fill="both", expand=True)

        # date/time fields
        gf = ttk.Frame(p); gf.pack(fill="x", pady=(0, 6))
        now = datetime.datetime.now()

        ttk.Label(gf, text="Start date:").grid(row=0, column=0, sticky="w", pady=3)
        self._freeze_start_date = tk.StringVar(value=now.strftime("%Y-%m-%d"))
        ttk.Entry(gf, textvariable=self._freeze_start_date, width=11).grid(row=0, column=1, sticky="w", padx=8)
        ttk.Label(gf, text="Time (HH:MM):").grid(row=0, column=2, sticky="w")
        self._freeze_start_time = tk.StringVar(value=now.strftime("%H:%M"))
        ttk.Entry(gf, textvariable=self._freeze_start_time, width=6).grid(row=0, column=3, sticky="w", padx=8)

        ttk.Label(gf, text="End date:").grid(row=1, column=0, sticky="w", pady=3)
        self._freeze_end_date = tk.StringVar(value="")
        ttk.Entry(gf, textvariable=self._freeze_end_date, width=11).grid(row=1, column=1, sticky="w", padx=8)
        ttk.Label(gf, text="Time (HH:MM):").grid(row=1, column=2, sticky="w")
        self._freeze_end_time = tk.StringVar(value="")
        ttk.Entry(gf, textvariable=self._freeze_end_time, width=6).grid(row=1, column=3, sticky="w", padx=8)

        ttk.Separator(p, orient="horizontal").pack(fill="x", pady=(4, 6))

        # status + buttons
        bf = ttk.Frame(p); bf.pack(fill="x", pady=(0, 4))
        self._freeze_status_var = tk.StringVar(value="Freeze Detection inactive")
        ttk.Label(bf, textvariable=self._freeze_status_var,
                  foreground="#4fc3f7").pack(side="left")
        self._freeze_stop_btn = ttk.Button(bf, text="■  Stop Freeze Detection",
                                           command=self.stop_freeze_detection,
                                           state="disabled")
        self._freeze_stop_btn.pack(side="right")
        ttk.Button(bf, text="Clear log",
                   command=self._clear_freeze_log).pack(side="right", padx=(0,6))

        ttk.Separator(p, orient="horizontal").pack(fill="x", pady=(0, 6))

        # log box
        self._freeze_box = scrolledtext.ScrolledText(p, width=58, height=20,
                                                      state="disabled", font=MONO_FONT)
        self._freeze_box.pack(fill="both", expand=True)
        self._freeze_box.tag_config("OK",    foreground="green")
        self._freeze_box.tag_config("WARN",  foreground="darkorange")
        self._freeze_box.tag_config("ERROR", foreground="red")
        self._freeze_box.tag_config("HEAD",  foreground="purple")

        # state
        self._freeze_running = False
        self._freeze_thread  = None

    def _flog(self, msg, level="INFO"):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._freeze_box.config(state="normal")
        self._freeze_box.insert("end", f"[{ts}] {msg}\n", level)
        self._freeze_box.see("end")
        self._freeze_box.config(state="disabled")

    def _clear_freeze_log(self):
        self._freeze_box.config(state="normal")
        self._freeze_box.delete("1.0", "end")
        self._freeze_box.config(state="disabled")

    def start_freeze_detection(self, end_dt):
        """Called automatically after successful click if Freeze Detection is enabled."""
        if self._freeze_running:
            return
        # read end_dt from fields if user edited them manually
        try:
            d = self._freeze_end_date.get().strip()
            t = self._freeze_end_time.get().strip()
            if d and t:
                end_dt = self._parse_dt(d, t)
        except Exception:
            pass  # keep auto-calculated end_dt
        self._freeze_running = True
        # populate start/end fields
        start_now = datetime.datetime.now()
        self.root.after(0, lambda: self._freeze_start_date.set(start_now.strftime("%Y-%m-%d")))
        self.root.after(0, lambda: self._freeze_start_time.set(start_now.strftime("%H:%M")))
        self.root.after(0, lambda: self._freeze_end_date.set(end_dt.strftime("%Y-%m-%d")))
        self.root.after(0, lambda: self._freeze_end_time.set(end_dt.strftime("%H:%M")))
        self.root.after(0, lambda: self._freeze_stop_btn.config(state="normal"))
        self.root.after(0, lambda: self._freeze_status_var.set("Freeze Detection active…"))
        self._set_status("Freeze Detection active")
        self._freeze_thread = threading.Thread(
            target=self._freeze_loop, args=(end_dt,), daemon=True)
        self._freeze_thread.start()

    def stop_freeze_detection(self):
        self._freeze_running = False
        self.root.after(0, lambda: self._freeze_stop_btn.config(state="disabled"))
        self.root.after(0, lambda: self._freeze_status_var.set("Freeze Detection inactive"))
        self.root.after(0, lambda: self._flog("Freeze Detection stopped.", "WARN"))
        self._set_status("Idle")

    def _freeze_loop(self, end_dt):
        CHECK_INTERVAL = 30   # seconds between checks
        REFRESH_WAIT   = 60   # seconds to wait after refresh before re-checking

        self.root.after(0, lambda: self._flog(
            f"── Freeze Detection started (runs until {end_dt.strftime('%H:%M')}) ──", "HEAD"))

        prev_time = None

        while self._freeze_running:
            # check end time
            if datetime.datetime.now() >= end_dt:
                self.root.after(0, lambda: self._flog(
                    "── Freeze Detection: end time reached, stopping. ──", "HEAD"))
                self.root.after(0, self.stop_freeze_detection)
                break

            # check browser still alive
            if not self._alive():
                self.root.after(0, lambda: self._flog(
                    "Browser closed — stopping Freeze Detection.", "ERROR"))
                self.root.after(0, self.stop_freeze_detection)
                break

            # sample currentTime
            current_time = None
            try:
                current_time = self.driver.execute_script(
                    "const v = document.querySelector('video'); "
                    "return v ? v.currentTime : null;")
            except Exception as e:
                err = str(e)
                self.root.after(0, lambda m=err: self._flog(f"JS error: {m}", "ERROR"))

            if current_time is None:
                self.root.after(0, lambda: self._flog(
                    "  ⚠  No video element found — refreshing…", "WARN"))
                self._do_freeze_refresh(REFRESH_WAIT)
                prev_time = None
                continue

            if prev_time is None:
                # first sample — just record and wait
                prev_time = current_time
                self.root.after(0, lambda t=current_time: self._flog(
                    f"  ▶  First sample: currentTime={t:.1f}s — waiting {CHECK_INTERVAL}s…"))
                if not self._freeze_sleep(CHECK_INTERVAL):
                    break
                continue

            # compare — delta must be at least 80% of CHECK_INTERVAL
            delta = current_time - prev_time
            min_expected = CHECK_INTERVAL * 0.8
            if delta >= min_expected:
                self.root.after(0, lambda t=current_time, d=delta: self._flog(
                    f"  ✓  Video OK — currentTime={t:.1f}s (+{d:.1f}s)", "OK"))
                prev_time = current_time
                if not self._freeze_sleep(CHECK_INTERVAL):
                    break
            else:
                self.root.after(0, lambda t=current_time, p=prev_time, d=delta, m=min_expected: self._flog(
                    f"  ❄  FREEZE detected! currentTime={t:.1f}s (+{d:.1f}s, expected ≥{m:.0f}s) — refreshing…", "ERROR"))
                self._do_freeze_refresh(REFRESH_WAIT)
                prev_time = None

        self._freeze_running = False
        self.root.after(0, lambda: self._freeze_stop_btn.config(state="disabled"))
        self.root.after(0, lambda: self._freeze_status_var.set("Freeze Detection inactive"))

    def _do_freeze_refresh(self, wait_s):
        """Refresh page and wait before next check. If recovery=remonitor, restart click monitoring."""
        try:
            self.driver.refresh()
            self.root.after(0, lambda: self._flog("  ↺  Page refreshed — waiting for video to load…", "WARN"))
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda m=err: self._flog(f"  Refresh error: {m}", "ERROR"))
        # remonitor: skip the 60s wait — monitoring loop handles its own load_wait
        if getattr(self, "_freeze_recovery", "refresh_only") == "remonitor":
            self.root.after(0, lambda: self._flog(
                "  ▶  Restarting click monitoring to recover playback…", "WARN"))
            self._freeze_running = False  # pause freeze loop
            self.root.after(0, self._freeze_remonitor)
        else:
            # refresh_only: wait before re-checking (video needs time to reload)
            self.root.after(0, lambda s=wait_s: self._flog(f"  ⏱  Waiting {s}s…"))
            self._freeze_sleep(wait_s)

    def _freeze_remonitor(self):
        """Restart click monitoring after a freeze. When click succeeds, freeze detection resumes."""
        if not self._alive():
            self._flog("Browser closed — cannot remonitor.", "ERROR")
            return
        # set start time to now so freeze end time stays consistent
        self._monitor_start_dt = datetime.datetime.now()
        self.running = True
        self.root.after(0, lambda: self.start_btn.config(state="disabled"))
        self.root.after(0, lambda: self.stop_btn.config(state="normal"))
        self.log("── Freeze Recovery: restarting click monitoring ──", "HEAD")
        s_dt = datetime.datetime.now()
        self.thread = threading.Thread(target=self._loop, args=(s_dt, None), daemon=True)
        self.thread.start()

    def _freeze_sleep(self, secs):
        """Interruptible sleep for freeze loop."""
        for _ in range(max(1, int(secs * 10))):
            if not self._freeze_running:
                return False
            time.sleep(0.1)
        return True

    # ── INSPECTOR TAB ────────────────────────────────────────────────────────
    def _inspector_tab(self, parent):
        p = ttk.Frame(parent, padding=12)
        p.pack(fill="both", expand=True)

        self._inspect_active = False

        # top bar
        bf = ttk.Frame(p); bf.pack(fill="x", pady=(0, 6))
        self.inspect_btn = ttk.Button(bf, text="▶  Start Inspect Mode",
                                      command=self._toggle_inspect)
        self.inspect_btn.pack(side="left", padx=(0, 8))
        ttk.Button(bf, text="Clear", command=self._clear_inspect).pack(side="left", padx=(0, 4))
        ttk.Button(bf, text="Save to file", command=self._save_inspect).pack(side="left")
        self._inspect_status = tk.StringVar(value="Inspect mode OFF — click Start to begin")
        ttk.Label(bf, textvariable=self._inspect_status,
                  foreground="#888888").pack(side="left", padx=12)

        ttk.Separator(p, orient="horizontal").pack(fill="x", pady=(0, 6))

        # log box
        self._inspect_box = scrolledtext.ScrolledText(p, width=58, height=18,
                                                       state="disabled", font=MONO_FONT)
        self._inspect_box.pack(fill="both", expand=True)
        self._inspect_box.tag_config("HEAD", foreground="purple")
        self._inspect_box.tag_config("KEY",  foreground="#4fc3f7")
        self._inspect_box.tag_config("VAL",  foreground="green")

    def _toggle_inspect(self):
        if not self._alive():
            messagebox.showwarning("No browser", "Open browser first."); return
        self._inspect_active = not self._inspect_active
        if self._inspect_active:
            self._inject_inspector()
            self.inspect_btn.config(text="■  Stop Inspect Mode")
            self._inspect_status.set("Inspect mode ON — click any element in the browser")
            self._poll_inspect()
        else:
            self.inspect_btn.config(text="▶  Start Inspect Mode")
            self._inspect_status.set("Inspect mode OFF — click Start to begin")

    def _inject_inspector(self):
        js = """
(function() {
    if (window._inspectInstalled) return;
    window._inspectInstalled = true;
    window._inspectedElement = null;
    document.addEventListener('click', function(e) {
        var el = e.target;
        var walked = el;
        for (var i = 0; i < 6; i++) {
            if (!walked || walked === document.body) break;
            if (walked.tagName === 'ARTICLE' ||
                walked.tagName === 'A' ||
                walked.tagName === 'BUTTON' ||
                (walked.className && typeof walked.className === 'string' &&
                 (walked.className.includes('live') || walked.className.includes('play') ||
                  walked.className.includes('watch') || walked.className.includes('event')))) {
                el = walked; break;
            }
            walked = walked.parentElement;
        }
        var info = {
            tag:     el.tagName,
            id:      el.id || '',
            cls:     (typeof el.className === 'string') ? el.className.trim() : '',
            href:    el.href || el.getAttribute('href') || '',
            text:    el.innerText ? el.innerText.trim().substring(0, 120) : '',
            outer:   el.outerHTML ? el.outerHTML.substring(0, 800) : ''
        };
        var attrs = {};
        for (var a = 0; a < el.attributes.length; a++) {
            var at = el.attributes[a];
            if (at.name.startsWith('data-')) attrs[at.name] = at.value;
        }
        info.data = attrs;
        window._inspectedElement = info;
    }, true);
})();
"""
        try:
            self.driver.execute_script(js)
        except Exception as e:
            self._ilog(f"Inject error: {e}")

    def _poll_inspect(self):
        if not self._inspect_active or not self._alive():
            return
        try:
            installed = self.driver.execute_script("return !!window._inspectInstalled")
            if not installed:
                self._inject_inspector()
            info = self.driver.execute_script("return window._inspectedElement")
            if info:
                self.driver.execute_script("window._inspectedElement = null")
                self._log_capture(info)
        except Exception:
            pass
        self.root.after(400, self._poll_inspect)

    def _log_capture(self, info):
        self._inspect_box.config(state="normal")
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._inspect_box.insert("end", f"── [{ts}] {info.get('tag','')} ──\n", "HEAD")
        for key in ("id", "cls", "href", "text"):
            val = info.get(key, "").strip()
            if val:
                self._inspect_box.insert("end", f"  {key}: ", "KEY")
                self._inspect_box.insert("end", f"{val}\n", "VAL")
        for k, v in (info.get("data") or {}).items():
            self._inspect_box.insert("end", f"  {k}: ", "KEY")
            self._inspect_box.insert("end", f"{v}\n", "VAL")
        # suggest XPath
        cls = info.get("cls", "").strip()
        tag = info.get("tag", "*").lower()
        if cls:
            first_cls = cls.split()[0]
            xpath = f'//{tag}[contains(@class,"{first_cls}")]'
            self._inspect_box.insert("end", f"  xpath: ", "KEY")
            self._inspect_box.insert("end", f"{xpath}\n", "VAL")
        self._inspect_box.insert("end", "\n")
        self._inspect_box.see("end")
        self._inspect_box.config(state="disabled")
        # store raw for save
        if not hasattr(self, "_captures"):
            self._captures = []
        self._captures.append(info)

    def _ilog(self, msg):
        self._inspect_box.config(state="normal")
        self._inspect_box.insert("end", msg + "\n")
        self._inspect_box.see("end")
        self._inspect_box.config(state="disabled")

    def _clear_inspect(self):
        self._inspect_box.config(state="normal")
        self._inspect_box.delete("1.0", "end")
        self._inspect_box.config(state="disabled")
        self._captures = []

    def _save_inspect(self):
        if not hasattr(self, "_captures") or not self._captures:
            messagebox.showinfo("Nothing to save", "No captures yet."); return
        import json
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captures.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._captures, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Saved", f"Saved {len(self._captures)} capture(s) to:\n{path}")

    # ── CHANNELS TAB ─────────────────────────────────────────────────────────
    def _channels_tab(self, parent):
        p = ttk.Frame(parent, padding=8)
        p.pack(fill="both", expand=True)

        # top bar
        bf = ttk.Frame(p); bf.pack(fill="x", pady=(0, 6))
        ttk.Button(bf, text="↺  Refresh", command=self._load_channels).pack(side="left")
        self._ch_status = tk.StringVar(value="")
        ttk.Label(bf, textvariable=self._ch_status,
                  foreground="#888888").pack(side="left", padx=10)

        # treeview
        cols = ("Country", "Channel", "ID", "PC", "Status")
        self._ch_tree = ttk.Treeview(p, columns=cols, show="headings",
                                      selectmode="browse")
        col_widths = {"Country": 80, "Channel": 210, "ID": 55, "PC": 110, "Status": 70}
        for c in cols:
            self._ch_tree.heading(c, text=c)
            self._ch_tree.column(c, width=col_widths[c], anchor="w")

        # color tags
        self._ch_tree.tag_configure("Chrome", foreground="#f4b400")
        self._ch_tree.tag_configure("Edge",   foreground="#4fc3f7")
        self._ch_tree.tag_configure("Both",   foreground="#81c995")
        self._ch_tree.tag_configure("?",      foreground="#888888")

        sb = ttk.Scrollbar(p, orient="vertical", command=self._ch_tree.yview)
        self._ch_tree.configure(yscrollcommand=sb.set)
        self._ch_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")

        self._channels_loaded = False

    def _on_tab_changed(self, _event=None):
        tab = self.nb.tab(self.nb.select(), "text").strip()
        if tab == "Channels" and not self._channels_loaded:
            threading.Thread(target=self._load_channels, daemon=True).start()

    def _load_channels(self):
        self.root.after(0, lambda: self._ch_status.set("Loading…"))
        try:
            import csv, io
            import ssl as _ssl
            _ctx = _ssl.create_default_context()
            _ctx.check_hostname = False
            _ctx.verify_mode = _ssl.CERT_NONE
            with urllib.request.urlopen(CHANNELS_URL, timeout=8, context=_ctx) as r:
                raw = r.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(raw))
            rows = list(reader)
            def _update():
                self._ch_tree.delete(*self._ch_tree.get_children())
                for row in rows:
                    status = row.get("Status", "?").strip()
                    tag = status if status in ("Chrome", "Edge", "Both") else "?"
                    self._ch_tree.insert("", "end", values=(
                        row.get("Country","").strip(),
                        row.get("Channel","").strip(),
                        row.get("ID","").strip(),
                        row.get("PC","").strip(),
                        status,
                    ), tags=(tag,))
                self._ch_status.set(f"{len(rows)} channels — {__import__('datetime').datetime.now().strftime('%H:%M:%S')}")
                self._channels_loaded = True
            self.root.after(0, _update)
        except Exception as e:
            _err = str(e)
            self.root.after(0, lambda msg=_err: self._ch_status.set(f"Error: {msg}"))

    # ── IP fetch ──────────────────────────────────────────────────────────────
    def _fetch_ip(self):
        self.root.after(0, lambda: self.ip_var.set("IP: …"))
        try:
            import json
            with urllib.request.urlopen("http://ip-api.com/json/?fields=query,country", timeout=5) as r:
                data = json.loads(r.read().decode())
            ip      = data.get("query", "?")
            country = data.get("country", "?")
            self.root.after(0, lambda: self.ip_var.set(f"IP: {ip}  ({country})"))
        except Exception:
            self.root.after(0, lambda: self.ip_var.set("IP: unavailable"))

    # ── auto-update ───────────────────────────────────────────────────────────
    def _check_update(self):
        try:
            with urllib.request.urlopen(UPDATE_VERSION_URL, timeout=5) as r:
                remote = r.read().decode().strip()
            def _ver(v):
                return tuple(int(x) for x in v.split("."))
            if _ver(remote) > _ver(VERSION):
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
            app_dir = os.path.dirname(script_path)
            with urllib.request.urlopen(UPDATE_SCRIPT_URL, timeout=15) as r:
                new_code = r.read()
            with open(script_path, "wb") as f:
                f.write(new_code)
            # also update run.vbs if it exists next to the script
            vbs_path = os.path.join(app_dir, "run.vbs")
            if os.path.exists(vbs_path):
                try:
                    with urllib.request.urlopen(UPDATE_VBS_URL, timeout=10) as r:
                        new_vbs = r.read()
                    with open(vbs_path, "wb") as f:
                        f.write(new_vbs)
                except Exception:
                    pass  # non-critical, don't block the update
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
        self._video_detect = False
        rule = PLATFORM_RULES.get(name)
        if rule:
            if "selector" in rule:
                self.sel_var.set(rule["selector"])
            self._base_targets = rule.get("targets", "")
            self.targets_text.delete("1.0", "end")
            self.targets_text.insert("1.0", rule.get("targets", ""))
            if "refresh_first" in rule:
                self.refresh_first_var.set(rule["refresh_first"])
            if "click_delay" in rule:
                self.delay_var.set(rule["click_delay"])
            if "scroll_after" in rule:
                self.scroll_after_var.set(rule["scroll_after"])
            else:
                self.scroll_after_var.set(0)
            # force spinbox visual refresh on Windows (IntVar.set alone may not update display)
            val = self.scroll_after_var.get()
            self.scroll_after_spin.delete(0, "end")
            self.scroll_after_spin.insert(0, str(val))
            if "load_wait" in rule:
                self.load_var.set(rule["load_wait"])
            else:
                self.load_var.set(5)
            self._key_press          = rule.get("key_press", "")
            self._post_click_targets = rule.get("post_click_targets", "").splitlines()
            self._post_click_wait    = rule.get("post_click_wait", 3)
            self._post_switch_wait   = rule.get("post_switch_wait", 0)
            self._prevent_new_window = rule.get("prevent_new_window", False)
            self._ctrl_click         = rule.get("ctrl_click", False)
            self._video_detect       = rule.get("video_detect", False)
            self._video_detect_js    = rule.get("video_detect_js", "")
            self._freeze_recovery    = rule.get("freeze_recovery", "refresh_only")
        # set default browser per platform
        if name in ("TOD", "Paramount+", "NBA Docomo", "Disney+ SE", "Disney+ DK", "Prime Video MX", "Coupang Play", "Peacock", "DAZN ES"):
            self.browser_var.set("Edge")
        elif name:
            self.browser_var.set("Chrome")
        # freeze detection default per platform
        if name in ("DAZN DE", "DAZN ES"):
            self.freeze_detect_var.set(True)
        else:
            self.freeze_detect_var.set(False)
        # show/hide event keyword field
        if name in ("Paramount+", "SPOTV Now JP"):
            self._kw_label.grid()
            self._kw_frame.grid()
        else:
            self.event_kw_var.set("")
            self._kw_label.grid_remove()
            self._kw_frame.grid_remove()
    def _on_kw_changed(self, *_):
        """Live-update targets_text when event keyword changes."""
        kw = self.event_kw_var.get().strip()
        base = self._base_targets
        if not base:
            return
        if kw:
            lines = []
            for t in base.splitlines():
                t = t.strip()
                if not t:
                    continue
                idx = t.find("]")
                if idx != -1:
                    t = t[:idx] + f" and contains(.,'{kw}')" + t[idx:]
                else:
                    t = t + f"[contains(.,'{kw}')]"
                lines.append(t)
            effective = "\n".join(lines)
        else:
            effective = base
        self.targets_text.delete("1.0", "end")
        self.targets_text.insert("1.0", effective)

    # ── helpers ───────────────────────────────────────────────────────────────
    def _targets(self):
        return [l.strip() for l in
                self.targets_text.get("1.0","end").splitlines() if l.strip()]

    def _effective_targets(self):
        """Returns targets as shown in targets_text (already includes keyword if set)."""
        return self._targets()

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

    def _toggle_compact(self):
        if not self._compact:
            self._full_geometry = self.root.geometry()
            self.nb.pack_forget()
            self._compact_frame.pack(fill="x", before=self._status_bar)
            self.root.geometry(f"400x60+{self.root.winfo_x()}+{self.root.winfo_y()}")
            self.root.resizable(False, False)
            self._compact_btn.configure(text="Expand")
            self._compact = True
        else:
            self._compact_frame.pack_forget()
            self.nb.pack(fill="both", expand=True, padx=6, pady=6)
            if self._full_geometry:
                self.root.geometry(self._full_geometry)
            self.root.resizable(True, True)
            self._compact_btn.configure(text="Compact Mode")
            self._compact = False

    def log(self, msg, level="INFO"):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_box.config(state="normal")
        self.log_box.insert("end", f"[{ts}] {msg}\n", level)
        self.log_box.see("end")
        self.log_box.config(state="disabled")
        # update compact view with last log line
        short = msg if len(msg) <= 55 else msg[:52] + "…"
        self._compact_log_var.set(f"[{ts}] {short}")

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0","end")
        self.log_box.config(state="disabled")

    # ── browser ───────────────────────────────────────────────────────────────
    def _kill_procs(self, procs_win, procs_mac):
        """Kill a list of processes. Returns list of killed names."""
        killed = []
        if IS_MAC:
            for name in procs_mac:
                try:
                    r = subprocess.run(["pkill", "-f", name], capture_output=True)
                    if r.returncode == 0:
                        killed.append(name)
                except Exception:
                    pass
        else:
            for proc in procs_win:
                try:
                    r = subprocess.run(
                        ["taskkill", "/F", "/IM", proc, "/T"],
                        capture_output=True, text=True, creationflags=0x08000000)
                    if r.returncode == 0:
                        killed.append(proc)
                except Exception:
                    pass
        return killed

    def _on_sys_profile_toggle(self):
        """When 'Use system profile' is checked, show kill-browser dialog."""
        if not self.sys_profile_var.get():
            return  # unchecked — nothing to do

        choice = tk.StringVar(value="cancel")

        dlg = tk.Toplevel(self.root)
        dlg.title("Close browsers")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.transient(self.root)
        self.root.update_idletasks()
        rx = self.root.winfo_x(); ry = self.root.winfo_y()
        rw = self.root.winfo_width(); rh = self.root.winfo_height()
        dlg.update_idletasks()
        dw = dlg.winfo_reqwidth(); dh = dlg.winfo_reqheight()
        dlg.geometry(f"+{rx + (rw - dw)//2}+{ry + (rh - dh)//2}")

        tk.Label(dlg,
                 text="Which browser processes should be closed?",
                 font=("", 10, "bold")).pack(padx=20, pady=(12, 4))
        tk.Label(dlg,
                 text="The system profile is locked while the browser is open.\n"
                      "Selenium cannot attach to it if Chrome or Edge is already running.\n"
                      "Close all instances before opening the browser here.",
                 justify="left", foreground="#888888").pack(padx=20, pady=(0, 10))

        bf = tk.Frame(dlg, padx=16, pady=8)
        bf.pack()

        def pick(val):
            choice.set(val)
            dlg.destroy()

        tk.Button(bf, text="Kill Chrome", width=14,
                  command=lambda: pick("chrome")).grid(row=0, column=0, padx=4, pady=4)
        tk.Button(bf, text="Kill Edge",   width=14,
                  command=lambda: pick("edge")).grid(row=0, column=1, padx=4, pady=4)
        tk.Button(bf, text="Both",        width=14,
                  command=lambda: pick("both")).grid(row=0, column=2, padx=4, pady=4)
        tk.Button(bf, text="Cancel",      width=14,
                  command=lambda: pick("cancel")).grid(row=0, column=3, padx=4, pady=4)

        dlg.wait_window()

        val = choice.get()
        if val == "cancel":
            self.sys_profile_var.set(False)
            return

        chrome_win = ["chrome.exe", "chromedriver.exe"]
        chrome_mac = ["Google Chrome", "chromedriver"]
        edge_win   = ["msedge.exe", "msedgedriver.exe"]
        edge_mac   = ["Microsoft Edge", "msedgedriver"]

        if val == "chrome":
            killed = self._kill_procs(chrome_win, chrome_mac)
        elif val == "edge":
            killed = self._kill_procs(edge_win, edge_mac)
        else:  # both
            killed = self._kill_procs(chrome_win + edge_win, chrome_mac + edge_mac)

        if killed:
            self.log(f"Closed for system profile: {', '.join(killed)}", "WARN")
        else:
            self.log("System profile: no running browser processes found.", "WARN")

    def open_browser(self):
        if not SEL:
            messagebox.showerror("Missing","Install: pip3 install selenium"); return
        if self._alive():
            self.log("Browser already open. Use Navigate.", "WARN"); return

        browser    = self.browser_var.get()
        url        = self.url_var.get().strip()
        use_sys    = self.sys_profile_var.get()
        localappdata = os.environ.get("LOCALAPPDATA", "")
        if use_sys:
            if browser == "Chrome":
                pdir = os.path.join(localappdata, "Google", "Chrome", "User Data")
            else:
                pdir = os.path.join(localappdata, "Microsoft", "Edge", "User Data")
        else:
            pdir = os.path.join(PROFILE_DIR, f"{browser.lower()}_profile")
            os.makedirs(pdir, exist_ok=True)
        self._set_status(f"Opening {browser}…")
        self.log(f"Opening {browser}  |  {'system' if use_sys else 'autoclicker'} profile: {pdir}")

        def _go():
            try:
                if browser == "Chrome":
                    o = COptions()
                else:
                    o = EOptions()
                # detect active profile directory for system profile
                profile_dir_name = "Default"
                if use_sys and not IS_MAC:
                    try:
                        import json as _json
                        local_state_path = os.path.join(pdir, "Local State")
                        with open(local_state_path, encoding="utf-8") as _f:
                            _ls = _json.load(_f)
                        profile_dir_name = _ls.get("profile", {}).get("last_used", "Default")
                    except Exception:
                        profile_dir_name = "Default"
                    self.root.after(0, lambda p=profile_dir_name: self.log(f"Using profile directory: {p}"))
                o.add_argument(f"--user-data-dir={pdir}")
                o.add_argument(f"--profile-directory={profile_dir_name}")
                o.add_argument("--disable-blink-features=AutomationControlled")
                o.add_argument("--no-sandbox")
                o.add_argument("--disable-dev-shm-usage")
                o.add_experimental_option("excludeSwitches", ["enable-automation"])
                o.add_experimental_option("useAutomationExtension", False)
                if browser == "Chrome":
                    self.driver = webdriver.Chrome(options=o)
                else:
                    edge_bin = None
                    # 1) try Windows registry (most reliable)
                    if not IS_MAC:
                        try:
                            import winreg
                            key = winreg.OpenKey(
                                winreg.HKEY_LOCAL_MACHINE,
                                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe")
                            edge_bin, _ = winreg.QueryValueEx(key, "")
                            winreg.CloseKey(key)
                        except Exception:
                            edge_bin = None
                    # 2) fallback: known install paths
                    if not edge_bin or not os.path.exists(edge_bin):
                        for ep in [
                            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                            os.path.join(os.environ.get("LOCALAPPDATA", ""),
                                         r"Microsoft\Edge\Application\msedge.exe"),
                        ]:
                            if os.path.exists(ep):
                                edge_bin = ep
                                break
                    if edge_bin:
                        o.binary_location = edge_bin
                        self.root.after(0, lambda b=edge_bin: self.log(f"Edge binary: {b}"))
                    else:
                        self.root.after(0, lambda: self.log(
                            "Edge binary not found in registry or known paths", "WARN"))
                    # find msedgedriver locally — avoids Selenium Manager network download
                    import shutil as _shutil
                    msedgedriver = None
                    drv_name = "msedgedriver.exe" if not IS_MAC else "msedgedriver"
                    # a) app folder (user can drop msedgedriver.exe next to the script)
                    _app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                    _local = os.path.join(_app_dir, drv_name)
                    if os.path.exists(_local):
                        msedgedriver = _local
                    # b) PATH
                    if not msedgedriver:
                        msedgedriver = _shutil.which("msedgedriver") or _shutil.which(drv_name)
                    # c) Selenium Manager cache  (~/.cache/selenium or %LOCALAPPDATA%\selenium)
                    if not msedgedriver:
                        _cache_roots = [
                            os.path.join(os.environ.get("LOCALAPPDATA", ""), "selenium", "msedgedriver"),
                            os.path.join(os.path.expanduser("~"), ".cache", "selenium", "msedgedriver"),
                        ]
                        for _cr in _cache_roots:
                            if os.path.isdir(_cr):
                                for _root, _dirs, _files in os.walk(_cr):
                                    if drv_name in _files:
                                        msedgedriver = os.path.join(_root, drv_name)
                                        break
                            if msedgedriver:
                                break
                    # version check: skip cached driver if major version doesn't match Edge
                    if msedgedriver:
                        try:
                            import re as _re
                            _cflags = 0x08000000 if not IS_MAC else 0
                            # driver major version from cache path or --version
                            _dm = None
                            _m = _re.search(r'[/\\](\d+)\.\d+\.\d+\.\d+[/\\]', msedgedriver)
                            if _m:
                                _dm = int(_m.group(1))
                            else:
                                try:
                                    _r = subprocess.run([msedgedriver, "--version"],
                                        capture_output=True, text=True, timeout=5,
                                        creationflags=_cflags)
                                    _m2 = _re.search(r'(\d+)\.\d+', _r.stdout)
                                    if _m2: _dm = int(_m2.group(1))
                                except Exception: pass
                            # Edge major version — try multiple registry locations + PowerShell fallback
                            _em = None
                            try:
                                import winreg as _wr
                                _reg_targets = [
                                    (_wr.HKEY_CURRENT_USER,  r"Software\Microsoft\Edge\BLBeacon", "version"),
                                    (_wr.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Edge\BLBeacon", "version"),
                                    (_wr.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Edge\BLBeacon", "version"),
                                    (_wr.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}", "pv"),
                                    (_wr.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}", "pv"),
                                ]
                                for _hive, _rk, _vname in _reg_targets:
                                    try:
                                        _k = _wr.OpenKey(_hive, _rk)
                                        _v, _ = _wr.QueryValueEx(_k, _vname)
                                        _wr.CloseKey(_k)
                                        _em = int(_v.split(".")[0]); break
                                    except Exception: pass
                            except Exception: pass
                            # PowerShell fallback: read version from Edge binary file
                            if not _em and edge_bin and os.path.exists(edge_bin):
                                try:
                                    _ps = subprocess.run(
                                        ["powershell", "-command",
                                         f"(Get-Item '{edge_bin}').VersionInfo.ProductVersion"],
                                        capture_output=True, text=True, timeout=8,
                                        creationflags=_cflags)
                                    _m3 = _re.search(r'(\d+)\.\d+', _ps.stdout.strip())
                                    if _m3: _em = int(_m3.group(1))
                                except Exception: pass
                            # if driver version known but Edge version unknown → skip cache (safe default)
                            if _dm and not _em:
                                self.root.after(0, lambda: self.log(
                                    "Edge version unknown — skipping cached driver, using Selenium Manager…", "WARN"))
                                msedgedriver = None
                            elif _dm and _em and _dm != _em:
                                self.root.after(0, lambda dm=_dm, em=_em: self.log(
                                    f"EdgeDriver v{dm} ≠ Edge v{em} — skipping cache, downloading v{em}…", "WARN"))
                                msedgedriver = None
                        except Exception:
                            pass
                    if msedgedriver:
                        self.root.after(0, lambda d=msedgedriver: self.log(f"EdgeDriver: {d}"))
                        self.driver = webdriver.Edge(service=EService(msedgedriver), options=o)
                    else:
                        self.root.after(0, lambda: self.log(
                            "msedgedriver not found locally — Selenium Manager will download correct version…", "WARN"))
                        self.driver = webdriver.Edge(options=o)
                # restore saved browser window position/size
                prefs = self._load_prefs()
                bkey = f"{browser.lower()}_browser"
                bpref = prefs.get(bkey, {})
                _rule = PLATFORM_RULES.get(self.platform_var.get(), {})
                if "browser_size" in _rule:
                    w, h = _rule["browser_size"]
                else:
                    w = bpref.get("width", 550)
                    h = bpref.get("height", 450)
                x = bpref.get("x", None)
                y = bpref.get("y", None)
                self.driver.set_window_size(w, h)
                if x is not None and y is not None:
                    self.driver.set_window_position(x, y)
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
            try:
                bkey = f"{self.browser_var.get().lower()}_browser"
                pos  = self.driver.get_window_position()
                size = self.driver.get_window_size()
                self._save_prefs({bkey: {
                    "x": pos["x"], "y": pos["y"],
                    "width": size["width"], "height": size["height"],
                }})
            except Exception:
                pass
            try: self.driver.quit()
            except Exception: pass
            self.driver = None
        self.log("Browser closed.", "WARN")
        self._set_status("Browser closed")

    def _kill_browser(self):
        choice = tk.StringVar(value="cancel")

        dlg = tk.Toplevel(self.root)
        dlg.title("Kill browser")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.transient(self.root)
        self.root.update_idletasks()
        rx = self.root.winfo_x(); ry = self.root.winfo_y()
        rw = self.root.winfo_width(); rh = self.root.winfo_height()
        dlg.update_idletasks()
        dw = dlg.winfo_reqwidth(); dh = dlg.winfo_reqheight()
        dlg.geometry(f"+{rx + (rw - dw)//2}+{ry + (rh - dh)//2}")

        tk.Label(dlg, text="Which browser processes should be killed?",
                 font=("", 10, "bold")).pack(padx=20, pady=(12, 4))
        tk.Label(dlg,
                 text="Force-kills all Chrome or Edge processes\n(browser + driver).",
                 justify="left", foreground="#888888").pack(padx=20, pady=(0, 10))

        bf = tk.Frame(dlg, padx=16, pady=8); bf.pack()

        def pick(val):
            choice.set(val); dlg.destroy()

        tk.Button(bf, text="Kill Chrome", width=14,
                  command=lambda: pick("chrome")).grid(row=0, column=0, padx=4, pady=4)
        tk.Button(bf, text="Kill Edge",   width=14,
                  command=lambda: pick("edge")  ).grid(row=0, column=1, padx=4, pady=4)
        tk.Button(bf, text="Both",        width=14,
                  command=lambda: pick("both")  ).grid(row=0, column=2, padx=4, pady=4)
        tk.Button(bf, text="Cancel",      width=14,
                  command=lambda: pick("cancel")).grid(row=0, column=3, padx=4, pady=4)

        dlg.wait_window()

        val = choice.get()
        if val == "cancel":
            return

        chrome_win = ["chrome.exe", "chromedriver.exe"]
        chrome_mac = ["Google Chrome", "chromedriver"]
        edge_win   = ["msedge.exe", "msedgedriver.exe"]
        edge_mac   = ["Microsoft Edge", "msedgedriver"]

        if val == "chrome":
            killed = self._kill_procs(chrome_win, chrome_mac)
        elif val == "edge":
            killed = self._kill_procs(edge_win, edge_mac)
        else:
            killed = self._kill_procs(chrome_win + edge_win, chrome_mac + edge_mac)

        self.driver = None
        self._set_status("Browser killed")
        if killed:
            self.log(f"Killed: {', '.join(killed)}", "WARN")
        else:
            self.log("Kill Browser: no running processes found.", "WARN")

    def _toggle_mute(self):
        if not self._alive():
            messagebox.showwarning("No browser", "Open browser first."); return
        self._muted = not self._muted
        js = ("document.querySelectorAll('video, audio').forEach(el => el.muted = true);"
              if self._muted else
              "document.querySelectorAll('video, audio').forEach(el => el.muted = false);")
        try:
            self.driver.execute_script(js)
            label = "🔊 Unmute" if self._muted else "🔇 Mute"
            self._mute_btn.config(text=label)
            self.log(f"Browser {'muted' if self._muted else 'unmuted'}.", "WARN")
        except Exception as e:
            self.log(f"Mute error: {e}", "ERROR")

    # ── test ─────────────────────────────────────────────────────────────────
    def test_targets(self):
        if not self._alive():
            messagebox.showwarning("No browser","Open the browser and navigate first."); return
        targets = self._effective_targets()
        if not targets:
            messagebox.showwarning("No targets","Enter at least one selector."); return
        by = self._by()
        self.log("=== TEST ===", "HEAD")
        kw = self.event_kw_var.get().strip() if hasattr(self, "event_kw_var") else ""
        if kw:
            self.log(f"  Event keyword filter: '{kw}'")
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
        targets = self._effective_targets(); by = self._by()
        load_s = self.load_var.get(); delay_s = self.delay_var.get()
        scroll_px = self.scroll_after_var.get()
        if load_s > 0: time.sleep(load_s)
        # scroll BEFORE click when key_press is used (e.g. NBA Docomo)
        if self._key_press and scroll_px > 0:
            self.driver.execute_script(f"document.body.scrollBy(0, {scroll_px})")
            self.log(f"  ↓  scrolled {scroll_px}px before click", "OK")
            time.sleep(0.5)
        ok = 0
        for t in targets:
            try:
                el = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable((by, t)))
                if self._ctrl_click:
                    ActionChains(self.driver).key_down(Keys.CONTROL).click(el).key_up(Keys.CONTROL).perform()
                    self.log(f"  ✓  Ctrl+clicked '{t}'", "OK")
                else:
                    try:
                        el.click()
                    except ElementClickInterceptedException:
                        self.driver.execute_script("arguments[0].click()", el)
                    if self._key_press:
                        time.sleep(0.3)
                        ActionChains(self.driver).send_keys(self._key_press).perform()
                        self.log(f"  ✓  clicked + key '{self._key_press}' on '{t}'", "OK")
                    else:
                        self.log(f"  ✓  clicked '{t}'", "OK")
                ok += 1
                if scroll_px > 0 and not self._key_press:
                    time.sleep(0.5)
                    self.driver.execute_script(f"document.body.scrollBy(0, {scroll_px})")
                    self.log(f"  ↓  scrolled {scroll_px}px", "OK")
            except TimeoutException:
                self.log(f"  ✗  timeout: '{t}'", "WARN")
            except NoSuchElementException:
                self.log(f"  ✗  not found: '{t}'", "WARN")
            except Exception as e:
                self.log(f"  ✗  error '{t}': {e}", "ERROR")
            if delay_s > 0: time.sleep(delay_s)
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
        if not self._video_detect and not self._targets():
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
        self._monitor_start_dt = s_dt
        self._freeze_end_dt = None  # reset so freeze gets fresh +4h on new monitoring session
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        end_str = str(e_dt) if e_dt else "indefinitely"
        self.log(f"Monitoring from {s_dt} → {end_str}", "HEAD")
        self.thread = threading.Thread(target=self._loop,
                                       args=(s_dt, e_dt), daemon=True)
        self.thread.start()

    def stop_monitoring(self, trigger_freeze=False):
        self.running = False
        self.root.after(0, lambda: self.start_btn.config(state="normal"))
        self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
        self.log("Monitoring stopped.", "WARN"); self._set_status("Stopped")
        if trigger_freeze and self.freeze_detect_var.get():
            # keep original end time if freeze was already running (remonitor case)
            if hasattr(self, "_freeze_end_dt") and self._freeze_end_dt:
                freeze_end_dt = self._freeze_end_dt
            else:
                start_dt = getattr(self, "_monitor_start_dt", datetime.datetime.now())
                freeze_end_dt = start_dt + datetime.timedelta(hours=4)
                self._freeze_end_dt = freeze_end_dt
            FREEZE_DELAY = 60
            self.root.after(0, lambda: self._flog(
                f"Freeze Detection will start in {FREEZE_DELAY}s…", "WARN"))
            def _delayed_start(end_dt=freeze_end_dt):
                deadline = time.time() + FREEZE_DELAY
                while time.time() < deadline:
                    if not self._alive():
                        self.root.after(0, lambda: self._flog(
                            "Browser closed before Freeze Detection could start.", "ERROR"))
                        return
                    time.sleep(0.5)
                self.root.after(0, lambda: self.start_freeze_detection(end_dt))
            threading.Thread(target=_delayed_start, daemon=True).start()

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
            # if driver is focused on a closed tab, switch back to first available tab
            # (must happen BEFORE _alive() check, which would otherwise stop monitoring)
            if self.driver:
                try:
                    _ = self.driver.current_url
                except Exception:
                    try:
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        self.root.after(0, lambda: self.log("  ↩  switched back to schedule tab", "WARN"))
                    except Exception:
                        pass  # browser truly closed — _alive() will catch it below
            if not self._alive():
                self.root.after(0, lambda: self.log("Browser closed.", "ERROR"))
                self.root.after(0, self.stop_monitoring); break
            if refresh_first: self._do_refresh()

            # ── VIDEO DETECT MODE (e.g. DAZN) ─────────────────────────────────
            # No click targets — refresh and check if video started playing via JS.
            if self._video_detect:
                self._set_status("Active — watching for video…")
                load_s = self.load_var.get()
                if load_s > 0:
                    self.root.after(0, lambda s=load_s:
                        self.log(f"  ⏱  page-load wait {s}s…"))
                    if not self._sleep(load_s): break
                js = self._video_detect_js
                playing = False
                try:
                    playing = bool(self.driver.execute_script(js))
                except Exception as e:
                    err = str(e)
                    self.root.after(0, lambda e=err: self.log(f"  JS error: {e}", "ERROR"))
                if playing:
                    self.root.after(0, lambda: self.log("  ▶  Video playing — stopping.", "OK"))
                    self.root.after(0, lambda: self.stop_monitoring(trigger_freeze=True))
                    break
                self.root.after(0, lambda: self.log("  —  Video not playing yet…"))
                if refresh_s > 0:
                    self.root.after(0, lambda s=refresh_s:
                        self.log(f"Waiting {s}s before next check…"))
                    if not self._sleep(refresh_s): break
                else:
                    self._sleep(1)
                continue
            # ──────────────────────────────────────────────────────────────────

            self.root.after(0, lambda: self.log("── click cycle ──", "HEAD"))
            handles_before = set(self.driver.window_handles) if self._prevent_new_window else set()
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
                # post-click: try optional targets after page navigates (e.g. popup)
                if self._post_click_targets:
                    self.root.after(0, lambda w=self._post_click_wait:
                        self.log(f"Waiting {w}s for post-click target…"))
                    self._sleep(self._post_click_wait)
                    if self._alive():
                        # switch to new tab/window if one was opened
                        if self._prevent_new_window:
                            try:
                                new_handles = set(self.driver.window_handles) - handles_before
                                if new_handles:
                                    self.driver.switch_to.window(new_handles.pop())
                                    self.root.after(0, lambda: self.log("  →  switched to new tab", "OK"))
                            except Exception:
                                pass
                        # optional second wait after switch (e.g. page needs time to load)
                        if self._post_switch_wait > 0:
                            self.root.after(0, lambda w=self._post_switch_wait:
                                self.log(f"Waiting {w}s for tab to load…"))
                            self._sleep(self._post_switch_wait)
                        by = self._by()
                        for t in self._post_click_targets:
                            try:
                                el = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((by, t)))
                                try:
                                    el.click()
                                except ElementClickInterceptedException:
                                    self.driver.execute_script("arguments[0].click()", el)
                                self.root.after(0, lambda x=t: self.log(f"  ✓  post-click '{x}'", "OK"))
                            except Exception:
                                self.root.after(0, lambda x=t: self.log(f"  —  post-click not found: '{x}'"))
                self.root.after(0, lambda: self.stop_monitoring(trigger_freeze=True)); break
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
