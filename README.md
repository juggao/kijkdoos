# 📺 Kijkdoos

A Dutch IPTV stream player built with Python, Tkinter and VLC.  
Loads channel lists from the [famelack-channels](https://github.com/famelack/famelack-channels) JSON format and plays them embedded directly in the window.

![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![VLC](https://img.shields.io/badge/vlc-required-orange) ![Platform](https://img.shields.io/badge/platform-linux%20%7C%20windows%20%7C%20macos-lightgrey)

---

## Requirements

| Package | Purpose | Install |
|---|---|---|
| [VLC media player](https://www.videolan.org/vlc/) | Stream playback engine | system package |
| `python-vlc` | Python bindings for VLC | `pip install python-vlc` |
| `Pillow` | App icon rendering | `pip install Pillow` |
| `yt-dlp` | YouTube channel support | `pip install yt-dlp` |

```bash
pip install python-vlc Pillow yt-dlp
```

---

## Quick start

```bash
# Run with the default Dutch channel list
python kijkdoos.py

# Use a different country (replace 'nl' with any ISO code)
python kijkdoos.py --json https://raw.githubusercontent.com/famelack/famelack-channels/main/channels/raw/countries/de.json

# Use a local JSON file
python kijkdoos.py --json /path/to/channels.json

# Install desktop icon (GNOME/Ubuntu)
python kijkdoos.py --install
```

---

## Features

### Playback
- Streams play embedded inside the window via VLC
- **◀◀ / ▶▶** buttons to step through channels
- **■ Stop** to halt playback
- Remembers the last watched channel and resumes it on next launch

### Channel list
- Loads channels from any famelack-compatible JSON source (URL or local file)
- **Live search** — filter by name as you type
- **Category filter** — dropdown to narrow by category
- Shows total channel count and currently filtered count
- **🔒** indicator for geo-blocked channels
- **[YT]** indicator for YouTube-only channels

### YouTube support
- YouTube channels (`[YT]`) are resolved via `yt-dlp` in a background thread
- Embed URLs (`youtube-nocookie.com/embed/…`) are automatically converted to standard watch URLs
- UI stays responsive while the stream URL is being resolved

### Recording
- **⏺ Record** button records the current stream to `~/Videos/`
- Output format: `kijkdoos_<channel>_<YYYYMMDD_HHMMSS>.ts`
- Recording runs silently in a separate VLC instance — no echo
- Main player stays audible during recording
- Button blinks red while recording; shows saved file path on stop

### Volume
- Animated **VU meter** — 20 bars, green → yellow → red
- Peak hold indicator
- Click or drag anywhere on the meter to set volume
- Mouse wheel scrolls volume up/down in 5% steps

### Fullscreen
- **⛶ Fullscreen** button or **F11** to enter
- Sidebar and chrome are hidden; video fills the screen
- Auto-hiding overlay with channel name, ◀◀/▶▶, and Exit button
- Overlay reappears on mouse movement, hides after 2.5 s
- **Esc** or **F11** to exit

### Settings
- **⚙ Settings** button opens a dialog to change the JSON source
- Accepts any URL or local file path
- Tip shown for switching to other countries (e.g. `de`, `fr`, `gb`, `us`, `be`)
- Settings saved to `~/.kijkdoos_config.json`

---

## JSON format

Kijkdoos understands the famelack channel schema out of the box:

```json
[
  {
    "nanoid": "abc123",
    "name": "NPO 1",
    "iptv_urls": ["https://example.com/npo1/index.m3u8"],
    "youtube_urls": [],
    "language": "nld",
    "country": "nl",
    "isGeoBlocked": false
  }
]
```

It also accepts:
- Plain arrays with a `url` field
- `{ "channels": [...] }` wrapper objects
- Flat `{ "name": "url" }` dictionaries
- Channels with multiple stream URLs (listed as `Channel [2]`, `Channel [3]`, etc.)

---

## GNOME / Ubuntu desktop integration

To add Kijkdoos to your application launcher with an icon:

```bash
python kijkdoos.py --install
```

This installs:
- The icon at all standard sizes into `~/.local/share/icons/hicolor/`
- A `.desktop` file at `~/.local/share/applications/kijkdoos.desktop`

If the icon doesn't appear in the taskbar, find the correct `WM_CLASS`:

```bash
# In one terminal:
python kijkdoos.py &

# In another terminal, then click the Kijkdoos window:
xprop WM_CLASS

# Edit the .desktop file and set:
# StartupWMClass=<second value from xprop output>

update-desktop-database ~/.local/share/applications
```

---

## Configuration file

Settings are stored in `~/.kijkdoos_config.json`:

```json
{
  "json_source": "https://raw.githubusercontent.com/famelack/...",
  "volume": 80,
  "last_channel": "NPO 1"
}
```

---

## Country codes

Change the country by swapping the ISO code in the URL:

| Code | Country |
|------|---------|
| `nl` | Netherlands |
| `de` | Germany |
| `fr` | France |
| `gb` | United Kingdom |
| `be` | Belgium |
| `us` | United States |

Full list at [famelack-channels](https://github.com/famelack/famelack-channels/tree/main/channels/raw/countries).

---

## License

MIT
