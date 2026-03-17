#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║          Kijkdoos  ·  v1.0               ║
║  A sleek Tkinter/VLC stream player for IPTV JSON     ║
╚══════════════════════════════════════════════════════╝

Requirements:
    pip install python-vlc requests

VLC must be installed on your system:
    https://www.videolan.org/vlc/

Usage:
    python kijkdoos.py
    python kijkdoos.py --json /path/to/channels.json
    python kijkdoos.py --json https://example.com/channels.json
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import threading
import json
import os
import sys
import re
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

# ── optional python-vlc ────────────────────────────────────────────────────────
try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False

# ── optional yt-dlp (for YouTube channel support) ──────────────────────────────
try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False

# ── default JSON source ────────────────────────────────────────────────────────
DEFAULT_JSON_URL = (
    "https://raw.githubusercontent.com/famelack/"
    "famelack-channels/main/channels/raw/countries/nl.json"
)
CONFIG_FILE = Path.home() / ".kijkdoos_config.json"

# ── app icon (embedded PNG) ──────────────────────────────────────────────────
ICON_PNG_B64 = (
    "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"
)

# ── colour palette ─────────────────────────────────────────────────────────────
COLORS = {
    "bg":         "#0d0d0f",
    "surface":    "#16161a",
    "surface2":   "#1e1e24",
    "border":     "#2a2a35",
    "accent":     "#e8ff00",          # electric lime — vivid, memorable
    "accent2":    "#00d4ff",          # cyan
    "text":       "#e8e8f0",
    "text_dim":   "#6b6b80",
    "text_muted": "#3a3a50",
    "playing":    "#e8ff00",
    "error":      "#ff4455",
    "ok":         "#00ff88",
}

FONTS = {
    "title":    ("Courier New", 18, "bold"),
    "heading":  ("Courier New", 10, "bold"),
    "body":     ("Courier New", 9),
    "small":    ("Courier New", 8),
    "status":   ("Courier New", 9, "italic"),
    "big":      ("Courier New", 28, "bold"),
}


