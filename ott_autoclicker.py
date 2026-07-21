#!/usr/bin/env python3
"""OTT AutoClicker – compatible with Python 3.9 / macOS system Tk"""
from __future__ import annotations
import os, sys, platform, time, threading, datetime, subprocess, re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
VERSION = "2.0.11"

UPDATE_VERSION_URL = "https://raw.githubusercontent.com/tampltor13/ott-autoclicker/main/version.txt"
UPDATE_SCRIPT_URL  = "https://raw.githubusercontent.com/tampltor13/ott-autoclicker/main/ott_autoclicker.py"
UPDATE_VBS_URL     = "https://raw.githubusercontent.com/tampltor13/ott-autoclicker/main/run.vbs"
CHANNELS_URL       = "https://raw.githubusercontent.com/tampltor13/ott-autoclicker/main/channels.csv"

PLATFORMS = {
    "Prime Video USA": "https://www.amazon.com/gp/video/sports",
    "Prime Video IT":  "https://www.primevideo.com",
    "Prime Video BR":  "https://www.primevideo.com",
    "Prime Video UK":  "https://www.amazon.co.uk/gp/video/sports",
    "Prime Video DE":  "https://www.amazon.de/gp/video/sports",
    "Prime Video ES":  "https://www.primevideo.com",
    "Prime Video JP":  "https://www.amazon.co.jp/",
    "Prime Video MX": "https://www.primevideo.com",
    "Prime Video FR": "https://www.primevideo.com",
    "DAZN DE":      "https://www.dazn.com/en-DE/home",
    "DAZN ES":      "https://www.dazn.com/en-ES/home",
    "DAZN IT":      "https://www.dazn.com/en-IT",
    "DStv":         "https://dstv.stream/#/livetv/sport",
    "Peacock":      "https://www.peacocktv.com/watch/home",
    "Coupang Play": "https://www.coupangplay.com",
    "SPOTV Now JP": "https://spotvnow.jp/schedule/0",
    "NBA Docomo":  "https://nba.docomo.ne.jp/schedule",
    "Paramount+":  "https://www.paramountplus.com",
    "TOD":         "https://www.tod.tv",
    "Disney+ US":  "https://www.disneyplus.com/home",
    "Disney+ SE":  "https://www.disneyplus.com/home",
    "Disney+ DK":  "https://www.disneyplus.com/home",
    "Disney+ AR":  "https://www.disneyplus.com/en-gb/home",
    "Disney+ BR":  "https://www.disneyplus.com/en-gb/home",
    "FanCode":    "https://www.fancode.com",
    "Tencent":    "https://sports.qq.com/kbsweb/index.htm",
    "Stan":       "https://play.stan.com.au/sport",
    "WOWOW":      "https://wod.wowow.co.jp/live-schedule",
    "ESPN+ US":    "https://www.espn.com/watch/schedule",
    "Viaplay DK":    "https://viaplay.dk/",
    "Victory+":      "https://victoryplus.com/",
    "U-Next":        "https://video.unext.jp/",
    "Dailymotion":   "https://www.dailymotion.com",
    "Teleantillas":  "https://teleantillas.com.do/en-vivo/",
    "Fubo":        "https://www.fubo.tv/",
    "Hotstar":     "https://www.hotstar.com/in/home",
}
# Predefined rules per platform: selector type + click targets (one per line)
PLATFORM_RULES = {
    "Prime Video USA": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
        "scan_offset":     30,
    },
    "Prime Video IT": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
        "scan_offset":     30,
    },
    "Prime Video BR": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
        "scan_offset":     30,
    },
    "Prime Video UK": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
        "scan_offset":     30,
    },
    "Prime Video DE": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
        "scan_offset":     30,
    },
    "Prime Video ES": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
        "scan_offset":     30,
    },
    "Prime Video JP": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
        "scan_offset":     30,
    },
    "Prime Video MX": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
        "scan_offset":     30,
    },
    "Prime Video FR": {
        "selector":        "XPath",
        "targets":         '//*[@data-automation-id="circular-playbutton"]\n//*[@data-testid="play"]',
        "refresh_first":   True,
        "click_delay":     2,
        "freeze_recovery": "remonitor",
        "scan_offset":     30,
    },
    "Peacock": {
        "selector":               "XPath",
        "targets":                '//*[@data-testid="watch-button"]',
        "refresh_first":          True,
        "click_delay":            3,
        "load_wait":              10,
        "scan_offset":            30,
        "freeze_profile_selector": '//div[contains(@class,"profiles__avatar--image") and contains(@aria-label,"Ingrid")]',
        "freeze_live_selector":    '//*[@data-testid="watch-button"]',
    },
    "Coupang Play": {
        "selector":      "XPath",
        "targets":       '//*[@data-cy="playCtaButtonText" and contains(.,"Watch Live Now")]',
        "refresh_first": True,
        "click_delay":   2,
    },
    "SPOTV Now JP": {
        "selector":           "XPath",
        "targets":            '//div[contains(@class,"match-column")]//div[contains(@class,"view-box live")]',
        "pre_click_targets":  '//button[contains(@class,"login-btn")]\n//button[contains(@class,"default") and contains(.,"ログイン")]',
        "pre_click_wait":     5,   # wait between pre-clicks (login form load)
        "pre_click_nav_url":  "https://spotvnow.jp/schedule/0",  # navigate here after pre-clicks
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
        "scan_offset":   10,
    },
    "Paramount+": {
        "selector":      "XPath",
        "targets":       '//article[contains(@class,"live-event")]//a',
        "refresh_first": True,
        "click_delay":   2,
    },
    "Disney+ US": {
        "selector":      "XPath",
        "targets":       '//*[@data-testid="modal-action-button"]\n//*[@data-testid="playback-action-button"]\n//*[@data-testid="live-modal-watch-live-action-button"]',
        "refresh_first": True,
    },
    "Disney+ SE": {
        "selector":      "XPath",
        "targets":       '//*[@data-testid="modal-action-button"]\n//*[@data-testid="playback-action-button"]\n//*[@data-testid="live-modal-watch-live-action-button"]',
        "refresh_first": True,
    },
    "Disney+ DK": {
        "selector":      "XPath",
        "targets":       '//*[@data-testid="modal-action-button"]\n//*[@data-testid="playback-action-button"]\n//*[@data-testid="live-modal-watch-live-action-button"]',
        "refresh_first": True,
    },
    "Disney+ BR": {
        "selector":      "XPath",
        "targets":       '//*[@data-testid="modal-action-button"]\n//*[@data-testid="playback-action-button"]\n//*[@data-testid="live-modal-watch-live-action-button"]',
        "refresh_first": True,
        "click_delay":   2,
        "load_wait":     10,
    },
    "Disney+ AR": {
        "selector":      "XPath",
        "targets":       '//*[@data-testid="modal-action-button"]\n//*[@data-testid="playback-action-button"]\n//*[@data-testid="live-modal-watch-live-action-button"]',
        "refresh_first": True,
        "click_delay":   2,
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
    "DAZN IT": {
        "video_detect":    True,
        "video_detect_js": "const v = document.querySelector('video'); return !!(v && !v.paused && !v.error && v.currentTime > 0 && v.readyState >= 3);",
        "refresh_first":   True,
        "load_wait":       60,
        "freeze_recovery": "refresh_only",
    },
    "DStv": {
        # OLD click mode (keep for reference, re-enable if DStv breaks again):
        # "selector":           "XPath",
        # "targets":            '//button[contains(@class,"PlayerControls_buttonpause")]',
        # "refresh_first":      False,
        # "load_wait":          10,
        # "hover_before_click": True,
        # "freeze_recovery":    "remonitor",
        "video_detect":    True,
        "video_detect_js": "const v = document.querySelector('video'); return !!(v && !v.paused && !v.error && v.currentTime > 0 && v.readyState >= 3);",
        "refresh_first":   True,
        "load_wait":       60,
        "freeze_default":  True,
        "freeze_no_end":   True,
        "freeze_recovery": "refresh_only",
        "freeze_profile_selector": '//img[contains(@class,"Avatar_avatar__jkjO-")]',
    },
    "Tencent": {
        "selector":      "XPath",
        "targets":       "",
        "refresh_first": False,
    },
    "Fubo": {
        "selector":         "XPath",
        "targets":          "",
        "refresh_first":    True,
        "load_wait":        10,
        "post_refresh_key": " ",
    },
    "Stan": {
        "selector":        "XPath",
        "targets":         '//span[contains(@class,"play__label") and text()="Watch Live"]',
        "refresh_first":   True,
        "load_wait":       10,
        "click_delay":     2,
        "force_js_click":  True,
        "dispatch_click":  True,
        "freeze_video_js": "const p = document.querySelector('stan-player'); const v = p && p.shadowRoot && p.shadowRoot.querySelector('video'); return v ? v.currentTime : null;",
        "scan_offset":     15,
    },
    "FanCode": {
        "selector":        "XPath",
        "targets":         "",
        "refresh_first":   True,
        "load_wait":       30,
        "video_detect":    True,
        "video_detect_js": "const v = document.querySelector('video'); return !!(v && !v.error && v.currentTime > 0 && v.readyState >= 3);",
        "video_detect_key": "m",
        "freeze_recovery": "refresh_only",
    },
    "ESPN+ US": {
        "video_detect":      True,
        "video_detect_js":   "return Array.from(document.querySelectorAll('video')).some(v => v.currentTime > 1 && !v.error);",
        "video_detect_key":  "m",
        "refresh_first":     True,
        "load_wait":         15,
        "freeze_recovery":   "refresh_only",
        "scan_offset":       10,
    },
    "Dailymotion": {
        "refresh_first":     False,
        "freeze_recovery":   "refresh_only",
    },
    "Teleantillas": {
        "refresh_first":     False,
        "freeze_recovery":   "refresh_only",
        "freeze_iframe_src": ["dailymotion.com", "geo.dailymotion.com"],
        "freeze_unmute_selector": '//button[@data-testid="tap-to-unmute"]',
    },
    "Viaplay DK": {
        "selector":        "XPath",
        "targets":         '//*[@data-testid="play-button-text"]',
        "refresh_first":   True,
        "load_wait":       10,
        "freeze_recovery": "refresh_only",
        "scan_offset":     30,
    },
    "U-Next": {
        "selector":      "XPath",
        "targets":       '//*[@data-testid="liveTitleDetail-stage-play"]',
        "refresh_first": True,
        "load_wait":     8,
        "scan_offset":   30,
    },
    "Victory+": {
        "video_detect":      True,
        "video_detect_js":   "const v = document.querySelector('video'); return !!(v && !v.paused && !v.error && v.currentTime > 0 && v.readyState >= 3);",
        "refresh_first":     True,
        "load_wait":         15,
        "freeze_recovery":   "refresh_only",
    },
    "WOWOW": {
        "video_detect":       True,
        "video_detect_js":    "const v = document.querySelector('video'); return !!(v && !v.paused && !v.error && v.currentTime > 0 && v.readyState >= 3);",
        "refresh_first":      True,
        "load_wait":          60,
        "freeze_recovery":    "refresh_only",
        "freeze_live_selector": '//a[contains(@class,"btn-fill") and contains(.,"ライブを再生")]',
        "scan_offset":        30,
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
LOG_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs.txt")

# ── Pre-check email config (loaded from smtp_config.txt) ─────────────────────
PRECHECK_SMTP_HOST = ""
PRECHECK_SMTP_PORT = 587
PRECHECK_SMTP_USER = ""
PRECHECK_SMTP_PASS = ""
PRECHECK_MAIL_FROM = ""
PRECHECK_MAIL_TO   = ""

def _load_smtp_config():
    global PRECHECK_SMTP_HOST, PRECHECK_SMTP_PORT, PRECHECK_SMTP_USER
    global PRECHECK_SMTP_PASS, PRECHECK_MAIL_FROM, PRECHECK_MAIL_TO
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smtp_config.txt")
    if not os.path.exists(config_path):
        return
    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip(); val = val.strip()
            if key == "SMTP_HOST":   PRECHECK_SMTP_HOST = val
            elif key == "SMTP_PORT": PRECHECK_SMTP_PORT = int(val)
            elif key == "SMTP_USER": PRECHECK_SMTP_USER = val
            elif key == "SMTP_PASS": PRECHECK_SMTP_PASS = val
            elif key == "MAIL_FROM": PRECHECK_MAIL_FROM = val
            elif key == "MAIL_TO":   PRECHECK_MAIL_TO   = val

_load_smtp_config()
# ─────────────────────────────────────────────────────────────────────────────

# ── Per-platform required VPN country (ISO 3166-1 alpha-2) ───────────────────
# If platform is in this dict, pre-check will verify browser IP matches country.
PLATFORM_VPN_COUNTRY = {
    "Prime Video USA": "US",
    "ESPN+ US":        "US",
    "Victory+":        "US",
    "Peacock":         "US",
    "Prime Video IT":  "IT",
    "Prime Video BR":  "BR",
    "Prime Video UK":  "GB",
    "Prime Video DE":  "DE",
    "Prime Video ES":  "ES",
    "Prime Video JP":  "JP",
    "Prime Video MX":  "MX",
    "Prime Video FR":  "FR",
    "Viaplay DK":      "HR",   # no VPN needed — direct HR IP is expected and OK
}
# ─────────────────────────────────────────────────────────────────────────────
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


class TimePickerWidget(ttk.Frame):
    """HH:MM time picker — click hours or minutes to select, arrows to change.

    Compatible with existing .get() / .set() usage via self.var (StringVar, "HH:MM" or "").
    Supports empty value (for optional end-time fields) via allow_empty=True.
    """

    def __init__(self, parent, var: tk.StringVar, allow_empty: bool = False, **kwargs):
        super().__init__(parent, **kwargs)
        self.var         = var
        self.allow_empty = allow_empty
        self._updating   = False

        # internal vars for the two entry boxes
        self._hvar = tk.StringVar()
        self._mvar = tk.StringVar()

        # sync internal vars from external var
        self._sync_from_var()
        # whenever external var changes (e.g. .set() calls), sync inward
        self.var.trace_add("write", self._on_var_write)

        # ── build widgets ────────────────────────────────────────────────────
        vcmd_h = (self.register(lambda s: len(s) <= 2 and (s == "" or s.isdigit())), "%P")
        vcmd_m = (self.register(lambda s: len(s) <= 2 and (s == "" or s.isdigit())), "%P")

        self._h_entry = ttk.Entry(self, textvariable=self._hvar, width=3,
                                  justify="center", validate="key",
                                  validatecommand=vcmd_h)
        self._sep = ttk.Label(self, text=":")
        self._m_entry = ttk.Entry(self, textvariable=self._mvar, width=3,
                                  justify="center", validate="key",
                                  validatecommand=vcmd_m)

        self._h_entry.pack(side="left")
        self._sep.pack(side="left", padx=1)
        self._m_entry.pack(side="left")

        # ── bindings ─────────────────────────────────────────────────────────
        for entry, is_hour in ((self._h_entry, True), (self._m_entry, False)):
            entry.bind("<Up>",       lambda e, h=is_hour: self._step(h, +1))
            entry.bind("<Down>",     lambda e, h=is_hour: self._step(h, -1))
            entry.bind("<FocusIn>",  lambda e: e.widget.select_range(0, "end"))
            entry.bind("<FocusOut>", lambda e, h=is_hour: self._on_focus_out(h))
            entry.bind("<KeyRelease>", lambda e, h=is_hour: self._on_key(e, h))

        # click on ":" label focuses hours
        self._sep.bind("<Button-1>", lambda e: self._h_entry.focus_set())

    # ── internal helpers ──────────────────────────────────────────────────────

    def _sync_from_var(self):
        """Push external var value → internal _hvar/_mvar."""
        val = self.var.get().strip()
        if val and ":" in val:
            parts = val.split(":")
            self._hvar.set(parts[0].zfill(2))
            self._mvar.set(parts[1][:2].zfill(2))
        else:
            self._hvar.set("")
            self._mvar.set("")

    def _sync_to_var(self):
        """Push internal _hvar/_mvar → external var."""
        h = self._hvar.get().strip()
        m = self._mvar.get().strip()
        if h == "" and m == "" and self.allow_empty:
            self._updating = True
            self.var.set("")
            self._updating = False
        elif h.isdigit() and m.isdigit():
            self._updating = True
            self.var.set(f"{int(h):02d}:{int(m):02d}")
            self._updating = False

    def _on_var_write(self, *_):
        """External .set() called — update internal entries."""
        if not self._updating:
            self._sync_from_var()

    def _on_focus_out(self, is_hour: bool):
        """Validate and zero-pad on focus out."""
        if is_hour:
            val = self._hvar.get().strip()
            if val.isdigit():
                v = max(0, min(23, int(val)))
                self._hvar.set(f"{v:02d}")
            elif val == "" and self.allow_empty:
                self._mvar.set("")
        else:
            val = self._mvar.get().strip()
            if val.isdigit():
                v = max(0, min(59, int(val)))
                self._mvar.set(f"{v:02d}")
        self._sync_to_var()

    def _on_key(self, event, is_hour: bool):
        """Auto-jump to minutes after 2 digits in hours field."""
        if is_hour:
            val = self._hvar.get().strip()
            if len(val) == 2 and val.isdigit():
                # clamp immediately
                v = max(0, min(23, int(val)))
                self._hvar.set(f"{v:02d}")
                self._m_entry.focus_set()
                self._m_entry.select_range(0, "end")
        self._sync_to_var()

    def _step(self, is_hour: bool, delta: int):
        """Arrow key — increment/decrement with wraparound."""
        if is_hour:
            val = self._hvar.get().strip()
            cur = int(val) if val.isdigit() else 0
            new = (cur + delta) % 24
            self._hvar.set(f"{new:02d}")
        else:
            val = self._mvar.get().strip()
            cur = int(val) if val.isdigit() else 0
            new = (cur + delta) % 60
            self._mvar.set(f"{new:02d}")
        self._sync_to_var()
        return "break"  # prevent default tkinter behaviour

    # ── public API ────────────────────────────────────────────────────────────

    def get(self) -> str:
        """Return current value as 'HH:MM' or '' if empty."""
        return self.var.get()

    def set(self, value: str):
        """Set value — delegates to var which triggers _on_var_write."""
        self.var.set(value)


class DatePickerWidget(ttk.Frame):
    """DD-MM date picker — arrows change day/month, internally stores YYYY-MM-DD.

    var (StringVar) holds the full "YYYY-MM-DD" string used by _parse_dt.
    Visually shows only DD-MM. allow_empty=True supports optional end-date fields.
    """

    def __init__(self, parent, var: tk.StringVar, allow_empty: bool = False, **kwargs):
        super().__init__(parent, **kwargs)
        self.var         = var
        self.allow_empty = allow_empty
        self._updating   = False

        self._dvar = tk.StringVar()
        self._mvar = tk.StringVar()

        self._sync_from_var()
        self.var.trace_add("write", self._on_var_write)

        vcmd = (self.register(lambda s: len(s) <= 2 and (s == "" or s.isdigit())), "%P")

        self._d_entry = ttk.Entry(self, textvariable=self._dvar, width=3,
                                  justify="center", validate="key", validatecommand=vcmd)
        self._sep = ttk.Label(self, text="-")
        self._m_entry = ttk.Entry(self, textvariable=self._mvar, width=3,
                                  justify="center", validate="key", validatecommand=vcmd)

        self._d_entry.pack(side="left")
        self._sep.pack(side="left", padx=1)
        self._m_entry.pack(side="left")

        for entry, is_day in ((self._d_entry, True), (self._m_entry, False)):
            entry.bind("<Up>",        lambda e, d=is_day: self._step(d, +1))
            entry.bind("<Down>",      lambda e, d=is_day: self._step(d, -1))
            entry.bind("<FocusIn>",   lambda e: e.widget.select_range(0, "end"))
            entry.bind("<FocusOut>",  lambda e, d=is_day: self._on_focus_out(d))
            entry.bind("<KeyRelease>", lambda e, d=is_day: self._on_key(e, d))

        self._sep.bind("<Button-1>", lambda e: self._d_entry.focus_set())

    def _year(self) -> int:
        raw = self.var.get().strip()
        if raw and len(raw) >= 4:
            try:
                return int(raw[:4])
            except ValueError:
                pass
        return datetime.datetime.now().year

    def _max_day(self, month: int, year: int) -> int:
        import calendar
        return calendar.monthrange(year, month)[1]

    def _sync_from_var(self):
        raw = self.var.get().strip()
        if raw and len(raw) == 10:
            try:
                d = datetime.datetime.strptime(raw, "%Y-%m-%d")
                self._dvar.set(f"{d.day:02d}")
                self._mvar.set(f"{d.month:02d}")
                return
            except ValueError:
                pass
        self._dvar.set("")
        self._mvar.set("")

    def _sync_to_var(self):
        d = self._dvar.get().strip()
        m = self._mvar.get().strip()
        if d == "" and m == "" and self.allow_empty:
            self._updating = True
            self.var.set("")
            self._updating = False
        elif d.isdigit() and m.isdigit():
            year  = self._year()
            month = max(1, min(12, int(m)))
            day   = max(1, min(self._max_day(month, year), int(d)))
            self._updating = True
            self.var.set(f"{year:04d}-{month:02d}-{day:02d}")
            self._updating = False

    def _on_var_write(self, *_):
        if not self._updating:
            self._sync_from_var()

    def _on_focus_out(self, is_day: bool):
        if is_day:
            val = self._dvar.get().strip()
            if val.isdigit():
                year  = self._year()
                month = int(self._mvar.get()) if self._mvar.get().strip().isdigit() else 1
                self._dvar.set(f"{max(1, min(self._max_day(month, year), int(val))):02d}")
            elif val == "" and self.allow_empty:
                self._mvar.set("")
        else:
            val = self._mvar.get().strip()
            if val.isdigit():
                self._mvar.set(f"{max(1, min(12, int(val))):02d}")
        self._sync_to_var()

    def _on_key(self, event, is_day: bool):
        if is_day:
            val = self._dvar.get().strip()
            if len(val) == 2 and val.isdigit():
                year  = self._year()
                month = int(self._mvar.get()) if self._mvar.get().strip().isdigit() else 1
                v = max(1, min(self._max_day(month, year), int(val)))
                self._dvar.set(f"{v:02d}")
                self._m_entry.focus_set()
                self._m_entry.select_range(0, "end")
        self._sync_to_var()

    def _step(self, is_day: bool, delta: int):
        year = self._year()
        if is_day:
            val   = self._dvar.get().strip()
            month = int(self._mvar.get()) if self._mvar.get().strip().isdigit() else 1
            cur   = int(val) if val.isdigit() else 1
            maxd  = self._max_day(month, year)
            new   = (cur - 1 + delta) % maxd + 1
            self._dvar.set(f"{new:02d}")
        else:
            val = self._mvar.get().strip()
            cur = int(val) if val.isdigit() else 1
            new = (cur - 1 + delta) % 12 + 1
            self._mvar.set(f"{new:02d}")
        self._sync_to_var()
        return "break"

    def get(self) -> str:
        return self.var.get()

    def set(self, value: str):
        self.var.set(value)


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
        self._compact_btn = ttk.Button(self._status_bar, text="Compact",
                                       command=self._toggle_compact)
        self._compact_btn.pack(side="right", padx=4, pady=5)
        self._advanced_mode = False
        self._adv_btn = ttk.Button(self._status_bar, text="Advanced",
                                   command=self._toggle_advanced)
        self._adv_btn.pack(side="right", padx=(4, 0), pady=5)
        ttk.Label(self._status_bar, textvariable=self.status_var).pack(
            anchor="w", padx=6, pady=6, side="left")

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=6, pady=6)

        t1 = ttk.Frame(self.nb); self.nb.add(t1, text="  Setup  ")
        t2 = ttk.Frame(self.nb); self.nb.add(t2, text="  Monitor  ")
        t_freeze = ttk.Frame(self.nb); self.nb.add(t_freeze, text="  Freeze  ")
        t3 = ttk.Frame(self.nb); self.nb.add(t3, text="  Inspector  ")
        t4 = ttk.Frame(self.nb); self.nb.add(t4, text="  Channels  ")
        self._tab_inspector = t3
        self._tab_channels  = t4
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
        # Scrollable container so Advanced mode content isn't clipped
        _canvas = tk.Canvas(parent, highlightthickness=0)
        _vsb = ttk.Scrollbar(parent, orient="vertical", command=_canvas.yview)
        _canvas.configure(yscrollcommand=_vsb.set)
        _vsb.pack(side="right", fill="y")
        _canvas.pack(side="left", fill="both", expand=True)

        p = ttk.Frame(_canvas, padding=12)
        _cwin = _canvas.create_window((0, 0), window=p, anchor="nw")

        def _on_frame_configure(e):
            _canvas.configure(scrollregion=_canvas.bbox("all"))
        def _on_canvas_configure(e):
            _canvas.itemconfig(_cwin, width=e.width)
        def _on_mousewheel(e):
            _canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        p.bind("<Configure>", _on_frame_configure)
        _canvas.bind("<Configure>", _on_canvas_configure)
        _canvas.bind("<MouseWheel>", _on_mousewheel)
        p.bind_all("<MouseWheel>", _on_mousewheel)

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
        # browser radio buttons
        ttk.Label(p, text="Browser:").grid(row=r, column=0, sticky="w", pady=3)
        self.browser_var = tk.StringVar(value="Chrome")
        f_br = ttk.Frame(p); f_br.grid(row=r, column=1, columnspan=3, sticky="w", padx=8)
        ttk.Radiobutton(f_br, text="Chrome", variable=self.browser_var, value="Chrome").pack(side="left")
        ttk.Radiobutton(f_br, text="Edge",   variable=self.browser_var, value="Edge"  ).pack(side="left", padx=(12, 0))
        r += 1

        ttk.Label(p, text="Platform:").grid(row=r, column=0, sticky="w", pady=3)
        self.platform_var = tk.StringVar(value="")
        cb = ttk.Combobox(p, textvariable=self.platform_var,
                          values=list(PLATFORMS.keys()), state="readonly", width=22, height=20)
        cb.grid(row=r, column=1, columnspan=3, sticky="w", padx=8)
        cb.bind("<<ComboboxSelected>>", self._platform_changed)
        cb.bind("<MouseWheel>", lambda e: "break"); r += 1

        # url
        ttk.Label(p, text="URL:").grid(row=r, column=0, sticky="w", pady=3)
        self.url_var = tk.StringVar(value="")
        ttk.Entry(p, textvariable=self.url_var, width=50).grid(
            row=r, column=1, columnspan=3, sticky="ew", padx=8); r += 1

        # browser size dropdown (advanced only)
        _lbs = ttk.Label(p, text="Browser size:"); _lbs.grid(row=r, column=0, sticky="w", pady=3)
        self.browser_size_var = tk.StringVar(value="SM — 550×450")
        _cbs = ttk.Combobox(p, textvariable=self.browser_size_var,
                     values=["SM — 550×450", "MD — 650×550", "LG — 750×650"],
                     state="readonly", width=16)
        _cbs.grid(row=r, column=1, sticky="w", padx=8)
        _cbs.bind("<MouseWheel>", lambda e: "break")
        self.browser_size_var.trace_add("write", self._on_browser_size_changed)
        self._adv_widgets = [(_lbs, "grid"), (_cbs, "grid")]
        r += 1

        # buttons — row 1
        bf = ttk.Frame(p); bf.grid(row=r, column=0, columnspan=4,
                                    sticky="w", pady=(4,0)); r += 1
        ttk.Button(bf, text="Open Browser",  command=self.open_browser  ).pack(side="left", padx=(0,4))
        ttk.Button(bf, text="Navigate",      command=self.navigate      ).pack(side="left", padx=(0,4))
        ttk.Button(bf, text="Close Browser", command=self.close_browser ).pack(side="left", padx=(0,4))
        self._muted = False
        self._mute_btn = ttk.Button(bf, text="🔇 Mute", command=self._toggle_mute)
        self._mute_btn.pack(side="left", padx=(0,4))
        # buttons — row 2
        bf2 = ttk.Frame(p); bf2.grid(row=r, column=0, columnspan=4,
                                      sticky="w", pady=(2,8)); r += 1
        self._adv_reposition_btn = ttk.Button(bf2, text="Reposition", command=self._reposition_browser)
        self._adv_reposition_btn.pack(side="left", padx=(0,4))
        self._adv_widgets.append((self._adv_reposition_btn, "pack"))
        self._adv_kill_btn = ttk.Button(bf2, text="Kill Browser", command=self._kill_browser)
        self._adv_kill_btn.pack(side="left", padx=(0,4))
        self._adv_widgets.append((self._adv_kill_btn, "pack"))
        self._adv_test_btn = ttk.Button(bf2, text="Test Target", command=self.test_targets)
        self._adv_test_btn.pack(side="left")
        self._adv_widgets.append((self._adv_test_btn, "pack"))

        _sep1 = ttk.Separator(p, orient="horizontal")
        _sep1.grid(row=r, column=0, columnspan=4, sticky="ew", pady=4)
        self._adv_widgets.append((_sep1, "grid")); r += 1

        # click targets
        _lct = ttk.Label(p, text="Click targets (one per line):")
        _lct.grid(row=r, column=0, columnspan=4, sticky="w", pady=(6,2))
        self._adv_widgets.append((_lct, "grid")); r += 1
        self.targets_text = scrolledtext.ScrolledText(p, width=44, height=3,
                                                       font=MONO_FONT)
        self.targets_text.grid(row=r, column=0, columnspan=4, sticky="ew")
        self._adv_widgets.append((self.targets_text, "grid"))
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
        self._post_refresh_key   = ""
        self._pre_click_targets  = []
        self._pre_click_wait     = 3
        self._pre_click_nav_url  = ""
        self._post_click_targets = []
        self._post_click_wait    = 3
        self._post_switch_wait   = 0
        self._prevent_new_window = False
        self._force_js_click     = False
        self._dispatch_click     = False
        self._ctrl_click         = False
        self._hover_before_click = False
        self._video_detect       = False
        self._video_detect_js    = ""
        self._video_detect_key   = ""
        self._freeze_video_js    = ""
        self._freeze_recovery    = "refresh_only"
        self._freeze_profile_selector = ""
        self._freeze_live_selector    = ""
        self._freeze_iframe_src       = ""
        self._freeze_unmute_selector  = ""
        r += 1

        # selector type
        _lsel = ttk.Label(p, text="Selector:"); _lsel.grid(row=r, column=0, sticky="w", pady=3)
        self.sel_var = tk.StringVar(value="Class Name")
        sf = ttk.Frame(p); sf.grid(row=r, column=1, columnspan=3, sticky="w", padx=8)
        for s in SELECTOR_LABELS:
            ttk.Radiobutton(sf, text=s, variable=self.sel_var,
                            value=s).pack(side="left", padx=2); r += 1
        self._adv_widgets += [(_lsel, "grid"), (sf, "grid")]

        # divider
        _sep2 = ttk.Separator(p, orient="horizontal")
        _sep2.grid(row=r, column=0, columnspan=4, sticky="ew", pady=6)
        self._adv_widgets.append((_sep2, "grid")); r += 1

        # delays
        _ldelay = ttk.Label(p, text="Click delay (s):"); _ldelay.grid(row=r, column=0, sticky="w", pady=3)
        self.delay_var = tk.IntVar(value=1)
        f_delay = ttk.Frame(p); f_delay.grid(row=r, column=1, sticky="w", padx=8)
        tk.Spinbox(f_delay, from_=0, to=300, textvariable=self.delay_var,
                   width=8, bg="#3c3c3c", fg="#ffffff",
                   buttonbackground="#555555", insertbackground="#ffffff").pack(side="left")
        i1 = ttk.Label(f_delay, text=" ⓘ", foreground="#888888", cursor="hand2")
        i1.pack(side="left")
        Tooltip(i1, "Pause between clicks when you have multiple targets.\n"
                    "e.g. 2 = waits 2s between each click.")

        _lload = ttk.Label(p, text="Page-load wait (s):"); _lload.grid(row=r, column=2, sticky="w")
        self.load_var = tk.IntVar(value=5)
        f_load = ttk.Frame(p); f_load.grid(row=r, column=3, sticky="w")
        tk.Spinbox(f_load, from_=0, to=60, textvariable=self.load_var,
                   width=6, bg="#3c3c3c", fg="#ffffff",
                   buttonbackground="#555555", insertbackground="#ffffff").pack(side="left")
        i2 = ttk.Label(f_load, text=" ⓘ", foreground="#888888", cursor="hand2")
        i2.pack(side="left")
        Tooltip(i2, "Seconds to wait after refresh before looking for the element.\n"
                    "Gives the page time to load.\n"
                    "Increase if your internet is slow.")
        self._adv_widgets += [(_ldelay, "grid"), (f_delay, "grid"), (_lload, "grid"), (f_load, "grid")]
        r += 1

        # refresh
        _lref = ttk.Label(p, text="Refresh every (s):"); _lref.grid(row=r, column=0, sticky="w", pady=3)
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
                    "If unchecked: looks for the button first, refreshes at end of cycle.")
        self._adv_widgets += [(_lref, "grid"), (f_refresh, "grid"), (f_rf, "grid")]
        r += 1

        # scroll after click + freeze detection (same row, left/right columns)
        _lscroll = ttk.Label(p, text="Scroll after click (px):"); _lscroll.grid(row=r, column=0, sticky="w", pady=3)
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
                      "Runs for 4 hours from monitoring start time.")
        self._adv_widgets += [(_lscroll, "grid"), (f_scroll, "grid"), (f_fd, "grid")]
        r += 1

        # scan offset
        _lscan = ttk.Label(p, text="Scan time offset (min):"); _lscan.grid(row=r, column=0, sticky="w", pady=3)
        self.scan_offset_var = tk.IntVar(value=60)
        f_scan = ttk.Frame(p); f_scan.grid(row=r, column=1, sticky="w", padx=8)
        tk.Spinbox(f_scan, from_=0, to=480, textvariable=self.scan_offset_var,
                   width=8, bg="#3c3c3c", fg="#ffffff",
                   buttonbackground="#555555", insertbackground="#ffffff").pack(side="left")
        i_scan = ttk.Label(f_scan, text=" ⓘ", foreground="#888888", cursor="hand2")
        i_scan.pack(side="left")
        Tooltip(i_scan, "Minutes to subtract from the scanned time.\n"
                        "e.g. if the page shows 08:45 and offset is 60,\n"
                        "Start time will be set to 07:45.\n"
                        "Set to 0 to use the exact time found on the page.")
        self._adv_widgets += [(_lscan, "grid"), (f_scan, "grid")]
        r += 1

        p.columnconfigure(1, weight=1)
        p.columnconfigure(3, weight=1)
        self._advanced_mode = True   # trick toggle into going simple on first call
        self._toggle_advanced()      # start in simple mode — must be after all widgets are created

    # ── MONITOR TAB ──────────────────────────────────────────────────────────
    def _monitor_tab(self, parent):
        p = ttk.Frame(parent, padding=12)
        p.pack(fill="both", expand=True)

        now = datetime.datetime.now()
        r = 0

        gm = ttk.Frame(p); gm.grid(row=r, column=0, columnspan=4, sticky="w"); r += 1

        ttk.Label(gm, text="Start date:").grid(row=0, column=0, sticky="w", pady=3)
        self.start_date = tk.StringVar(value=now.strftime("%Y-%m-%d"))
        sd_frame = ttk.Frame(gm); sd_frame.grid(row=0, column=1, sticky="w", padx=8)
        DatePickerWidget(sd_frame, self.start_date).pack(side="left")
        ttk.Button(sd_frame, text="+", width=2,
                   command=lambda: self._shift_date(self.start_date, +1)).pack(side="left", padx=(3, 0))
        ttk.Label(gm, text="Time (HH:MM):").grid(row=0, column=2, sticky="w")
        st_frame = ttk.Frame(gm); st_frame.grid(row=0, column=3, sticky="w", padx=8)
        self.start_time = tk.StringVar(value=now.strftime("%H:%M"))
        TimePickerWidget(st_frame, self.start_time).pack(side="left")
        ttk.Button(st_frame, text="Now", width=6,
                   command=self._set_start_now).pack(side="left", padx=(4, 0))

        ttk.Label(gm, text="End date:").grid(row=1, column=0, sticky="w", pady=3)
        self.end_date = tk.StringVar(value="")
        ed_frame = ttk.Frame(gm); ed_frame.grid(row=1, column=1, sticky="w", padx=8)
        DatePickerWidget(ed_frame, self.end_date, allow_empty=True).pack(side="left")
        ttk.Button(ed_frame, text="+", width=2,
                   command=lambda: self._shift_date(self.end_date, +1)).pack(side="left", padx=(3, 0))
        ttk.Label(gm, text="Time (HH:MM):").grid(row=1, column=2, sticky="w")
        et_frame = ttk.Frame(gm); et_frame.grid(row=1, column=3, sticky="w", padx=8)
        self.end_time = tk.StringVar(value="")
        TimePickerWidget(et_frame, self.end_time, allow_empty=True).pack(side="left")
        ttk.Button(et_frame, text="Scan", width=6,
                   command=self._scan_time).pack(side="left", padx=(4, 0))

        ttk.Separator(p, orient="horizontal").grid(
            row=r, column=0, columnspan=4, sticky="ew", pady=6); r += 1

        bf = ttk.Frame(p); bf.grid(row=r, column=0, columnspan=4, sticky="ew"); r += 1
        self._monitor_status_var = tk.StringVar(value="Monitoring inactive")
        ttk.Label(bf, textvariable=self._monitor_status_var,
                  foreground="#f0c040").pack(side="left", padx=(0, 12))
        self.stop_btn = ttk.Button(bf, text="■  Stop Monitoring",
                                   command=self.stop_monitoring, state="disabled")
        self.stop_btn.pack(side="right")
        self.start_btn = ttk.Button(bf, text="▶  Start Monitoring",
                                    command=self.start_monitoring)
        self.start_btn.pack(side="right", padx=(0, 6))

        ttk.Separator(p, orient="horizontal").grid(
            row=r, column=0, columnspan=4, sticky="ew", pady=6); r += 1
        self.log_box = scrolledtext.ScrolledText(p, width=58, height=16,
                                                  state="disabled", font=MONO_FONT)
        self.log_box.grid(row=r, column=0, columnspan=4, sticky="nsew")
        self.log_box.tag_config("OK",       foreground="green")
        self.log_box.tag_config("WARN",     foreground="darkorange")
        self.log_box.tag_config("ERROR",    foreground="red")
        self.log_box.tag_config("HEAD",     foreground="purple")
        self.log_box.tag_config("PRECHECK", foreground="#4fc3f7"); r += 1

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
        gf = ttk.Frame(p); gf.pack(fill="x")
        now = datetime.datetime.now()

        ttk.Label(gf, text="Start date:").grid(row=0, column=0, sticky="w", pady=3)
        self._freeze_start_date = tk.StringVar(value=now.strftime("%Y-%m-%d"))
        fsd_frame = ttk.Frame(gf); fsd_frame.grid(row=0, column=1, sticky="w", padx=8)
        DatePickerWidget(fsd_frame, self._freeze_start_date).pack(side="left")
        ttk.Button(fsd_frame, text="+", width=2,
                   command=lambda: self._shift_date(self._freeze_start_date, +1)).pack(side="left", padx=(3, 0))
        ttk.Label(gf, text="Time (HH:MM):").grid(row=0, column=2, sticky="w")
        self._freeze_start_time = tk.StringVar(value=now.strftime("%H:%M"))
        fst_frame = ttk.Frame(gf); fst_frame.grid(row=0, column=3, sticky="w", padx=8)
        TimePickerWidget(fst_frame, self._freeze_start_time).pack(side="left")
        ttk.Button(fst_frame, text="Now", width=6,
                   command=self._set_freeze_start_now).pack(side="left", padx=(4, 0))

        ttk.Label(gf, text="End date:").grid(row=1, column=0, sticky="w", pady=3)
        self._freeze_end_date = tk.StringVar(value="")
        fed_frame = ttk.Frame(gf); fed_frame.grid(row=1, column=1, sticky="w", padx=8)
        DatePickerWidget(fed_frame, self._freeze_end_date, allow_empty=True).pack(side="left")
        ttk.Button(fed_frame, text="+", width=2,
                   command=lambda: self._shift_date(self._freeze_end_date, +1)).pack(side="left", padx=(3, 0))
        ttk.Label(gf, text="Time (HH:MM):").grid(row=1, column=2, sticky="w")
        self._freeze_end_time = tk.StringVar(value="")
        TimePickerWidget(gf, self._freeze_end_time, allow_empty=True).grid(row=1, column=3, sticky="w", padx=8)

        ttk.Separator(p, orient="horizontal").pack(fill="x", pady=6)

        # status + buttons
        bf = ttk.Frame(p); bf.pack(fill="x")
        self._freeze_status_var = tk.StringVar(value="AntiFreeze inactive")
        ttk.Label(bf, textvariable=self._freeze_status_var,
                  foreground="#4fc3f7").pack(side="left")
        self._freeze_stop_btn = ttk.Button(bf, text="■  Stop AntiFreeze",
                                           command=self.stop_freeze_detection,
                                           state="disabled")
        self._freeze_stop_btn.pack(side="right")
        self._freeze_start_btn = ttk.Button(bf, text="▶  Start AntiFreeze",
                                            command=self._manual_start_freeze)
        self._freeze_start_btn.pack(side="right", padx=(0, 6))

        ttk.Separator(p, orient="horizontal").pack(fill="x", pady=6)

        # log box
        self._freeze_box = scrolledtext.ScrolledText(p, width=58, height=20,
                                                      state="disabled", font=MONO_FONT)
        self._freeze_box.pack(fill="both", expand=True)
        self._freeze_box.tag_config("OK",    foreground="green")
        self._freeze_box.tag_config("WARN",  foreground="darkorange")
        self._freeze_box.tag_config("ERROR", foreground="red")
        self._freeze_box.tag_config("HEAD",  foreground="purple")

        ttk.Button(p, text="Clear log",
                   command=self._clear_freeze_log).pack(side="right", pady=(4, 0))

        # state
        self._freeze_running = False
        self._freeze_thread  = None

    def _flog(self, msg, level="INFO"):
        now = datetime.datetime.now()
        ts  = now.strftime("%d-%m %H:%M:%S")
        self._freeze_box.config(state="normal")
        self._freeze_box.insert("end", f"[{ts}] {msg}\n", level)
        self._freeze_box.see("end")
        self._freeze_box.config(state="disabled")
        # append to log file
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[FREEZE] [{ts}] {msg}\n")
        except Exception:
            pass

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
            # if fields are empty and end_dt was not provided (None), stay None (indefinite)
            # if fields are empty and end_dt was provided (e.g. now+4h from monitoring), keep it
        except Exception:
            pass  # keep auto-calculated end_dt
        self._freeze_running = True
        # populate start/end fields
        start_now = datetime.datetime.now()
        self.root.after(0, lambda: self._freeze_start_date.set(start_now.strftime("%Y-%m-%d")))
        self.root.after(0, lambda: self._freeze_start_time.set(start_now.strftime("%H:%M")))
        if end_dt is not None:
            self.root.after(0, lambda: self._freeze_end_date.set(end_dt.strftime("%Y-%m-%d")))
            self.root.after(0, lambda: self._freeze_end_time.set(end_dt.strftime("%H:%M")))
        self.root.after(0, lambda: self._freeze_stop_btn.config(state="normal"))
        self.root.after(0, lambda: self._freeze_start_btn.config(state="disabled"))
        self.root.after(0, lambda: self._freeze_status_var.set("AntiFreeze active…"))
        self._set_status("AntiFreeze active")
        self._freeze_thread = threading.Thread(
            target=self._freeze_loop, args=(end_dt,), daemon=True)
        self._freeze_thread.start()

    def stop_freeze_detection(self):
        self._freeze_running = False
        self.root.after(0, lambda: self._freeze_stop_btn.config(state="disabled"))
        self.root.after(0, lambda: self._freeze_start_btn.config(state="normal"))
        self.root.after(0, lambda: self._freeze_status_var.set("AntiFreeze inactive"))
        self.root.after(0, lambda: self._flog("Freeze Detection stopped.", "WARN"))
        self._set_status("Idle")

    def _manual_start_freeze(self):
        """Start AntiFreeze manually, without going through monitoring."""
        if self._freeze_running:
            return
        if not self._alive():
            messagebox.showwarning("No browser", "Open browser first.")
            return
        # calculate end_dt: use end fields if filled, None if empty (indefinite)
        try:
            d = self._freeze_end_date.get().strip()
            t = self._freeze_end_time.get().strip()
            if d and t:
                end_dt = self._parse_dt(d, t)
            else:
                end_dt = None  # no end time — run indefinitely
        except Exception:
            end_dt = None
        self._freeze_end_dt = end_dt
        self._freeze_start_btn.config(state="disabled")
        MANUAL_DELAY = 30
        self._flog(f"Freeze Detection will start in {MANUAL_DELAY}s…", "WARN")
        def _delayed_manual(end_dt=end_dt):
            deadline = time.time() + MANUAL_DELAY
            while time.time() < deadline:
                if not self._alive():
                    self.root.after(0, lambda: self._flog(
                        "Browser closed before Freeze Detection could start.", "ERROR"))
                    self.root.after(0, lambda: self._freeze_start_btn.config(state="normal"))
                    return
                time.sleep(0.5)
            self.root.after(0, lambda: self.start_freeze_detection(end_dt))
        threading.Thread(target=_delayed_manual, daemon=True).start()

    def _freeze_loop(self, end_dt):
        CHECK_INTERVAL   = 30   # seconds between checks
        REFRESH_WAIT     = 60   # seconds to wait after refresh before re-checking
        MAX_ZERO_RETRIES = 3    # stop after this many consecutive zero-baseline cycles

        end_label = end_dt.strftime("%H:%M") if end_dt else "∞ (no end time)"
        self.root.after(0, lambda: self._flog(
            f"── Freeze Detection started (runs until {end_label}) ──", "HEAD"))

        prev_time        = None
        zero_retry_count = 0    # counts consecutive cycles where baseline was 0.0
        consec_zero_recovery = 0  # counts consecutive freeze recoveries where currentTime stayed 0.0

        while self._freeze_running:
            # check end time (skip if indefinite)
            if end_dt is not None and datetime.datetime.now() >= end_dt:
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

            # check for browser crash/error page (OOM, net error, etc.)
            try:
                cur_url = self.driver.current_url or ""
                if cur_url.startswith(("chrome-error://", "edge://crashedtab",
                                       "about:neterror", "chrome://crashedtab")):
                    self.root.after(0, lambda u=cur_url: self._flog(
                        f"  ⚠  Browser crash page detected — navigating back to platform URL…", "WARN"))
                    plat_url = PLATFORMS.get(getattr(self, "_current_platform", ""), "")
                    if plat_url:
                        try:
                            self.driver.get(plat_url)
                        except Exception:
                            pass
                    self._do_freeze_refresh(REFRESH_WAIT)
                    prev_time = None
                    continue
            except Exception:
                pass

            # sample currentTime
            current_time = None
            try:
                iframe_srcs = getattr(self, "_freeze_iframe_src", "")
                if iframe_srcs:
                    # support single string or list for nested iframes
                    if isinstance(iframe_srcs, str):
                        iframe_srcs = [iframe_srcs]
                    # switch through each iframe level in sequence
                    for src in iframe_srcs:
                        try:
                            iframe_el = self.driver.find_element(
                                "xpath", f'//iframe[contains(@src, "{src}")]')
                            self.driver.switch_to.frame(iframe_el)
                        except Exception:
                            break  # iframe not found at this level, stop switching
                js_to_run = (self._freeze_video_js if self._freeze_video_js else
                             "const vids = document.querySelectorAll('video');"
                             "const v = Array.from(vids).find(v => !v.paused && v.readyState > 0)"
                             "         || vids[vids.length - 1];"
                             "return v ? v.currentTime : null;")
                current_time = self.driver.execute_script(js_to_run)
            except Exception as e:
                err = str(e)
                # check if tab crashed (OOM etc.) — URL may now be an error page
                try:
                    crash_url = self.driver.current_url or ""
                    if any(crash_url.startswith(p) for p in (
                            "chrome-error://", "edge://crashedtab",
                            "about:neterror", "chrome://crashedtab")):
                        self.root.after(0, lambda: self._flog(
                            "  ⚠  Browser tab crashed (Out of Memory?) — navigating back to platform URL…", "WARN"))
                        plat_url = PLATFORMS.get(getattr(self, "_current_platform", ""), "")
                        if plat_url:
                            try:
                                self.driver.get(plat_url)
                            except Exception:
                                pass
                        self._do_freeze_refresh(REFRESH_WAIT)
                        prev_time = None
                        continue
                except Exception:
                    pass
                self.root.after(0, lambda m=err: self._flog(f"  JS error: {m}", "ERROR"))
            finally:
                try:
                    self.driver.switch_to.default_content()
                except Exception:
                    pass

            if current_time is None:
                self.root.after(0, lambda: self._flog(
                    "  ⚠  No video element found — refreshing…", "WARN"))
                self._do_freeze_refresh(REFRESH_WAIT)
                prev_time = None
                continue

            if prev_time is None:
                # first sample — if it's 0.0, video probably hasn't started yet; skip and retry
                if current_time == 0.0:
                    zero_retry_count += 1
                    if zero_retry_count >= MAX_ZERO_RETRIES:
                        self.root.after(0, lambda: self._flog(
                            f"  ⛔  Baseline currentTime=0.0 for {MAX_ZERO_RETRIES} consecutive cycles — "
                            "video not playing. Stopping Freeze Detection.", "ERROR"))
                        self.root.after(0, self.stop_freeze_detection)
                        break
                    self.root.after(0, lambda n=zero_retry_count, m=MAX_ZERO_RETRIES: self._flog(
                        f"  ⏳  Baseline=0.0 — video not started yet, retrying ({n}/{m})… waiting {CHECK_INTERVAL}s", "WARN"))
                    if not self._freeze_sleep(CHECK_INTERVAL):
                        break
                    continue
                # baseline is > 0 — video is playing, reset counter and proceed normally
                zero_retry_count = 0
                consec_zero_recovery = 0
                prev_time = current_time
                self.root.after(0, lambda t=current_time: self._flog(
                    f"  ▶  First sample: currentTime={t:.1f}s — waiting {CHECK_INTERVAL}s…"))
                if not self._freeze_sleep(CHECK_INTERVAL):
                    break
                continue

            # compare — delta must be at least MIN_DELTA seconds
            delta = current_time - prev_time
            min_expected = 15  # seconds; video must advance at least this much per interval
            if delta >= min_expected:
                self.root.after(0, lambda t=current_time, d=delta: self._flog(
                    f"  ✓  Video OK — currentTime={t:.1f}s (+{d:.1f}s)", "OK"))
                prev_time = current_time
                consec_zero_recovery = 0
                if not self._freeze_sleep(CHECK_INTERVAL):
                    break
            else:
                # freeze detected — check if currentTime is stuck at 0.0 after recovery attempts
                if current_time == 0.0:
                    consec_zero_recovery += 1
                    if consec_zero_recovery >= MAX_ZERO_RETRIES:
                        self.root.after(0, lambda: self._flog(
                            f"  ⛔  currentTime=0.0 after {MAX_ZERO_RETRIES} consecutive recoveries — "
                            "video unresponsive. Stopping Freeze Detection.", "ERROR"))
                        self.root.after(0, self.stop_freeze_detection)
                        break
                else:
                    consec_zero_recovery = 0  # normal freeze (not zero), reset zero-recovery counter
                self.root.after(0, lambda t=current_time, p=prev_time, d=delta, m=min_expected: self._flog(
                    f"  ❄  FREEZE detected! currentTime={t:.1f}s (+{d:.1f}s, expected ≥{m:.0f}s) — refreshing…", "ERROR"))
                self._do_freeze_refresh(REFRESH_WAIT)
                prev_time = None

        self._freeze_running = False
        self.root.after(0, lambda: self._freeze_stop_btn.config(state="disabled"))
        self.root.after(0, lambda: self._freeze_start_btn.config(state="normal"))
        self.root.after(0, lambda: self._freeze_status_var.set("AntiFreeze inactive"))

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
            # check for DAZN "Join live" button after refresh
            self._freeze_try_join_live()
            # check for profile-chooser avatar after refresh (e.g. DStv)
            self._freeze_try_profile_select()
            # check for platform-specific "Play Live" dialog after refresh (e.g. WOWOW)
            self._try_live_selector()
            # click unmute button inside iframe if platform needs it after refresh (e.g. Teleantillas)
            self._try_unmute()

    def _freeze_try_join_live(self):
        """After freeze refresh, click #joinLive if present (DAZN 'Join live' button)."""
        if not self._alive():
            return
        try:
            btn = self.driver.find_element("id", "joinLive")
            if btn and btn.is_displayed():
                btn.click()
                self.root.after(0, lambda: self._flog(
                    "  ▶  'Join live' button found — clicked to rejoin stream.", "OK"))
        except Exception:
            pass  # button not present — video resumed on its own, continue normally

    def _freeze_try_profile_select(self):
        """After freeze refresh, click profile-chooser avatar if present (e.g. DStv reverts to profile chooser)."""
        if not self._alive():
            return
        xpath = getattr(self, "_freeze_profile_selector", "")
        if not xpath:
            return
        try:
            el = self.driver.find_element("xpath", xpath)
            if el and el.is_displayed():
                el.click()
                self.root.after(0, lambda: self._flog(
                    "  ▶  Profile chooser detected — clicked profile avatar to resume.", "OK"))
                time.sleep(3)  # wait for profile to load before next step (e.g. watch-button)
        except Exception:
            pass  # profile chooser not present — video resumed on its own, continue normally

    def _try_live_selector(self):
        """After refresh, click a platform-specific 'Play Live' button if present (e.g. WOWOW resume dialog).
        Uses freeze_live_selector XPath from PLATFORM_RULES. Silent no-op if element not found."""
        if not self._alive():
            return
        xpath = getattr(self, "_freeze_live_selector", "")
        if not xpath:
            return
        try:
            el = self.driver.find_element("xpath", xpath)
            if el and el.is_displayed():
                el.click()
                self.root.after(0, lambda: self._flog(
                    "  ▶  'Play Live' dialog detected — clicked to start live stream.", "OK"))
        except Exception:
            pass  # dialog not present — video resumed on its own, continue normally

    def _try_unmute(self):
        """After refresh, switch into freeze_iframe_src frames and click the unmute button
        (freeze_unmute_selector XPath). Silent no-op if selector empty or element not found."""
        if not self._alive():
            return
        xpath = getattr(self, "_freeze_unmute_selector", "")
        if not xpath:
            return
        iframe_srcs = getattr(self, "_freeze_iframe_src", "")
        if isinstance(iframe_srcs, str):
            iframe_srcs = [iframe_srcs] if iframe_srcs else []
        try:
            for src in iframe_srcs:
                try:
                    iframe_el = self.driver.find_element(
                        "xpath", f'//iframe[contains(@src, "{src}")]')
                    self.driver.switch_to.frame(iframe_el)
                except Exception:
                    break
            el = self.driver.find_element("xpath", xpath)
            if el and el.is_displayed():
                el.click()
                self.root.after(0, lambda: self._flog(
                    "  🔊  Unmute button found — clicked to unmute player.", "OK"))
        except Exception:
            pass  # unmute button not present — video already unmuted or not loaded yet
        finally:
            try:
                self.driver.switch_to.default_content()
            except Exception:
                pass

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
        ttk.Button(bf, text="Clear", command=self._clear_inspect).pack(side="left")
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

    # ── browser size helpers ──────────────────────────────────────────────────
    BROWSER_SIZES = {
        "SM": (550, 450),
        "MD": (650, 550),
        "LG": (750, 650),
    }

    def _get_browser_wh(self):
        """Return (w, h) from the browser_size_var dropdown."""
        key = self.browser_size_var.get().split(" ")[0]  # "SM" or "MD"
        return self.BROWSER_SIZES.get(key, (550, 450))

    def _on_browser_size_changed(self, *_):
        """Live-resize browser if it's open."""
        if not self._alive():
            return
        w, h = self._get_browser_wh()
        try:
            self.driver.set_window_size(w, h)
        except Exception:
            pass

    # ── date helpers ──────────────────────────────────────────────────────────
    def _shift_date(self, var: tk.StringVar, days: int):
        raw = var.get().strip()
        try:
            d = datetime.datetime.strptime(raw, "%Y-%m-%d")
        except ValueError:
            d = datetime.datetime.now()
        d += datetime.timedelta(days=days)
        var.set(d.strftime("%Y-%m-%d"))

    # ── platform change ───────────────────────────────────────────────────────
    def _set_start_now(self):
        n = datetime.datetime.now()
        self.start_date.set(n.strftime("%Y-%m-%d"))
        self.start_time.set(n.strftime("%H:%M"))

    def _set_freeze_start_now(self):
        n = datetime.datetime.now()
        self._freeze_start_date.set(n.strftime("%Y-%m-%d"))
        self._freeze_start_time.set(n.strftime("%H:%M"))

    def _scan_time(self):
        """Scan the currently open browser page for a date/time and populate start date/time."""
        if not self.driver:
            messagebox.showwarning("Scan", "No browser open. Open the browser first.")
            return
        try:
            page_text = self.driver.execute_script("return document.body.innerText;")
        except Exception as e:
            messagebox.showerror("Scan", f"Could not read page: {e}")
            return

        dt_found = None
        platform = self.platform_var.get()
        is_prime = platform.startswith("Prime Video")

        MONTHS = {
            "Jan":1,"January":1,"Feb":2,"February":2,"Mar":3,"March":3,
            "Apr":4,"April":4,"May":5,"Jun":6,"June":6,
            "Jul":7,"July":7,"Aug":8,"August":8,"Sep":9,"September":9,
            "Oct":10,"October":10,"Nov":11,"November":11,"Dec":12,"December":12,
        }

        def _parse_amazon(text):
            # Format 1: full date — "June 28, 2026 3:00 AM CEST" or "29 Jun 2026 3:10 PM CEST"
            m = re.search(
                r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
                r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
                r'\s+(\d{1,2}),?\s+(\d{4})\s+(\d{1,2}):(\d{2})\s*(AM|PM)',
                text, re.IGNORECASE)
            if m:
                try:
                    mon  = MONTHS.get(m.group(1).capitalize()) or MONTHS.get(m.group(1)[:3].capitalize())
                    day  = int(m.group(2))
                    year = int(m.group(3))
                    hour = int(m.group(4))
                    mins = int(m.group(5))
                    ampm = m.group(6).upper()
                    if ampm == "PM" and hour != 12:
                        hour += 12
                    elif ampm == "AM" and hour == 12:
                        hour = 0
                    return datetime.datetime(year, mon, day, hour, mins)
                except ValueError:
                    pass

            # Format 2: time only — "Watch Live: 15:10 CEST" (event is today, no date shown)
            m2 = re.search(r'\b(\d{1,2}):(\d{2})\s*(?:CEST|CET|UTC|GMT|EST|PST|BST)?\b', text)
            if m2:
                try:
                    now = datetime.datetime.now()
                    return now.replace(hour=int(m2.group(1)), minute=int(m2.group(2)),
                                       second=0, microsecond=0)
                except ValueError:
                    pass

            return None

        def _parse_stan(text):
            # Stan format: "3:00pm 29 June 2026" or "11:30am 1 July 2026"
            # Extracted from <section class="program__details-extended"> → first program__extra div
            m = re.search(
                r'\b(\d{1,2}):(\d{2})(am|pm)\s+(\d{1,2})\s+'
                r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
                r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
                r'\s+(\d{4})',
                text, re.IGNORECASE)
            if m:
                try:
                    hour = int(m.group(1))
                    mins = int(m.group(2))
                    ampm = m.group(3).lower()
                    day  = int(m.group(4))
                    mon  = MONTHS.get(m.group(5).capitalize()) or MONTHS.get(m.group(5)[:3].capitalize())
                    year = int(m.group(6))
                    if ampm == "pm" and hour != 12:
                        hour += 12
                    elif ampm == "am" and hour == 12:
                        hour = 0
                    return datetime.datetime(year, mon, day, hour, mins)
                except ValueError:
                    pass
            return None

        def _parse_espn(text):
            # ESPN+ format: "Monday, July 6 | 7:30 PM"
            # Extracted from <p class="WatchPaywall__subtitle">
            # ESPN+ shows times in the PC's local timezone (detected from browser locale),
            # so no conversion needed — use as-is.
            m = re.search(
                r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+'
                r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
                r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
                r'\s+(\d{1,2})\s*\|\s*(\d{1,2}):(\d{2})\s*(AM|PM)',
                text, re.IGNORECASE)
            if m:
                try:
                    mon  = MONTHS.get(m.group(1).capitalize()) or MONTHS.get(m.group(1)[:3].capitalize())
                    day  = int(m.group(2))
                    hour = int(m.group(3))
                    mins = int(m.group(4))
                    ampm = m.group(5).upper()
                    if ampm == "PM" and hour != 12:
                        hour += 12
                    elif ampm == "AM" and hour == 12:
                        hour = 0
                    year = datetime.datetime.now().year
                    return datetime.datetime(year, mon, day, hour, mins)
                except ValueError:
                    pass
            return None

        is_stan      = (platform == "Stan")
        is_espn      = (platform == "ESPN+ US")
        is_viaplay_dk = (platform == "Viaplay DK")

        def _parse_viaplay_dk(text):
            # Format: "I dag kl. 07.30" (today), "I morgen kl. 07.30" (tomorrow)
            # or Danish weekday: "Mandag kl. 07.30" etc.
            # Time uses dot separator: HH.MM
            if not text:
                return None
            m = re.search(r'\bkl\.\s*(\d{1,2})\.(\d{2})\b', text, re.IGNORECASE)
            if not m:
                return None
            try:
                hour = int(m.group(1))
                mins = int(m.group(2))
                now  = datetime.datetime.now()
                base = now.replace(hour=0, minute=0, second=0, microsecond=0)
                if re.search(r'\bI morgen\b', text, re.IGNORECASE):
                    base = base + datetime.timedelta(days=1)
                else:
                    DK_DAYS = {"Mandag":0,"Tirsdag":1,"Onsdag":2,"Torsdag":3,
                               "Fredag":4,"Lørdag":5,"Lordag":5,"Søndag":6,"Sondag":6}
                    for dk_day, weekday in DK_DAYS.items():
                        if re.search(r'\b' + dk_day + r'\b', text, re.IGNORECASE):
                            days_ahead = (weekday - now.weekday()) % 7
                            base = now.replace(hour=0, minute=0, second=0, microsecond=0) \
                                   + datetime.timedelta(days=days_ahead)
                            break
                    # else "I dag" or unrecognised prefix → today (base unchanged)
                return base.replace(hour=hour, minute=mins)
            except ValueError:
                return None

        if is_prime:
            # For Prime Video: wait for buy-box-msg to render, then read ONLY that element.
            # Never fall back to full page — page is full of other dates/timestamps.
            def _read_buy_box(d):
                t = d.execute_script("""
                    var el = document.querySelector('[data-testid="buy-box-msg"]');
                    if (!el) return null;
                    return (el.innerText || el.textContent || '').replace(/ /g, ' ').trim();
                """)
                return t if t else None

            try:
                prime_text = WebDriverWait(self.driver, 10).until(_read_buy_box)
                self.log(f"  🔍  Scan [buy-box-msg]: {repr(prime_text[:80]) if prime_text else 'None'}", "PRECHECK")
                dt_found = _parse_amazon(prime_text) if prime_text else None
            except Exception as e:
                prime_text = None
                self.log(f"  🔍  Scan [buy-box-msg] timeout/error: {e}", "PRECHECK")

            if dt_found is None:
                # Last resort: try current page_text (already read at top) with Amazon regex only
                dt_found = _parse_amazon(page_text)
                if dt_found:
                    self.log(f"  🔍  Scan [body fallback]: {repr(page_text[:80])}", "PRECHECK")

            if dt_found is None:
                messagebox.showinfo("Scan", "No Amazon date/time found on page.\n"
                                            "Make sure you're on the event page with the 'Watch Live' button visible.")
                return

        # 1b. Stan — "3:00pm 29 June 2026" from program__details-extended
        if is_stan and dt_found is None:
            try:
                stan_text = self.driver.execute_script("""
                    var el = document.querySelector('section.program__details-extended .program__extra');
                    return el ? (el.innerText || el.textContent || '').trim() : null;
                """)
                self.log(f"  🔍  Scan [Stan program__extra]: {repr(stan_text[:80]) if stan_text else 'None'}", "PRECHECK")
                dt_found = _parse_stan(stan_text) if stan_text else None
            except Exception as e:
                self.log(f"  🔍  Scan [Stan] error: {e}", "PRECHECK")

            if dt_found is None:
                # Fallback: try full page text with Stan parser
                dt_found = _parse_stan(page_text)

            if dt_found is None:
                messagebox.showinfo("Scan", "No Stan date/time found on page.\n"
                                            "Make sure you're on the event page showing the start time.")
                return

        # 1c. ESPN+ US — "Monday, July 6 | 7:30 PM" (local PC time, no conversion needed)
        if is_espn and dt_found is None:
            try:
                espn_text = self.driver.execute_script("""
                    var el = document.querySelector('.WatchPaywall__subtitle');
                    return el ? (el.innerText || el.textContent || '').trim() : null;
                """)
                self.log(f"  🔍  Scan [ESPN+ WatchPaywall__subtitle]: {repr(espn_text[:80]) if espn_text else 'None'}", "PRECHECK")
                dt_found = _parse_espn(espn_text) if espn_text else None
            except Exception as e:
                self.log(f"  🔍  Scan [ESPN+] error: {e}", "PRECHECK")

            if dt_found is None:
                dt_found = _parse_espn(page_text)

            if dt_found is None:
                messagebox.showinfo("Scan", "No ESPN+ date/time found on page.\n"
                                            "Make sure you're on the event page showing the start time.")
                return

        # 1d. Viaplay DK — "I dag kl. 07.30" from StartTime_container element
        if is_viaplay_dk and dt_found is None:
            try:
                viaplay_text = self.driver.execute_script("""
                    var el = document.querySelector('[class*="StartTime_container"]');
                    return el ? (el.innerText || el.textContent || '').trim() : null;
                """)
                self.log(
                    f"  🔍  Scan [Viaplay DK StartTime_container]: "
                    f"{repr(viaplay_text[:80]) if viaplay_text else 'None'}", "PRECHECK")
                dt_found = _parse_viaplay_dk(viaplay_text) if viaplay_text else None
            except Exception as e:
                self.log(f"  🔍  Scan [Viaplay DK] error: {e}", "PRECHECK")
            if dt_found is None:
                dt_found = _parse_viaplay_dk(page_text)
            if dt_found is None:
                messagebox.showinfo("Scan", "No Viaplay DK time found on page.\n"
                                            "Make sure you're on the event page showing the start time.")
                return

        # 2. YYYY/MM/DD HH:MM or YYYY-MM-DD HH:MM (e.g. NBA Docomo: 2026/06/24 08:45)
        if dt_found is None:
            m2 = re.search(r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})\s+(\d{1,2}):(\d{2})', page_text)
            if m2:
                try:
                    dt_found = datetime.datetime(
                        int(m2.group(1)), int(m2.group(2)), int(m2.group(3)),
                        int(m2.group(4)), int(m2.group(5))
                    )
                except ValueError:
                    dt_found = None

        # 3. Fallback: plain HH:MM (uses today's date)
        if dt_found is None:
            m3 = re.search(r'\b(\d{1,2}):(\d{2})\b', page_text)
            if m3:
                try:
                    now = datetime.datetime.now()
                    dt_found = now.replace(hour=int(m3.group(1)), minute=int(m3.group(2)),
                                           second=0, microsecond=0)
                except ValueError:
                    dt_found = None

        if dt_found is None:
            messagebox.showinfo("Scan", "No time found on the current page.")
            return

        # Apply offset
        offset_min = getattr(self, "scan_offset_var", None)
        offset = offset_min.get() if offset_min else 0
        dt_adjusted = dt_found - datetime.timedelta(minutes=offset)

        self.start_date.set(dt_adjusted.strftime("%Y-%m-%d"))
        self.start_time.set(dt_adjusted.strftime("%H:%M"))
        self.log(
            f"  🔍  Scan: found {dt_found.strftime('%Y-%m-%d %H:%M')} → "
            f"start set to {dt_adjusted.strftime('%Y-%m-%d %H:%M')} "
            f"(offset -{offset} min)", "PRECHECK"
        )

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
            self._post_refresh_key   = rule.get("post_refresh_key", "")
            self._pre_click_targets  = rule.get("pre_click_targets", "").splitlines()
            self._pre_click_wait     = rule.get("pre_click_wait", 3)
            self._pre_click_nav_url  = rule.get("pre_click_nav_url", "")
            self._post_click_targets = rule.get("post_click_targets", "").splitlines()
            self._post_click_wait    = rule.get("post_click_wait", 3)
            self._post_switch_wait   = rule.get("post_switch_wait", 0)
            self._prevent_new_window = rule.get("prevent_new_window", False)
            self._force_js_click     = rule.get("force_js_click", False)
            self._dispatch_click     = rule.get("dispatch_click", False)
            self._ctrl_click         = rule.get("ctrl_click", False)
            self._hover_before_click = rule.get("hover_before_click", False)
            self._video_detect       = rule.get("video_detect", False)
            self._video_detect_js    = rule.get("video_detect_js", "")
            self._video_detect_key   = rule.get("video_detect_key", "")
            self._freeze_video_js    = rule.get("freeze_video_js", "")
            self._freeze_recovery    = rule.get("freeze_recovery", "refresh_only")
            self._freeze_profile_selector = rule.get("freeze_profile_selector", "")
            self._freeze_live_selector    = rule.get("freeze_live_selector", "")
            self._freeze_iframe_src       = rule.get("freeze_iframe_src", "")
            self._freeze_unmute_selector  = rule.get("freeze_unmute_selector", "")
        # scan offset default per platform
        scan_off = PLATFORM_RULES.get(name, {}).get("scan_offset", None)
        if scan_off is not None:
            self.scan_offset_var.set(scan_off)
        # set default browser per platform
        if name in ("TOD", "Paramount+", "NBA Docomo", "Disney+ SE", "Disney+ DK", "Disney+ AR", "Disney+ BR", "Prime Video MX", "Coupang Play", "Peacock", "DAZN ES", "DStv", "FanCode", "Hotstar", "WOWOW", "Victory+", "Dailymotion", "Teleantillas", "U-Next"):
            self.browser_var.set("Edge")
        elif name:
            self.browser_var.set("Chrome")
        # browser size default per platform
        if name in ("SPOTV Now JP", "Disney+ AR", "Disney+ BR", "Fubo", "Hotstar", "ESPN+ US"):
            self.browser_size_var.set("MD — 650×550")
        elif name in ("FanCode", "Stan"):
            self.browser_size_var.set("LG — 750×650")
        elif name:
            self.browser_size_var.set("SM — 550×450")
        # freeze detection default per platform
        if name in ("DAZN DE", "DAZN ES", "DAZN IT", "DStv",
                    "Prime Video USA", "Prime Video IT", "Prime Video BR",
                    "Prime Video UK", "Prime Video DE", "Prime Video ES",
                    "Prime Video JP", "Prime Video MX", "Prime Video FR",
                    "Disney+ AR", "FanCode", "Stan", "WOWOW", "Viaplay DK"):
            self.freeze_detect_var.set(True)
        else:
            self.freeze_detect_var.set(False)
        # DStv: clear end date/time (runs indefinitely)
        rule = PLATFORM_RULES.get(name, {})
        if rule.get("freeze_no_end"):
            self._freeze_end_date.set("")
            self._freeze_end_time.set("")
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

    def _toggle_advanced(self):
        self._advanced_mode = not self._advanced_mode
        if self._advanced_mode:
            # show advanced widgets
            for w, method in self._adv_widgets:
                if method == "grid":
                    w.grid()
                else:
                    w.pack(side="left", padx=(0, 4))
            # show Inspector and Channels tabs
            self.nb.add(self._tab_inspector, text="  Inspector  ")
            self.nb.add(self._tab_channels,  text="  Channels  ")
            self._adv_btn.config(text="Simple")
        else:
            # hide advanced widgets
            for w, method in self._adv_widgets:
                if method == "grid":
                    w.grid_remove()
                else:
                    w.pack_forget()
            # hide Inspector and Channels tabs
            self.nb.hide(self._tab_inspector)
            self.nb.hide(self._tab_channels)
            self._adv_btn.config(text="Advanced")

    def _toggle_compact(self):
        if not self._compact:
            self._full_geometry = self.root.geometry()
            self.nb.pack_forget()
            self._compact_frame.pack(fill="x", before=self._status_bar)
            self.root.geometry(f"500x80+{self.root.winfo_x()}+{self.root.winfo_y()}")
            self.root.resizable(False, False)
            self._compact_btn.configure(text="Expand")
            self._adv_btn.pack_forget()
            self._compact = True
        else:
            self._compact_frame.pack_forget()
            self.nb.pack(fill="both", expand=True, padx=6, pady=6)
            if self._full_geometry:
                self.root.geometry(self._full_geometry)
            self.root.resizable(True, True)
            self._compact_btn.configure(text="Compact")
            self._adv_btn.pack(side="right", padx=(4, 0), pady=1)
            self._compact = False

    def log(self, msg, level="INFO"):
        now = datetime.datetime.now()
        ts  = now.strftime("%d-%m %H:%M:%S")
        self.log_box.config(state="normal")
        self.log_box.insert("end", f"[{ts}] {msg}\n", level)
        self.log_box.see("end")
        self.log_box.config(state="disabled")
        # update compact view with last log line
        short = msg if len(msg) <= 55 else msg[:52] + "…"
        self._compact_log_var.set(f"[{ts}] {short}")
        # append to log file
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] {msg}\n")
        except Exception:
            pass

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

    def open_browser(self):
        if not SEL:
            messagebox.showerror("Missing","Install: pip3 install selenium"); return
        if self._alive():
            self.log("Browser already open. Use Navigate.", "WARN"); return

        browser    = self.browser_var.get()
        url        = self.url_var.get().strip()
        pdir = os.path.join(PROFILE_DIR, f"{browser.lower()}_profile")
        os.makedirs(pdir, exist_ok=True)
        self._set_status(f"Opening {browser}…")
        self.log(f"Opening {browser}  |  autoclicker profile: {pdir}")

        def _go():
            try:
                if browser == "Chrome":
                    o = COptions()
                else:
                    o = EOptions()
                o.add_argument(f"--user-data-dir={pdir}")
                o.add_argument(f"--profile-directory=Default")
                o.add_argument("--disable-blink-features=AutomationControlled")
                o.add_argument("--no-sandbox")
                o.add_argument("--disable-dev-shm-usage")
                o.add_argument("--disable-gpu")
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
                        # after Selenium Manager downloads the driver, copy it to app folder
                        # so next launch finds it locally without re-downloading
                        try:
                            import shutil as _shutil2, re as _re2
                            _app_dir2 = os.path.dirname(os.path.abspath(sys.argv[0]))
                            _dest = os.path.join(_app_dir2, drv_name)
                            _cache_roots2 = [
                                os.path.join(os.environ.get("LOCALAPPDATA", ""), "selenium", "msedgedriver"),
                                os.path.join(os.path.expanduser("~"), ".cache", "selenium", "msedgedriver"),
                            ]
                            _found_new = None
                            for _cr2 in _cache_roots2:
                                if os.path.isdir(_cr2):
                                    for _root2, _dirs2, _files2 in os.walk(_cr2):
                                        if drv_name in _files2:
                                            _candidate = os.path.join(_root2, drv_name)
                                            # only copy if version matches current Edge
                                            _mv = _re2.search(r'[/\\](\d+)\.\d+\.\d+\.\d+[/\\]', _candidate)
                                            if _mv and _em and int(_mv.group(1)) == _em:
                                                _found_new = _candidate
                                                break
                                if _found_new:
                                    break
                            if _found_new:
                                _shutil2.copy2(_found_new, _dest)
                                self.root.after(0, lambda p=_dest: self.log(
                                    f"EdgeDriver cached locally: {p}", "OK"))
                        except Exception as _ce:
                            self.root.after(0, lambda e=str(_ce): self.log(
                                f"EdgeDriver cache copy skipped: {e}", "WARN"))
                # restore saved browser window position/size
                prefs = self._load_prefs()
                bkey = f"{browser.lower()}_browser"
                bpref = prefs.get(bkey, {})
                w, h = self._get_browser_wh()
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

    def _reposition_browser(self):
        if not self._alive():
            messagebox.showwarning("No browser", "Open browser first."); return
        prefs = self._load_prefs()
        bkey  = f"{self.browser_var.get().lower()}_browser"
        bpref = prefs.get(bkey, {})
        if not bpref:
            messagebox.showinfo("Reposition", "No saved position found. Close browser normally first to save position."); return
        try:
            w, h = self._get_browser_wh()
            x = bpref.get("x")
            y = bpref.get("y")
            self.driver.set_window_size(w, h)
            if x is not None and y is not None:
                self.driver.set_window_position(x, y)
            self.log(f"Browser repositioned to {x},{y} size {w}x{h}", "OK")
        except Exception as e:
            self.log(f"Reposition error: {e}", "ERROR")

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
        # hover over video element first if platform requires it (to reveal player controls)
        if self._hover_before_click:
            try:
                self.driver.execute_script("""
                    const el = document.querySelector('video') || document.body;
                    const rect = el.getBoundingClientRect();
                    const cx = rect.left + rect.width / 2;
                    const cy = rect.top + rect.height / 2;
                    el.dispatchEvent(new MouseEvent('mousemove', {bubbles:true, clientX:cx, clientY:cy}));
                    el.dispatchEvent(new MouseEvent('mouseenter', {bubbles:true, clientX:cx, clientY:cy}));
                    document.dispatchEvent(new MouseEvent('mousemove', {bubbles:true, clientX:cx, clientY:cy}));
                """)
                time.sleep(1.5)
            except Exception:
                pass  # continue anyway
        ok = 0
        for t in targets:
            try:
                if self._force_js_click:
                    el = WebDriverWait(self.driver, 8).until(
                        EC.presence_of_element_located((by, t)))
                    if self._dispatch_click:
                        self.driver.execute_script(
                            "arguments[0].dispatchEvent(new MouseEvent('click', "
                            "{bubbles: true, cancelable: true, view: window}))", el)
                        self.log(f"  ✓  dispatch-clicked '{t}'", "OK")
                    else:
                        self.driver.execute_script("arguments[0].click()", el)
                        self.log(f"  ✓  JS-clicked '{t}'", "OK")
                    ok += 1
                    if delay_s > 0: time.sleep(delay_s)
                    continue
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
        self.root.after(0, lambda: self._monitor_status_var.set("Monitoring active…"))
        self.log(f"Monitoring from {s_dt} → {end_str}", "HEAD")
        self.thread = threading.Thread(target=self._loop,
                                       args=(s_dt, e_dt), daemon=True)
        self.thread.start()
        # start pre-check thread (fires 2h before s_dt, checks driver is alive)
        precheck_thread = threading.Thread(target=self._precheck_loop,
                                           args=(s_dt,), daemon=True)
        precheck_thread.start()

    # ── Pre-check ─────────────────────────────────────────────────────────────

    def _run_precheck_now(self):
        """Immediately run the pre-check (browser alive + VPN IP) and alert if failed."""
        self.root.after(0, lambda: self.log("  🔍  Running pre-check now…", "PRECHECK"))
        try:
            result = self.driver.execute_script("return 1;")
            if result == 1:
                self.root.after(0, lambda: self.log("  ✅  Browser OK — browser is connected.", "PRECHECK"))
                self._precheck_ip_info()
            else:
                raise RuntimeError(f"Unexpected script result: {result}")
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda m=err: self.log(
                f"  🔴  Browser FAILED — browser disconnected: {m}", "ERROR"))
            self._send_precheck_alert(err)

    def _send_test_mail(self):
        """Send a test email to verify SMTP configuration."""
        self.root.after(0, lambda: self.log("  ✉  Sending test mail…", "PRECHECK"))
        try:
            body = (
                f"OTT AutoClicker — test mail.\n\n"
                f"SMTP konfiguracija radi ispravno.\n"
                f"Sent: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = "✅ AC - Test mail"
            msg["From"]    = PRECHECK_MAIL_FROM
            msg["To"]      = PRECHECK_MAIL_TO
            with smtplib.SMTP(PRECHECK_SMTP_HOST, PRECHECK_SMTP_PORT, timeout=15) as s:
                s.starttls()
                s.login(PRECHECK_SMTP_USER, PRECHECK_SMTP_PASS)
                s.sendmail(PRECHECK_MAIL_FROM, [PRECHECK_MAIL_TO], msg.as_string())
            self.root.after(0, lambda: self.log(
                f"  ✅  Test mail sent to {PRECHECK_MAIL_TO}.", "PRECHECK"))
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda m=err: self.log(
                f"  🔴  Test mail failed: {m}", "ERROR"))

    def _build_alert_html(self, platform_name, start_str, check_str, until_str, error_msg):
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:32px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        <!-- Header -->
        <tr>
          <td style="background:#c0392b;padding:24px 32px;">
            <span style="font-size:22px;font-weight:bold;color:#ffffff;letter-spacing:0.5px;">Browser Disconnected</span>
          </td>
        </tr>
        <!-- Body -->
        <tr>
          <td style="padding:28px 32px 24px 32px;">
            <p style="margin:0 0 20px 0;font-size:15px;color:#333333;line-height:1.6;">
              OTT AutoClicker pre-check detected that the browser is <strong>disconnected</strong>.<br>
              Please reconnect the browser before the scheduled start time.
            </p>
            <!-- Info table -->
            <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-radius:4px;overflow:hidden;">
              <tr style="background:#ebebeb;">
                <td style="padding:10px 14px;border-left:4px solid #c0392b;font-size:13px;color:#555555;width:170px;">Platform</td>
                <td style="padding:10px 14px;font-size:14px;color:#111111;font-weight:bold;">{platform_name}</td>
              </tr>
              <tr style="background:#ffffff;">
                <td style="padding:10px 14px;border-left:4px solid #c0392b;font-size:13px;color:#555555;">Check time</td>
                <td style="padding:10px 14px;font-size:14px;color:#111111;">{check_str}</td>
              </tr>
              <tr style="background:#ebebeb;">
                <td style="padding:10px 14px;border-left:4px solid #c0392b;font-size:13px;color:#555555;">Monitoring start</td>
                <td style="padding:10px 14px;font-size:14px;color:#111111;">{start_str}</td>
              </tr>
              <tr style="background:#ffffff;">
                <td style="padding:10px 14px;border-left:4px solid #c0392b;font-size:13px;color:#555555;">Until live</td>
                <td style="padding:10px 14px;font-size:14px;color:#111111;font-weight:bold;">{until_str}</td>
              </tr>
              <tr style="background:#ebebeb;">
                <td style="padding:10px 14px;border-left:4px solid #c0392b;font-size:13px;color:#555555;vertical-align:top;">Error</td>
                <td style="padding:10px 14px;font-size:13px;color:#c0392b;font-family:monospace;word-break:break-all;">{error_msg}</td>
              </tr>
            </table>
          </td>
        </tr>
        <!-- Footer -->
        <tr>
          <td style="padding:20px 32px;border-top:1px solid #eeeeee;">
            <p style="margin:0;font-size:12px;color:#aaaaaa;">OTT AutoClicker &nbsp;·&nbsp; autoclicker@global-mmk.com</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

    def _send_precheck_alert(self, error_msg):
        """Send email notification when pre-check detects browser is disconnected."""
        platform_name = self.platform_var.get() if hasattr(self, "platform_var") else "?"
        now = datetime.datetime.now()
        start_str = self._monitor_start_dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(self, "_monitor_start_dt") else "?"
        check_str = now.strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(self, "_monitor_start_dt"):
            delta = self._monitor_start_dt - now
            total_s = max(0, int(delta.total_seconds()))
            h, rem = divmod(total_s, 3600)
            m, s   = divmod(rem, 60)
            until_str = f"{h}h {m}m {s}s" if h else f"{m}m {s}s"
        else:
            until_str = "?"
        if not PRECHECK_SMTP_USER or not PRECHECK_SMTP_PASS or not PRECHECK_MAIL_TO:
            self.root.after(0, lambda: self.log(
                "  ⚠  Pre-check alert: mail not configured (set PRECHECK_SMTP_* in code).", "WARN"))
            return
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🔴 Browser Disconnected [{platform_name}]"
            msg["From"]    = PRECHECK_MAIL_FROM
            msg["To"]      = PRECHECK_MAIL_TO
            # plain text fallback
            plain = (
                f"OTT AutoClicker pre-check FAILED — browser disconnected.\n\n"
                f"Platform : {platform_name}\n"
                f"Start time: {start_str}\n"
                f"Check time: {check_str}\n"
                f"Error     : {error_msg}\n\n"
                f"Please reconnect the browser before the scheduled start."
            )
            msg.attach(MIMEText(plain, "plain", "utf-8"))
            msg.attach(MIMEText(self._build_alert_html(platform_name, start_str, check_str, until_str, error_msg), "html", "utf-8"))
            with smtplib.SMTP(PRECHECK_SMTP_HOST, PRECHECK_SMTP_PORT, timeout=15) as s:
                s.starttls()
                s.login(PRECHECK_SMTP_USER, PRECHECK_SMTP_PASS)
                s.sendmail(PRECHECK_MAIL_FROM, [PRECHECK_MAIL_TO], msg.as_string())
            self.root.after(0, lambda: self.log(
                f"  ✉  Pre-check alert sent to {PRECHECK_MAIL_TO}.", "WARN"))
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda m=err: self.log(
                f"  ✉  Pre-check alert — mail send failed: {m}", "ERROR"))

    def _precheck_ip_info(self):
        """Fetch IP/location info from inside the browser (reflects proxy/VPN extension).
        If the platform has a required country in PLATFORM_VPN_COUNTRY, verify the match
        and send an alert mail if it doesn't match."""
        import json as _json
        original_handle = None
        new_handle = None
        try:
            original_handle = self.driver.current_window_handle
            existing_handles = set(self.driver.window_handles)
            self.driver.execute_script("window.open('https://ipinfo.io/json');")
            # find the new handle — whichever wasn't there before
            import time as _time
            deadline = _time.time() + 5
            while _time.time() < deadline:
                new_handles = set(self.driver.window_handles) - existing_handles
                if new_handles:
                    new_handle = new_handles.pop()
                    break
                _time.sleep(0.2)
            if not new_handle:
                raise RuntimeError("New tab did not open")
            self.driver.switch_to.window(new_handle)
            _time.sleep(2)
            raw = self.driver.find_element("tag name", "pre").text
            data = _json.loads(raw)
            ip      = data.get("ip", "?")
            city    = data.get("city", "?")
            country = data.get("country", "?")
            org     = data.get("org", "?")
            self.root.after(0, lambda i=ip, ci=city, co=country: self.log(
                f"  ✅  VPN OK — browser IP: {i} | {ci}, {co}", "PRECHECK"))
            # check required country for this platform
            platform_name = self.platform_var.get() if hasattr(self, "platform_var") else ""
            required = PLATFORM_VPN_COUNTRY.get(platform_name)
            if required:
                if country.upper() != required.upper():
                    msg = (f"Expected country {required}, got {country} "
                           f"(IP: {ip} | {city}, {country})")
                    self.root.after(0, lambda m=msg: self.log(
                        f"  🔴  VPN WRONG COUNTRY — {m}", "ERROR"))
                    self._send_vpn_alert(ip, city, country, org, required)
                else:
                    self.root.after(0, lambda co=country, req=required: self.log(
                        f"  ✅  VPN country OK — {co} matches required {req}", "PRECHECK"))
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda m=err: self.log(
                f"  ⚠  VPN check failed: {m}", "WARN"))
        finally:
            try:
                if new_handle and new_handle in self.driver.window_handles:
                    self.driver.switch_to.window(new_handle)
                    self.driver.close()
                if original_handle and original_handle in self.driver.window_handles:
                    self.driver.switch_to.window(original_handle)
            except Exception:
                pass

    def _send_vpn_alert(self, ip, city, country, org, required):
        """Send email alert when browser IP country doesn't match the required country."""
        platform_name = self.platform_var.get() if hasattr(self, "platform_var") else "?"
        start_str = self._monitor_start_dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(self, "_monitor_start_dt") else "?"
        check_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(self, "_monitor_start_dt"):
            delta = self._monitor_start_dt - datetime.datetime.now()
            total_s = max(0, int(delta.total_seconds()))
            h, rem = divmod(total_s, 3600)
            m, s   = divmod(rem, 60)
            until_str = f"{h}h {m}m {s}s" if h else f"{m}m {s}s"
        else:
            until_str = "?"
        if not PRECHECK_SMTP_USER or not PRECHECK_SMTP_PASS or not PRECHECK_MAIL_TO:
            return
        try:
            html = self._build_vpn_alert_html(
                platform_name, check_str, start_str, until_str,
                ip, city, country, org, required)
            plain = (
                f"OTT AutoClicker VPN pre-check FAILED — wrong country.\n\n"
                f"Platform : {platform_name}\n"
                f"Required : {required}\n"
                f"Got      : {country} (IP: {ip} | {city})\n"
                f"ISP/VPN  : {org}\n"
                f"Check    : {check_str}\n"
                f"Start    : {start_str}\n"
                f"Until    : {until_str}\n\n"
                f"Please reconnect VPN to {required} before the scheduled start."
            )
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🔴 VPN Wrong Country [{platform_name}]"
            msg["From"]    = PRECHECK_MAIL_FROM
            msg["To"]      = PRECHECK_MAIL_TO
            msg.attach(MIMEText(plain, "plain", "utf-8"))
            msg.attach(MIMEText(html, "html", "utf-8"))
            with smtplib.SMTP(PRECHECK_SMTP_HOST, PRECHECK_SMTP_PORT, timeout=15) as s:
                s.starttls()
                s.login(PRECHECK_SMTP_USER, PRECHECK_SMTP_PASS)
                s.sendmail(PRECHECK_MAIL_FROM, [PRECHECK_MAIL_TO], msg.as_string())
            self.root.after(0, lambda: self.log(
                f"  ✉  VPN alert sent to {PRECHECK_MAIL_TO}.", "WARN"))
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda m=err: self.log(
                f"  ✉  VPN alert — mail send failed: {m}", "ERROR"))

    def _build_vpn_alert_html(self, platform_name, check_str, start_str, until_str,
                               ip, city, country, org, required):
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:32px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        <!-- Header -->
        <tr>
          <td style="background:#b7860b;padding:24px 32px;">
            <span style="font-size:22px;font-weight:bold;color:#ffffff;letter-spacing:0.5px;">VPN Wrong Country</span>
          </td>
        </tr>
        <!-- Body -->
        <tr>
          <td style="padding:28px 32px 24px 32px;">
            <p style="margin:0 0 20px 0;font-size:15px;color:#333333;line-height:1.6;">
              OTT AutoClicker pre-check detected that the browser IP is in the <strong>wrong country</strong>. Please reconnect VPN to <strong>{required}</strong> before the scheduled start time.
            </p>
            <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-radius:4px;overflow:hidden;">
              <tr style="background:#ebebeb;">
                <td style="padding:10px 14px;border-left:4px solid #b7860b;font-size:13px;color:#555555;width:170px;">Platform</td>
                <td style="padding:10px 14px;font-size:14px;color:#111111;font-weight:bold;">{platform_name}</td>
              </tr>
              <tr style="background:#ffffff;">
                <td style="padding:10px 14px;border-left:4px solid #b7860b;font-size:13px;color:#555555;">Check time</td>
                <td style="padding:10px 14px;font-size:14px;color:#111111;">{check_str}</td>
              </tr>
              <tr style="background:#ebebeb;">
                <td style="padding:10px 14px;border-left:4px solid #b7860b;font-size:13px;color:#555555;">Monitoring start</td>
                <td style="padding:10px 14px;font-size:14px;color:#111111;">{start_str}</td>
              </tr>
              <tr style="background:#ffffff;">
                <td style="padding:10px 14px;border-left:4px solid #b7860b;font-size:13px;color:#555555;">Until live</td>
                <td style="padding:10px 14px;font-size:14px;color:#111111;font-weight:bold;">{until_str}</td>
              </tr>
              <tr style="background:#ebebeb;">
                <td style="padding:10px 14px;border-left:4px solid #b7860b;font-size:13px;color:#555555;">Required country</td>
                <td style="padding:10px 14px;font-size:14px;color:#111111;font-weight:bold;">{required}</td>
              </tr>
              <tr style="background:#ffffff;">
                <td style="padding:10px 14px;border-left:4px solid #b7860b;font-size:13px;color:#555555;">Detected country</td>
                <td style="padding:10px 14px;font-size:14px;color:#c0392b;font-weight:bold;">{country}</td>
              </tr>
              <tr style="background:#ebebeb;">
                <td style="padding:10px 14px;border-left:4px solid #b7860b;font-size:13px;color:#555555;">Browser IP</td>
                <td style="padding:10px 14px;font-size:14px;color:#111111;">{ip} &nbsp;·&nbsp; {city}</td>
              </tr>
            </table>
          </td>
        </tr>
        <!-- Footer -->
        <tr>
          <td style="padding:20px 32px;border-top:1px solid #eeeeee;">
            <p style="margin:0;font-size:12px;color:#aaaaaa;">OTT AutoClicker &nbsp;·&nbsp; autoclicker@global-mmk.com</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

    def _precheck_page_health(self):
        """Refresh the event page and check for error indicators (404, 'sorry', etc.).
        Called after _precheck_ip_info() — browser is already back on the original window."""
        try:
            current_url = self.driver.current_url
            self.root.after(0, lambda: self.log(
                "  🔍  Page health check — refreshing event page…", "PRECHECK"))
            self.driver.refresh()
            time.sleep(6)
            page_text = self.driver.execute_script(
                "return (document.body ? "
                "(document.body.innerText || document.body.textContent || '') : '');")
            page_lower = page_text.lower() if page_text else ""
            ERROR_PHRASES = ["sorry", "couldn't find", "page not found", "404"]
            detected = next((p for p in ERROR_PHRASES if p in page_lower), None)
            if detected:
                self.root.after(0, lambda p=detected, u=current_url: self.log(
                    f"  🔴  Page health FAILED — '{p}' detected on page: {u}", "ERROR"))
                self._send_page_health_alert(current_url, detected)
            else:
                self.root.after(0, lambda: self.log(
                    "  ✅  Page health OK — event page loaded without errors.", "PRECHECK"))
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda m=err: self.log(
                f"  ⚠  Page health check failed: {m}", "WARN"))

    def _send_page_health_alert(self, url, detected_phrase):
        """Send email alert when the event page returns a 404 / sorry error."""
        platform_name = self.platform_var.get() if hasattr(self, "platform_var") else "?"
        now = datetime.datetime.now()
        start_str = self._monitor_start_dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(self, "_monitor_start_dt") else "?"
        check_str = now.strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(self, "_monitor_start_dt"):
            delta = self._monitor_start_dt - now
            total_s = max(0, int(delta.total_seconds()))
            h, rem = divmod(total_s, 3600)
            m, s   = divmod(rem, 60)
            until_str = f"{h}h {m}m {s}s" if h else f"{m}m {s}s"
        else:
            until_str = "?"
        if not PRECHECK_SMTP_USER or not PRECHECK_SMTP_PASS or not PRECHECK_MAIL_TO:
            self.root.after(0, lambda: self.log(
                "  ⚠  Page health alert: mail not configured.", "WARN"))
            return
        try:
            plain = (
                f"OTT AutoClicker pre-check FAILED — event page returned an error.\n\n"
                f"Platform  : {platform_name}\n"
                f"URL       : {url}\n"
                f"Detected  : '{detected_phrase}' found in page\n"
                f"Check time: {check_str}\n"
                f"Start time: {start_str}\n\n"
                f"The event URL may have changed. Please update the URL in the browser before monitoring starts."
            )
            html = self._build_page_health_alert_html(
                platform_name, url, detected_phrase, check_str, start_str, until_str)
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🔴 Page Error Detected [{platform_name}]"
            msg["From"]    = PRECHECK_MAIL_FROM
            msg["To"]      = PRECHECK_MAIL_TO
            msg.attach(MIMEText(plain, "plain", "utf-8"))
            msg.attach(MIMEText(html, "html", "utf-8"))
            with smtplib.SMTP(PRECHECK_SMTP_HOST, PRECHECK_SMTP_PORT, timeout=15) as s:
                s.starttls()
                s.login(PRECHECK_SMTP_USER, PRECHECK_SMTP_PASS)
                s.sendmail(PRECHECK_MAIL_FROM, [PRECHECK_MAIL_TO], msg.as_string())
            self.root.after(0, lambda: self.log(
                f"  ✉  Page health alert sent to {PRECHECK_MAIL_TO}.", "WARN"))
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda m=err: self.log(
                f"  ✉  Page health alert — mail send failed: {m}", "ERROR"))

    def _build_page_health_alert_html(self, platform_name, url, detected_phrase,
                                       check_str, start_str, until_str):
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:32px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        <tr>
          <td style="background:#e67e22;padding:24px 32px;">
            <span style="font-size:22px;font-weight:bold;color:#ffffff;letter-spacing:0.5px;">⚠ Page Error Detected</span>
          </td>
        </tr>
        <tr>
          <td style="padding:28px 32px 24px 32px;">
            <p style="margin:0 0 20px 0;font-size:15px;color:#333333;line-height:1.6;">
              The event page returned an error during pre-check.<br>
              The URL may have changed — please update it in the browser before monitoring starts.
            </p>
            <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-radius:4px;overflow:hidden;">
              <tr style="background:#ebebeb;">
                <td style="padding:10px 14px;border-left:4px solid #e67e22;font-size:13px;color:#555555;width:170px;">Platform</td>
                <td style="padding:10px 14px;font-size:14px;color:#111111;font-weight:bold;">{platform_name}</td>
              </tr>
              <tr style="background:#ffffff;">
                <td style="padding:10px 14px;border-left:4px solid #e67e22;font-size:13px;color:#555555;">Detected</td>
                <td style="padding:10px 14px;font-size:14px;color:#e67e22;font-weight:bold;">"{detected_phrase}" on page</td>
              </tr>
              <tr style="background:#ebebeb;">
                <td style="padding:10px 14px;border-left:4px solid #e67e22;font-size:13px;color:#555555;">URL</td>
                <td style="padding:10px 14px;font-size:13px;color:#2980b9;word-break:break-all;font-family:monospace;">{url}</td>
              </tr>
              <tr style="background:#ffffff;">
                <td style="padding:10px 14px;border-left:4px solid #e67e22;font-size:13px;color:#555555;">Check time</td>
                <td style="padding:10px 14px;font-size:14px;color:#111111;">{check_str}</td>
              </tr>
              <tr style="background:#ebebeb;">
                <td style="padding:10px 14px;border-left:4px solid #e67e22;font-size:13px;color:#555555;">Monitoring start</td>
                <td style="padding:10px 14px;font-size:14px;color:#111111;">{start_str}</td>
              </tr>
              <tr style="background:#ffffff;">
                <td style="padding:10px 14px;border-left:4px solid #e67e22;font-size:13px;color:#555555;">Until live</td>
                <td style="padding:10px 14px;font-size:14px;color:#111111;font-weight:bold;">{until_str}</td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:20px 32px;border-top:1px solid #eeeeee;">
            <p style="margin:0;font-size:12px;color:#aaaaaa;">OTT AutoClicker &nbsp;·&nbsp; autoclicker@global-mmk.com</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

    def _precheck_loop(self, s_dt):
        """Determine check time based on start time, then verify browser is alive.
        - 00:00–04:59 (night): check at 23:00 the previous evening
        - 05:00–23:59 (day):   check 2 hours before start
        """
        now = datetime.datetime.now()
        if s_dt.hour < 5:
            # night start — check at 23:00 the previous day
            prev_day = s_dt.date() - datetime.timedelta(days=1)
            check_dt = datetime.datetime.combine(prev_day, datetime.time(23, 0))
            label = "23:00 (night check, evening before)"
        else:
            # day start — check 2 hours before
            check_dt = s_dt - datetime.timedelta(hours=2)
            label = f"{check_dt.strftime('%H:%M')} (2h before start)"
        if check_dt <= now:
            # check time already passed — skip
            return
        # sleep until check time
        wait_s = (check_dt - now).total_seconds()
        self.root.after(0, lambda t=label: self.log(
            f"  🔍  Pre-check scheduled at {t}.", "PRECHECK"))
        # interruptible sleep
        deadline = time.time() + wait_s
        while time.time() < deadline:
            if not self.running:
                return  # monitoring was stopped, cancel pre-check
            time.sleep(5)
        if not self.running:
            return
        # perform the check
        self.root.after(0, lambda: self.log("  🔍  Running pre-check…", "PRECHECK"))
        try:
            result = self.driver.execute_script("return 1;")
            if result == 1:
                self.root.after(0, lambda: self.log("  ✅  Browser OK — browser is connected.", "PRECHECK"))
                self._precheck_ip_info()
                self._precheck_page_health()
            else:
                raise RuntimeError(f"Unexpected script result: {result}")
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda m=err: self.log(
                f"  🔴  Browser FAILED — browser disconnected: {m}", "ERROR"))
            self._send_precheck_alert(err)

    def stop_monitoring(self, trigger_freeze=False):
        self.running = False
        self.root.after(0, lambda: self.start_btn.config(state="normal"))
        self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
        self.root.after(0, lambda: self._monitor_status_var.set("Monitoring inactive"))
        self.log("Monitoring stopped.", "WARN"); self._set_status("Stopped")
        if trigger_freeze and self.freeze_detect_var.get():
            # keep original end time if freeze was already running (remonitor case)
            if hasattr(self, "_freeze_end_dt") and self._freeze_end_dt:
                freeze_end_dt = self._freeze_end_dt
            else:
                start_dt = getattr(self, "_monitor_start_dt", datetime.datetime.now())
                freeze_end_dt = start_dt + datetime.timedelta(hours=6)
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
            if self._post_refresh_key:
                load_s = self.load_var.get()
                if load_s > 0:
                    self.root.after(0, lambda s=load_s:
                        self.log(f"  ⏱  page-load wait {s}s…"))
                    if not self._sleep(load_s): break
                try:
                    ActionChains(self.driver).send_keys(self._post_refresh_key).perform()
                    k = self._post_refresh_key
                    self.root.after(0, lambda k=k: self.log(f"  ⌨  sent key '{k}' after refresh", "OK"))
                except Exception as e:
                    err = str(e)
                    self.root.after(0, lambda e=err: self.log(f"  ✗  key error: {e}", "ERROR"))

            # ── VIDEO DETECT MODE (e.g. DAZN) ─────────────────────────────────
            # No click targets — refresh and check if video started playing via JS.
            if self._video_detect:
                self._set_status("Active — watching for video…")
                load_s = self.load_var.get()
                if load_s > 0:
                    self.root.after(0, lambda s=load_s:
                        self.log(f"  ⏱  page-load wait {s}s…"))
                    if not self._sleep(load_s): break
                # click "Play Live" dialog if present (e.g. WOWOW resume dialog)
                self._try_live_selector()
                js = self._video_detect_js
                playing = False
                try:
                    playing = bool(self.driver.execute_script(js))
                except Exception as e:
                    err = str(e)
                    self.root.after(0, lambda e=err: self.log(f"  JS error: {e}", "ERROR"))
                if playing:
                    self.root.after(0, lambda: self.log("  ▶  Video playing — stopping.", "OK"))
                    if self._video_detect_key:
                        try:
                            ActionChains(self.driver).send_keys(self._video_detect_key).perform()
                            k = self._video_detect_key
                            self.root.after(0, lambda k=k: self.log(f"  ⌨  sent key '{k}'", "OK"))
                        except Exception as e:
                            err = str(e)
                            self.root.after(0, lambda e=err: self.log(f"  ✗  key error: {e}", "ERROR"))
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
            # pre-click targets: plain clicks only (no ctrl, no tab switch) — e.g. login flow
            if self._pre_click_targets:
                by = self._by()
                any_pre_clicked = False
                for i, t in enumerate(self._pre_click_targets):
                    try:
                        el = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((by, t)))
                        try:
                            el.click()
                        except ElementClickInterceptedException:
                            self.driver.execute_script("arguments[0].click()", el)
                        self.root.after(0, lambda x=t: self.log(f"  ✓  pre-click '{x}'", "OK"))
                        any_pre_clicked = True
                        # always wait after each pre-click (including last) to let page react
                        self._sleep(self._pre_click_wait)
                    except TimeoutException:
                        self.root.after(0, lambda x=t: self.log(f"  —  pre-click not found (skip): '{x}'"))
                    except Exception as e:
                        err = str(e)
                        self.root.after(0, lambda x=t, e=err: self.log(f"  ✗  pre-click error '{x}': {e}", "ERROR"))
                # navigate to schedule URL only if login flow was triggered
                if self._pre_click_nav_url and any_pre_clicked:
                    try:
                        self.driver.get(self._pre_click_nav_url)
                        self.root.after(0, lambda u=self._pre_click_nav_url:
                            self.log(f"  ↪  navigated to {u}", "OK"))
                        self._sleep(self.load_var.get() or 5)
                    except Exception as e:
                        err = str(e)
                        self.root.after(0, lambda e=err: self.log(f"  ✗  navigate error: {e}", "ERROR"))
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