# ═══════════════════════════════════════════════════════════════════════════════
class ChannelLoader:
    """Load + parse channel JSON from a URL or local file path."""

    @staticmethod
    def load(source: str) -> list[dict]:
        raw = ChannelLoader._fetch(source)
        data = json.loads(raw)
        return ChannelLoader._normalise(data)

    @staticmethod
    def _fetch(source: str) -> str:
        if source.startswith("http://") or source.startswith("https://"):
            req = urllib.request.Request(
                source,
                headers={"User-Agent": "Kijkdoos/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.read().decode("utf-8")
        else:
            with open(source, "r", encoding="utf-8") as f:
                return f.read()

    @staticmethod
    def _normalise(data) -> list[dict]:
        """Accept multiple JSON shapes, including the famelack schema.

        famelack schema (nl.json):
          {nanoid, name, iptv_urls: [...], youtube_urls: [...],
           language, country, isGeoBlocked}

        Also handles:
          - plain list with a single 'url' field
          - {channels: [...]} wrapper dicts
          - flat {name: url_string} dicts
        """
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for key in ("channels", "items", "streams", "data"):
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    break
            else:
                # flat dict of name → url string
                items = [{"name": k, "url": v} for k, v in data.items()
                         if isinstance(v, str)]
        else:
            return []

        channels = []
        for ch in items:
            if not isinstance(ch, dict):
                continue

            name = (ch.get("name") or ch.get("title") or
                    ch.get("channel") or "Unknown").strip()
            logo = (ch.get("logo") or ch.get("icon") or
                    ch.get("thumbnail") or "").strip()
            category = (ch.get("category") or ch.get("group") or
                        ch.get("group-title") or "").strip()
            is_geo = ch.get("isGeoBlocked", False)

            # ── collect all stream URLs (famelack uses iptv_urls list) ──
            stream_urls: list[str] = []

            # famelack: iptv_urls is a list
            for u in ch.get("iptv_urls") or []:
                if isinstance(u, str) and u.strip():
                    stream_urls.append(u.strip())

            # fallback: plain 'url' / 'stream_url' / 'src' field
            for key in ("url", "stream_url", "streamUrl", "src"):
                val = ch.get(key)
                if isinstance(val, str) and val.strip():
                    stream_urls.append(val.strip())

            # youtube_urls as last-resort fallback (no native playback but
            # we still list them so the user can copy the URL)
            yt_urls: list[str] = []
            for u in ch.get("youtube_urls") or []:
                if isinstance(u, str) and u.strip():
                    yt_urls.append(u.strip())

            # de-duplicate while preserving order
            seen: set[str] = set()
            unique_urls: list[str] = []
            for u in stream_urls + yt_urls:
                if u not in seen:
                    seen.add(u)
                    unique_urls.append(u)

            if not unique_urls:
                continue  # no playable URL at all — skip

            # If multiple URLs exist, create one entry per URL with a suffix
            if len(unique_urls) == 1:
                channels.append({
                    "name": name,
                    "url": unique_urls[0],
                    "logo": logo,
                    "category": category or "General",
                    "is_geo": is_geo,
                    "is_youtube": unique_urls[0] in yt_urls,
                    "all_urls": unique_urls,
                })
            else:
                # Primary entry uses the first URL; extras get a stream index
                for i, url in enumerate(unique_urls):
                    label = name if i == 0 else f"{name}  [{i+1}]"
                    channels.append({
                        "name": label,
                        "url": url,
                        "logo": logo,
                        "category": category or "General",
                        "is_geo": is_geo,
                        "is_youtube": url in yt_urls,
                        "all_urls": unique_urls,
                    })

        return channels


# ═══════════════════════════════════════════════════════════════════════════════
class Config:
    """Persist user settings to ~/.kijkdoos_config.json."""

    defaults = {
        "json_source": DEFAULT_JSON_URL,
        "volume": 80,
        "last_channel": "",
    }

    def __init__(self):
        self.data = dict(self.defaults)
        self._load()

    def _load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    self.data.update(json.load(f))
            except Exception:
                pass

    def save(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def __getitem__(self, key):
        return self.data.get(key, self.defaults.get(key))

    def __setitem__(self, key, val):
        self.data[key] = val


# ═══════════════════════════════════════════════════════════════════════════════
class Kijkdoos(tk.Tk):
    """Main application window."""

    def __init__(self, initial_source: Optional[str] = None):
        super().__init__()
        self.config_store = Config()
        if initial_source:
            self.config_store["json_source"] = initial_source

        self.channels: list[dict] = []
        self.filtered: list[dict] = []
        self.current_idx: int = -1
        self._vlc_instance = None
        self._player = None
        self._loading = False
        self._poll_id = None
        self._recording = False
        self._rec_player = None
        self._fullscreen = False
        self._fs_overlay = None
        self._fs_hide_id = None   # separate VLC player for recording
        self._rec_file: str = ""
        self._rec_blink_id = None

        self._setup_window()
        self._build_ui()
        self._init_vlc()
        self.after(100, self._initial_load)

    # ── window ─────────────────────────────────────────────────────────────────
    def _setup_window(self):
        self.title("▶  KIJKDOOS")
        # Set WM_CLASS so GNOME matches window to kijkdoos.desktop
        # The class name must equal StartupWMClass in the .desktop file
        try:
            self.tk.call("tk", "appname", "kijkdoos.py")
        except Exception:
            pass
        self.configure(bg=COLORS["bg"])
        self.geometry("1080x680")
        self.minsize(760, 500)
        self.resizable(True, True)
        self.bind("<F11>", lambda _: self._toggle_fullscreen())
        # App icon — uses ICON_PNG_B64 constant defined at top of file
        try:
            import base64 as _b64, io as _io
            from PIL import Image as _Img, ImageTk as _ITk
            _data = _b64.b64decode(ICON_PNG_B64)
            _pil  = _Img.open(_io.BytesIO(_data)).resize((64, 64), _Img.LANCZOS)
            self._icon_img = _ITk.PhotoImage(_pil)
            self.iconphoto(True, self._icon_img)
        except Exception:
            pass

    # ── VLC ────────────────────────────────────────────────────────────────────
    def _init_vlc(self):
        if not VLC_AVAILABLE:
            return
        try:
            self._vlc_instance = vlc.Instance(
                "--no-xlib", "--quiet", "--no-video-title-show"
            )
            self._player = self._vlc_instance.media_player_new()
        except Exception as e:
            self._vlc_instance = None
            self._player = None
            print(f"VLC init failed: {e}")

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._apply_ttk_style()
        self._build_header()

        # ── main panes
        self._paned = tk.PanedWindow(
            self, orient=tk.HORIZONTAL, bg=COLORS["bg"],
            sashwidth=4, sashrelief=tk.FLAT, sashpad=0
        )
        self._paned.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self._sidebar_pane = tk.Frame(self._paned, bg=COLORS["surface"], width=320)
        self._player_pane  = tk.Frame(self._paned, bg=COLORS["bg"])
        self._paned.add(self._sidebar_pane, minsize=220)
        self._paned.add(self._player_pane,  minsize=400)

        self._build_sidebar(self._sidebar_pane)
        self._build_player_area(self._player_pane)
        self._build_statusbar()

    def _apply_ttk_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "TScrollbar",
            background=COLORS["surface2"],
            troughcolor=COLORS["surface"],
            bordercolor=COLORS["border"],
            arrowcolor=COLORS["text_dim"],
        )
        style.configure(
            "Search.TEntry",
            fieldbackground=COLORS["surface2"],
            foreground=COLORS["text"],
            insertcolor=COLORS["accent"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
        )

    def _build_header(self):
        self._header = tk.Frame(self, bg=COLORS["surface"], height=52)
        hdr = self._header
        hdr.pack(fill=tk.X, side=tk.TOP)
        hdr.pack_propagate(False)

        logo = tk.Label(
            hdr, text="▶  KIJKDOOS",
            font=FONTS["title"],
            fg=COLORS["accent"], bg=COLORS["surface"],
        )
        logo.pack(side=tk.LEFT, padx=18, pady=10)

        sub = tk.Label(
            hdr, text="· kijkdoos ·",
            font=("Courier New", 9, "bold"),
            fg=COLORS["text_dim"], bg=COLORS["surface"],
        )
        sub.pack(side=tk.LEFT, pady=14)

        # top-right buttons
        btn_frame = tk.Frame(hdr, bg=COLORS["surface"])
        btn_frame.pack(side=tk.RIGHT, padx=14)

        self._mk_btn(btn_frame, "⚙  Settings", self._open_settings,
                     fg=COLORS["text_dim"]).pack(side=tk.RIGHT, padx=4)
        self._mk_btn(btn_frame, "↺  Reload", self._reload_channels,
                     fg=COLORS["accent2"]).pack(side=tk.RIGHT, padx=4)

        # separator line
        self._header_sep = tk.Frame(self, bg=COLORS["accent"], height=2)
        self._header_sep.pack(fill=tk.X)

    def _build_sidebar(self, parent):
        # ── search
        search_frame = tk.Frame(parent, bg=COLORS["surface"], pady=8, padx=10)
        search_frame.pack(fill=tk.X)

        tk.Label(
            search_frame, text="CHANNELS",
            font=FONTS["heading"],
            fg=COLORS["accent"], bg=COLORS["surface"],
        ).pack(anchor="w")

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter_channels())

        search_entry = tk.Entry(
            search_frame,
            textvariable=self._search_var,
            font=FONTS["body"],
            bg=COLORS["surface2"], fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief=tk.FLAT,
            bd=0,
        )
        search_entry.pack(fill=tk.X, pady=(6, 0), ipady=6, padx=1)
        tk.Frame(search_frame, bg=COLORS["border"], height=1).pack(fill=tk.X)

        # ── category filter
        cat_frame = tk.Frame(parent, bg=COLORS["surface"], padx=10, pady=4)
        cat_frame.pack(fill=tk.X)

        tk.Label(
            cat_frame, text="CATEGORY",
            font=FONTS["small"],
            fg=COLORS["text_dim"], bg=COLORS["surface"],
        ).pack(anchor="w")

        self._cat_var = tk.StringVar(value="All")
        self._cat_combo = ttk.Combobox(
            cat_frame,
            textvariable=self._cat_var,
            state="readonly",
            font=FONTS["body"],
        )
        self._cat_combo.pack(fill=tk.X, pady=(2, 0))
        self._cat_combo.bind("<<ComboboxSelected>>",
                             lambda _: self._filter_channels())

        # ── channel list
        list_frame = tk.Frame(parent, bg=COLORS["surface"])
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._listbox = tk.Listbox(
            list_frame,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            selectbackground=COLORS["accent"],
            selectforeground=COLORS["bg"],
            font=FONTS["body"],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            activestyle="none",
            yscrollcommand=scrollbar.set,
            cursor="hand2",
        )
        self._listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self._listbox.yview)
        self._listbox.bind("<Double-Button-1>", lambda _: self._play_selected())
        self._listbox.bind("<Return>", lambda _: self._play_selected())

        # ── bottom info
        self._ch_count_var = tk.StringVar(value="No channels loaded")
        tk.Label(
            parent,
            textvariable=self._ch_count_var,
            font=FONTS["small"],
            fg=COLORS["text_muted"], bg=COLORS["surface"],
            pady=4,
        ).pack()

    def _build_player_area(self, parent):
        # ── video embed frame
        self._video_frame = tk.Frame(parent, bg="#000000")
        self._video_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # placeholder when nothing is playing
        self._placeholder = tk.Frame(self._video_frame, bg="#000000")
        self._placeholder.place(relx=0, rely=0, relwidth=1, relheight=1)

        tk.Label(
            self._placeholder,
            text="▶",
            font=("Courier New", 60),
            fg=COLORS["text_muted"], bg="#000000",
        ).place(relx=0.5, rely=0.4, anchor="center")

        self._now_playing_var = tk.StringVar(value="Select a channel to watch")
        tk.Label(
            self._placeholder,
            textvariable=self._now_playing_var,
            font=FONTS["heading"],
            fg=COLORS["text_dim"], bg="#000000",
        ).place(relx=0.5, rely=0.55, anchor="center")

        # ── controls bar
        ctrl = tk.Frame(parent, bg=COLORS["surface"], height=54)
        ctrl.pack(fill=tk.X, side=tk.BOTTOM)
        ctrl.pack_propagate(False)

        # Play / Stop / Record / Nav
        self._mk_btn(ctrl, "◀◀", self._prev_channel).pack(side=tk.LEFT, padx=(10, 2), pady=8)
        self._play_btn = self._mk_btn(ctrl, "▶  Play", self._play_selected,
                                      fg=COLORS["accent"])
        self._play_btn.pack(side=tk.LEFT, padx=2, pady=8)
        self._stop_btn = self._mk_btn(ctrl, "■  Stop", self._stop,
                                      fg=COLORS["error"])
        self._stop_btn.pack(side=tk.LEFT, padx=2, pady=8)
        self._rec_btn = self._mk_btn(ctrl, "⏺  Record", self._toggle_record,
                                     fg="#cc2233")
        self._rec_btn.pack(side=tk.LEFT, padx=2, pady=8)
        self._mk_btn(ctrl, "▶▶", self._next_channel).pack(side=tk.LEFT, padx=(2, 8), pady=8)

        # ── VU meter ──────────────────────────────────────────────────────
        vu_container = tk.Frame(ctrl, bg=COLORS["surface"])
        vu_container.pack(side=tk.LEFT, padx=(12, 4), pady=6)

        tk.Label(vu_container, text="VOL", font=FONTS["small"],
                 fg=COLORS["text_dim"], bg=COLORS["surface"]).pack(anchor="w")

        # Canvas: 20 bars × 6px wide, 3px gap = 180px wide, 18px tall
        self._VU_BARS   = 20
        self._VU_W      = 180
        self._VU_H      = 16
        self._vu_canvas = tk.Canvas(
            vu_container,
            width=self._VU_W, height=self._VU_H,
            bg=COLORS["surface"], highlightthickness=0,
            cursor="hand2",
        )
        self._vu_canvas.pack()

        self._vol_pct = self.config_store["volume"]   # 0–100, set-point
        self._vu_level = 0.0                          # animated display level 0.0–1.0
        self._vu_peak  = 0.0                          # peak hold
        self._vu_peak_hold = 0                        # frames to hold peak

        self._vu_bar_ids: list = []
        self._vu_peak_id = None
        self._build_vu_bars()

        # click or drag to set volume
        self._vu_canvas.bind("<Button-1>",        self._vu_click)
        self._vu_canvas.bind("<B1-Motion>",       self._vu_click)
        self._vu_canvas.bind("<MouseWheel>",      self._vu_scroll)
        self._vu_canvas.bind("<Button-4>",        self._vu_scroll)   # Linux scroll up
        self._vu_canvas.bind("<Button-5>",        self._vu_scroll)   # Linux scroll dn

        self._vol_label = tk.Label(
            vu_container, text=f"{self._vol_pct}%",
            font=FONTS["small"],
            fg=COLORS["text_dim"], bg=COLORS["surface"], width=4, anchor="e",
        )
        self._vol_label.pack(anchor="e")

        # kick off VU animation loop
        self._vu_anim_id = None
        self._vu_animate()

        # Fullscreen button
        self._mk_btn(ctrl, "⛶  Fullscreen", self._toggle_fullscreen,
                     fg=COLORS["text_dim"]).pack(side=tk.RIGHT, padx=(4, 10), pady=8)

        # URL display
        self._url_var = tk.StringVar(value="")
        tk.Entry(
            ctrl, textvariable=self._url_var,
            font=("Courier New", 7),
            bg=COLORS["surface2"], fg=COLORS["text_muted"],
            insertbackground=COLORS["accent"],
            relief=tk.FLAT, bd=0,
            state="readonly",
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 8), ipady=4)

    def _build_statusbar(self):
        self._statusbar = tk.Frame(self, bg=COLORS["surface2"], height=22)
        bar = self._statusbar
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        self._status_var = tk.StringVar(value="Ready")
        tk.Label(
            bar,
            textvariable=self._status_var,
            font=FONTS["status"],
            fg=COLORS["text_dim"], bg=COLORS["surface2"],
            anchor="w", padx=10,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._source_var = tk.StringVar(
            value=self._short_source(self.config_store["json_source"])
        )
        tk.Label(
            bar,
            textvariable=self._source_var,
            font=FONTS["status"],
            fg=COLORS["text_muted"], bg=COLORS["surface2"],
            anchor="e", padx=10,
        ).pack(side=tk.RIGHT)

    # ── helpers ────────────────────────────────────────────────────────────────
    def _mk_btn(self, parent, text, cmd, fg=None, bg=None):
        return tk.Button(
            parent, text=text, command=cmd,
            font=FONTS["body"],
            fg=fg or COLORS["text"],
            bg=bg or COLORS["surface2"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["accent"],
            relief=tk.FLAT, bd=0,
            padx=10, pady=4,
            cursor="hand2",
        )

    @staticmethod
    def _short_source(src: str) -> str:
        if src.startswith("http"):
            return "↗ " + src.split("/")[-1]
        return "📄 " + Path(src).name

    # ── loading ────────────────────────────────────────────────────────────────
    def _initial_load(self):
        self._load_channels(self.config_store["json_source"])

    def _reload_channels(self):
        self._load_channels(self.config_store["json_source"])

    def _load_channels(self, source: str):
        if self._loading:
            return
        self._loading = True
        self._set_status(f"Loading channels from {self._short_source(source)} …")
        self._listbox.delete(0, tk.END)
        self._listbox.insert(tk.END, "  ⟳  Loading…")
        self._ch_count_var.set("Loading…")

        def work():
            try:
                chs = ChannelLoader.load(source)
                self.after(0, self._on_loaded, chs, None)
            except Exception as e:
                self.after(0, self._on_loaded, [], str(e))

        threading.Thread(target=work, daemon=True).start()

    def _on_loaded(self, channels: list, error: Optional[str]):
        self._loading = False
        if error:
            self._set_status(f"✖ Error: {error}", error=True)
            self._listbox.delete(0, tk.END)
            self._listbox.insert(tk.END, "  ✖  Failed to load channels")
            self._ch_count_var.set("Error loading channels")
            messagebox.showerror(
                "Load Error",
                f"Could not load channels:\n\n{error}\n\n"
                "Open Settings to change the JSON source.",
            )
            return

        self.channels = channels
        # populate category dropdown
        cats = sorted({c["category"] for c in channels})
        self._cat_combo["values"] = ["All"] + cats
        self._cat_var.set("All")

        self._filter_channels()
        self._set_status(f"✔ Loaded {len(channels)} channels")

        # restore last channel
        last = self.config_store["last_channel"]
        if last:
            for i, ch in enumerate(self.filtered):
                if ch["name"] == last:
                    self._listbox.selection_clear(0, tk.END)
                    self._listbox.selection_set(i)
                    self._listbox.see(i)
                    self._play_channel(ch)
                    break

    def _filter_channels(self):
        query = self._search_var.get().lower()
        cat = self._cat_var.get()
        self.filtered = [
            c for c in self.channels
            if (cat == "All" or c["category"] == cat)
            and (not query or query in c["name"].lower() or
                 query in c["category"].lower())
        ]
        self._listbox.delete(0, tk.END)
        cur = self._current_channel()
        for ch in self.filtered:
            bullet = "▶ " if ch is cur else "▸ "
            geo    = " 🔒" if ch.get("is_geo") else ""
            yt     = " [YT]" if ch.get("is_youtube") else ""
            self._listbox.insert(tk.END, f"  {bullet}{ch['name']}{geo}{yt}")
        self._ch_count_var.set(
            f"{len(self.filtered)} / {len(self.channels)} channels"
        )
        # re-highlight current
        self._highlight_current()

    def _current_channel(self) -> Optional[dict]:
        if 0 <= self.current_idx < len(self.channels):
            return self.channels[self.current_idx]
        return None

    def _highlight_current(self):
        if self.current_idx < 0:
            return
        cur = self._current_channel()
        if not cur:
            return
        for i, ch in enumerate(self.filtered):
            if ch is cur:
                self._listbox.selection_clear(0, tk.END)
                self._listbox.selection_set(i)
                self._listbox.see(i)
                break

    # ── playback ───────────────────────────────────────────────────────────────
    def _play_selected(self):
        sel = self._listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self.filtered):
            return
        ch = self.filtered[idx]
        # find index in master list
        try:
            self.current_idx = self.channels.index(ch)
        except ValueError:
            self.current_idx = -1
        self._play_channel(ch)

    def _play_channel(self, ch: dict):
        url = ch["url"]
        name = ch["name"]
        self._url_var.set(url)
        self._now_playing_var.set(f"Now Playing: {name}")
        self.config_store["last_channel"] = name
        self.config_store.save()

        # build informative status
        tags = []
        if ch.get("is_geo"):
            tags.append("🔒 Geo-blocked")
        if ch.get("is_youtube"):
            tags.append("YouTube — may not play in VLC")
        n_urls = len(ch.get("all_urls", [url]))
        if n_urls > 1:
            tags.append(f"{n_urls} streams available")
        tag_str = "  •  " + "  |  ".join(tags) if tags else ""
        self._set_status(f"▶ {name}{tag_str}")

        self._play_btn.config(text="■  Stop", command=self._stop,
                              fg=COLORS["error"])
        self._highlight_current()

        if self._player:
            self._stop_poll()
            if ch.get("is_youtube"):
                # Resolve YouTube URL in background then play
                self._set_status(f"⟳ Resolving YouTube stream for {name}…")
                threading.Thread(
                    target=self._resolve_and_play,
                    args=(ch, url),
                    daemon=True,
                ).start()
            else:
                self._start_vlc_playback(url)
        else:
            self._set_status(
                "⚠ VLC not available — install python-vlc to enable playback"
            )

    def _start_vlc_playback(self, url: str):
        """Attach and play a direct stream URL in VLC."""
        media = self._vlc_instance.media_new(url)
        self._player.set_media(media)
        wid = self._video_frame.winfo_id()
        if sys.platform.startswith("win"):
            self._player.set_hwnd(wid)
        elif sys.platform.startswith("darwin"):
            self._player.set_nsobject(wid)
        else:
            self._player.set_xwindow(wid)
        self._player.audio_set_volume(self._vol_pct)
        self._player.play()
        self._hide_placeholder()
        self._start_poll()

    def _resolve_and_play(self, ch: dict, yt_url: str):
        """Background thread: use yt-dlp to get a direct stream URL."""
        if not YTDLP_AVAILABLE:
            self.after(0, self._set_status,
                "⚠ yt-dlp not installed — run: pip install yt-dlp")
            return
        try:
            import re as _re
            # Convert embed / nocookie URLs to standard watch URLs
            m = _re.search(r"/embed/([A-Za-z0-9_-]{6,})", yt_url)
            if m:
                yt_url = f"https://www.youtube.com/watch?v={m.group(1)}"

            ydl_opts = {
                # Prefer a single-file format VLC can seek in;
                # fall back to best available
                "format": (
                    "bestvideo[ext=mp4][protocol=https]+bestaudio[ext=m4a]"
                    "/best[ext=mp4][protocol=https]"
                    "/best[protocol=https]"
                    "/best"
                ),
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(yt_url, download=False)

            # Pick the best single-URL format (avoid DASH manifests)
            stream_url = None
            for fmt in reversed(info.get("formats", [])):
                proto = fmt.get("protocol", "")
                url   = fmt.get("url", "")
                if url and proto in ("https", "http", "m3u8_native", "m3u8"):
                    stream_url = url
                    break
            if not stream_url:
                stream_url = info.get("url")
            if not stream_url:
                raise ValueError("No playable stream URL found")

            # Hand off to VLC on the main thread
            self.after(0, self._url_var.set, stream_url)
            self.after(0, self._set_status, f"▶ {ch['name']}  •  YouTube")
            self.after(0, self._start_vlc_playback, stream_url)
        except Exception as e:
            self.after(0, self._set_status, f"✖ YouTube error: {e}")

    def _stop(self):
        if self._recording:
            self._stop_recording()
        if self._player:
            self._stop_poll()
            self._player.stop()
        self._play_btn.config(text="▶  Play", command=self._play_selected,
                              fg=COLORS["accent"])
        self._now_playing_var.set("Select a channel to watch")
        self._url_var.set("")
        self._show_placeholder()
        self._set_status("Stopped")

    def _prev_channel(self):
        if not self.filtered:
            return
        sel = self._listbox.curselection()
        idx = (sel[0] - 1) % len(self.filtered) if sel else 0
        self._listbox.selection_clear(0, tk.END)
        self._listbox.selection_set(idx)
        self._listbox.see(idx)
        self._play_selected()

    def _next_channel(self):
        if not self.filtered:
            return
        sel = self._listbox.curselection()
        idx = (sel[0] + 1) % len(self.filtered) if sel else 0
        self._listbox.selection_clear(0, tk.END)
        self._listbox.selection_set(idx)
        self._listbox.see(idx)
        self._play_selected()

    # ── recording ─────────────────────────────────────────────────────────────
    # ── fullscreen ────────────────────────────────────────────────────────────
    # ── fullscreen ────────────────────────────────────────────────────────────
    def _toggle_fullscreen(self):
        if self._fullscreen:
            self._exit_fullscreen()
        else:
            self._enter_fullscreen()

    def _enter_fullscreen(self):
        self._fullscreen = True
        # Save current geometry so we can restore it
        self._pre_fs_geometry = self.geometry()
        self._pre_fs_state    = self.state()
        # Hide chrome by collapsing sidebar and shrinking header/status to 0
        self._header.pack_forget()
        self._header_sep.pack_forget()
        self._statusbar.pack_forget()
        # Remove sidebar from paned window (hide it)
        self._paned.forget(self._sidebar_pane)
        # Go fullscreen at OS level — video frame stays put, VLC handle unchanged
        self.attributes("-fullscreen", True)
        # Overlay controls
        self._fs_overlay = tk.Frame(self, bg="#000000")
        self._fs_overlay.place(relx=0, rely=1.0, anchor="sw",
                               relwidth=1.0, height=48)
        tk.Label(self._fs_overlay, textvariable=self._now_playing_var,
                 font=FONTS["heading"], fg=COLORS["text"],
                 bg="#000000").pack(side=tk.LEFT, padx=12)
        self._mk_btn(self._fs_overlay, "⛶  Exit  [Esc]",
                     self._exit_fullscreen,
                     fg=COLORS["accent"]).pack(side=tk.RIGHT, padx=12, pady=8)
        self._mk_btn(self._fs_overlay, "▶▶", self._next_channel
                     ).pack(side=tk.RIGHT, padx=4, pady=8)
        self._mk_btn(self._fs_overlay, "◀◀", self._prev_channel
                     ).pack(side=tk.RIGHT, padx=4, pady=8)
        self._fs_overlay_shown = True
        self._fs_hide_id = self.after(2500, self._fs_hide_overlay)
        self.bind("<Motion>", self._fs_motion)
        self.bind("<Escape>", lambda _: self._exit_fullscreen())

    def _exit_fullscreen(self):
        if not self._fullscreen:
            return
        self._fullscreen = False
        self.unbind("<Motion>")
        self.unbind("<Escape>")
        if self._fs_hide_id:
            self.after_cancel(self._fs_hide_id)
            self._fs_hide_id = None
        if self._fs_overlay:
            self._fs_overlay.destroy()
            self._fs_overlay = None
        # Restore OS window
        self.attributes("-fullscreen", False)
        # Restore sidebar into paned
        self._paned.add(self._sidebar_pane, minsize=220, before=self._player_pane)
        # Restore chrome
        self._header.pack(fill=tk.X, side=tk.TOP)
        self._header_sep.pack(fill=tk.X)
        self._statusbar.pack(fill=tk.X, side=tk.BOTTOM)

    def _fs_motion(self, event):
        if not self._fs_overlay_shown:
            self._fs_overlay.place(relx=0, rely=1.0, anchor="sw",
                                   relwidth=1.0, height=48)
            self._fs_overlay_shown = True
        if self._fs_hide_id:
            self.after_cancel(self._fs_hide_id)
        self._fs_hide_id = self.after(2500, self._fs_hide_overlay)

    def _fs_hide_overlay(self):
        if self._fs_overlay:
            self._fs_overlay.place_forget()
        self._fs_overlay_shown = False
        self._fs_hide_id = None

    def _toggle_record(self):
        if self._recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        ch = self._current_channel()
        if not ch:
            messagebox.showwarning("Record", "Start playing a channel first.")
            return
        if not VLC_AVAILABLE or not self._vlc_instance:
            messagebox.showwarning("Record", "VLC is required for recording.")
            return

        import time, re
        # build a safe filename from channel name
        safe = re.sub(r'[^\w\-]', '_', ch['name'])
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        out_dir = Path.home() / "Videos"
        out_dir.mkdir(parents=True, exist_ok=True)
        self._rec_file = str(out_dir / f"kijkdoos_{safe}_{timestamp}.ts")

        # VLC sout: file only — no display output, no echo
        sout = f"#standard{{access=file,mux=ts,dst={self._rec_file}}}"
        media = self._vlc_instance.media_new(ch["url"])
        media.add_option(f":sout={sout}")
        media.add_option(":sout-keep")
        media.add_option(":no-sout-display")   # suppress any audio/video output

        self._rec_player = self._vlc_instance.media_player_new()
        self._rec_player.set_media(media)
        self._rec_player.play()

        self._recording = True
        self._rec_btn.config(text="⏹  Stop Rec", fg=COLORS["accent"])
        self._set_status(f"⏺ Recording → {self._rec_file}")
        self._blink_record()

    def _stop_recording(self):
        if self._rec_player:
            self._rec_player.stop()
            self._rec_player.release()
            self._rec_player = None
        self._recording = False
        if self._rec_blink_id:
            self.after_cancel(self._rec_blink_id)
            self._rec_blink_id = None
        self._rec_btn.config(text="⏺  Record", fg=COLORS["error"])
        msg = f"Recording saved:\n{self._rec_file}" if self._rec_file else "Recording stopped."
        self._set_status(f"⏹ Saved → {self._rec_file}")
        messagebox.showinfo("Recording saved", msg)
        self._rec_file = ""

    def _blink_record(self):
        if not self._recording:
            return
        cur = self._rec_btn.cget("fg")
        next_fg = COLORS["bg"] if cur == COLORS["error"] else COLORS["error"]
        self._rec_btn.config(fg=next_fg)
        self._rec_blink_id = self.after(600, self._blink_record)


    # ── VU meter ───────────────────────────────────────────────────────────────
    def _build_vu_bars(self):
        self._vu_canvas.delete("all")
        self._vu_bar_ids = []
        n   = self._VU_BARS
        w   = self._VU_W
        h   = self._VU_H
        bw  = w / n          # bar slot width
        gap = 2

        for i in range(n):
            x0 = int(i * bw) + 1
            x1 = int((i + 1) * bw) - gap
            bid = self._vu_canvas.create_rectangle(
                x0, 0, x1, h,
                fill=COLORS["surface2"], outline="",
            )
            self._vu_bar_ids.append(bid)

        # peak hold marker (thin bright line)
        self._vu_peak_id = self._vu_canvas.create_rectangle(
            0, 0, 0, h, fill=COLORS["accent"], outline="",
        )

    def _vu_bar_color(self, i: int, n: int) -> str:
        """Green → yellow → red gradient across n bars."""
        frac = i / (n - 1)
        if frac < 0.6:
            return COLORS["ok"]       # green
        elif frac < 0.85:
            return COLORS["accent"]   # yellow/lime
        else:
            return COLORS["error"]    # red

    def _vu_animate(self):
        """60 fps animation loop: smoothly chase target level."""
        n   = self._VU_BARS
        w   = self._VU_W
        h   = self._VU_H
        bw  = w / n

        # target = set volume / 100 (when playing, optionally modulate)
        target = self._vol_pct / 100.0
        playing = (self._player and VLC_AVAILABLE and
                   self._player.get_state() not in
                   (vlc.State.Stopped, vlc.State.NothingSpecial,
                    vlc.State.Ended, vlc.State.Error)
                   if VLC_AVAILABLE else False)

        if playing:
            # add a tiny random shimmer to simulate audio activity
            import random
            shimmer = random.uniform(-0.08, 0.08)
            target = max(0.0, min(1.0, target + shimmer))
        else:
            target = self._vol_pct / 100.0   # static when idle

        # smooth chase
        self._vu_level += (target - self._vu_level) * 0.25

        # peak hold
        if self._vu_level >= self._vu_peak:
            self._vu_peak = self._vu_level
            self._vu_peak_hold = 18          # ~0.3 s at 60 fps
        else:
            if self._vu_peak_hold > 0:
                self._vu_peak_hold -= 1
            else:
                self._vu_peak -= 0.015
                self._vu_peak = max(self._vu_peak, 0.0)

        # draw bars
        active = self._vu_level * n
        for i, bid in enumerate(self._vu_bar_ids):
            if i < active:
                color = self._vu_bar_color(i, n)
            else:
                color = COLORS["surface2"]
            self._vu_canvas.itemconfig(bid, fill=color)

        # draw peak marker (2 px wide)
        px = int(self._vu_peak * w)
        self._vu_canvas.coords(self._vu_peak_id, max(0, px - 2), 0, px, h)
        peak_color = self._vu_bar_color(
            min(n - 1, int(self._vu_peak * n)), n
        )
        self._vu_canvas.itemconfig(self._vu_peak_id, fill=peak_color)

        self._vu_anim_id = self.after(16, self._vu_animate)   # ~60 fps

    def _vu_click(self, event):
        """Set volume by clicking/dragging on the VU canvas."""
        frac = max(0.0, min(1.0, event.x / self._VU_W))
        self._set_volume(int(frac * 100))

    def _vu_scroll(self, event):
        """Mouse-wheel volume control."""
        if event.num == 4 or event.delta > 0:
            self._set_volume(self._vol_pct + 5)
        else:
            self._set_volume(self._vol_pct - 5)

    # ── VLC polling ────────────────────────────────────────────────────────────
    def _start_poll(self):
        self._poll_id = self.after(1000, self._poll_player)

    def _stop_poll(self):
        if self._poll_id:
            self.after_cancel(self._poll_id)
            self._poll_id = None

    def _poll_player(self):
        if not self._player:
            return
        state = self._player.get_state()
        if state == vlc.State.Error:
            self._set_status("✖ Stream error — check URL or your connection",
                             error=True)
            self._show_placeholder()
        elif state == vlc.State.Ended:
            self._set_status("Stream ended")
            self._show_placeholder()
        else:
            self._poll_id = self.after(1000, self._poll_player)

    # ── placeholder ────────────────────────────────────────────────────────────
    def _hide_placeholder(self):
        self._placeholder.place_forget()

    def _show_placeholder(self):
        self._placeholder.place(relx=0, rely=0, relwidth=1, relheight=1)

    # ── status bar ─────────────────────────────────────────────────────────────
    def _set_status(self, msg: str, error: bool = False):
        self._status_var.set(msg)

    # ── settings dialog ────────────────────────────────────────────────────────
    def _open_settings(self):
        dlg = SettingsDialog(self, self.config_store)
        self.wait_window(dlg)
        if dlg.changed:
            self.config_store.save()
            self._source_var.set(
                self._short_source(self.config_store["json_source"])
            )
            self._load_channels(self.config_store["json_source"])

    # ── cleanup ────────────────────────────────────────────────────────────────
    def destroy(self):
        if self._fullscreen:
            self._exit_fullscreen()
        self._stop_poll()
        if self._recording:
            self._stop_recording()
        if self._rec_blink_id:
            self.after_cancel(self._rec_blink_id)
        if self._vu_anim_id:
            self.after_cancel(self._vu_anim_id)
        if self._player:
            self._player.stop()
            self._player.release()
        if self._vlc_instance:
            self._vlc_instance.release()
        self.config_store.save()
        super().destroy()


# ═══════════════════════════════════════════════════════════════════════════════
class SettingsDialog(tk.Toplevel):
    """Modal settings window."""

    def __init__(self, parent: Kijkdoos, cfg: Config):
        super().__init__(parent)
        self.cfg = cfg
        self.changed = False
        self.title("Settings")
        self.configure(bg=COLORS["bg"])
        self.resizable(False, False)
        self.geometry("560x320")
        self.transient(parent)
        self.grab_set()
        self._build()
        # centre on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self):
        pad = {"padx": 20, "pady": 8}

        tk.Label(
            self, text="⚙  SETTINGS",
            font=FONTS["title"],
            fg=COLORS["accent"], bg=COLORS["bg"],
        ).pack(anchor="w", **pad)

        tk.Frame(self, bg=COLORS["accent"], height=2).pack(fill=tk.X)

        # ── JSON source
        src_frame = tk.Frame(self, bg=COLORS["bg"])
        src_frame.pack(fill=tk.X, **pad)

        tk.Label(
            src_frame, text="JSON Channel Source  (URL or local file path)",
            font=FONTS["heading"],
            fg=COLORS["text"], bg=COLORS["bg"],
        ).pack(anchor="w")

        entry_row = tk.Frame(src_frame, bg=COLORS["bg"])
        entry_row.pack(fill=tk.X, pady=(4, 0))

        self._src_var = tk.StringVar(value=self.cfg["json_source"])
        src_entry = tk.Entry(
            entry_row,
            textvariable=self._src_var,
            font=FONTS["body"],
            bg=COLORS["surface2"], fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief=tk.FLAT, bd=0,
        )
        src_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 6))

        tk.Button(
            entry_row, text="Browse…",
            command=self._browse,
            font=FONTS["body"],
            bg=COLORS["surface2"], fg=COLORS["text_dim"],
            relief=tk.FLAT, bd=0, padx=8, pady=4,
            cursor="hand2",
        ).pack(side=tk.LEFT)

        tk.Label(
            src_frame,
            text="e.g.  https://raw.githubusercontent.com/famelack/famelack-channels/main/channels/raw/countries/nl.json",
            font=FONTS["small"],
            fg=COLORS["text_muted"], bg=COLORS["bg"],
            wraplength=500, justify="left",
        ).pack(anchor="w", pady=(4, 0))

        # ── other country hint
        hint_frame = tk.Frame(self, bg=COLORS["surface"], padx=14, pady=10)
        hint_frame.pack(fill=tk.X, padx=20)

        tk.Label(
            hint_frame,
            text="💡 Tip — change country by replacing 'nl' with another ISO code, e.g. de, fr, us, gb, be",
            font=FONTS["small"],
            fg=COLORS["accent2"], bg=COLORS["surface"],
            wraplength=500, justify="left",
        ).pack(anchor="w")

        # ── buttons
        btn_row = tk.Frame(self, bg=COLORS["bg"])
        btn_row.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=16)

        tk.Button(
            btn_row, text="✔  Save",
            command=self._save,
            font=FONTS["heading"],
            bg=COLORS["accent"], fg=COLORS["bg"],
            relief=tk.FLAT, bd=0, padx=16, pady=6,
            cursor="hand2",
        ).pack(side=tk.RIGHT)

        tk.Button(
            btn_row, text="Cancel",
            command=self.destroy,
            font=FONTS["body"],
            bg=COLORS["surface2"], fg=COLORS["text_dim"],
            relief=tk.FLAT, bd=0, padx=12, pady=6,
            cursor="hand2",
        ).pack(side=tk.RIGHT, padx=(0, 8))

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select JSON channel file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            self._src_var.set(path)

    def _save(self):
        src = self._src_var.get().strip()
        if not src:
            messagebox.showwarning("Invalid", "Please enter a JSON source.")
            return
        self.cfg["json_source"] = src
        self.changed = True
        self.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
def _do_install():
    """Install .desktop file and icon for GNOME/Ubuntu."""
    import base64, io, shutil, subprocess
    from PIL import Image

    script_path = Path(__file__).resolve()
    icon_dir    = Path.home() / ".local/share/icons/hicolor"
    desktop_dir = Path.home() / ".local/share/applications"
    pixmaps_dir = Path.home() / ".local/share/pixmaps"

    # Decode icon PNG
    icon_data = base64.b64decode(ICON_PNG_B64)

    # Install at multiple sizes
    for size in (16, 32, 48, 64, 128, 256):
        d = icon_dir / f"{size}x{size}" / "apps"
        d.mkdir(parents=True, exist_ok=True)
        img = Image.open(io.BytesIO(icon_data)).resize((size, size), Image.LANCZOS)
        img.save(str(d / "kijkdoos.png"))

    # Pixmaps fallback
    pixmaps_dir.mkdir(parents=True, exist_ok=True)
    (pixmaps_dir / "kijkdoos.png").write_bytes(icon_data)

    # .desktop file
    desktop_dir.mkdir(parents=True, exist_ok=True)
    python_bin = shutil.which("python3") or "python3"
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Kijkdoos
GenericName=IPTV Player
Comment=Nederlandse IPTV stream speler
Exec={python_bin} {script_path}
Icon=kijkdoos
Terminal=false
Categories=AudioVideo;Video;Player;
Keywords=iptv;stream;tv;kijkdoos;
StartupWMClass=kijkdoos.py
"""
    desktop_file = desktop_dir / "kijkdoos.desktop"
    desktop_file.write_text(desktop_content)
    desktop_file.chmod(0o755)

    # Refresh caches
    for cmd in (
        ["update-desktop-database", str(desktop_dir)],
        ["gtk-update-icon-cache", "-f", "-t", str(icon_dir)],
    ):
        try:
            subprocess.run(cmd, check=False, capture_output=True)
        except FileNotFoundError:
            pass

    print("✔  Kijkdoos installed!")
    print(f"   Desktop: {desktop_file}")
    print(f"   Icon:    {icon_dir}/256x256/apps/kijkdoos.png")
    print()
    print("   To verify the WM_CLASS (needed if icon still doesn't show):")
    print(f"     1. Run:  python3 {script_path} &")
    print("     2. Run:  xprop WM_CLASS  then click the window")
    print(f"     3. Set StartupWMClass= to the result in {desktop_file}")
    print(f"     4. Run:  update-desktop-database {desktop_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Kijkdoos — Nederlandse IPTV speler"
    )
    parser.add_argument(
        "--json", metavar="SOURCE",
        help="URL or file path to JSON channel list (overrides saved config)",
    )
    parser.add_argument(
        "--install", action="store_true",
        help="Install .desktop file and icon for GNOME/Ubuntu, then exit",
    )
    args = parser.parse_args()

    if args.install:
        _do_install()
        return

    if not VLC_AVAILABLE:
        print(
            "\n⚠  python-vlc is not installed.\n"
            "   Install it with:  pip install python-vlc\n"
            "   Also ensure VLC media player is installed: https://www.videolan.org/vlc/\n"
            "   The player UI will still launch but cannot play streams.\n"
        )
    if not YTDLP_AVAILABLE:
        print(
            "\n⚠  yt-dlp is not installed — YouTube channels [YT] will not play.\n"
            "   Install it with:  pip install yt-dlp\n"
        )

    app = Kijkdoos(initial_source=args.json)
    app.mainloop()


if __name__ == "__main__":
    main()
