"""
Typing Speed Tester - Measure WPM with accuracy tracking and mistake highlighting.
Built with tkinter. Includes Standard, Custom, and Wikipedia modes.
"""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
import time
import random
import threading
import urllib.request
import urllib.parse
import json
import re


# ─── Sample Texts ───────────────────────────────────────────────────────────────

SAMPLE_TEXTS = {
    "Easy": [
        "The quick brown fox jumps over the lazy dog near the river bank.",
        "A warm cup of coffee sits on the table beside an open book.",
        "The sun sets behind the hills painting the sky in shades of gold.",
        "She walked along the quiet path listening to the birds singing above.",
        "Rain drops fell gently on the window creating a soft rhythm.",
        "The cat slept peacefully on the couch while the fire crackled nearby.",
        "He opened the door and stepped into the cool morning air smiling.",
        "Stars filled the night sky like tiny diamonds scattered across velvet.",
        "The little boy laughed as he chased the red balloon in the park.",
        "Fresh bread smells amazing when it comes right out of the oven.",
        "They sat together under the large oak tree and talked for hours.",
        "We packed our bags and headed to the beach for a summer vacation.",
        "A small green frog hopped across the lily pads in the pond.",
        "Playing games with friends is a great way to spend a Friday night.",
        "He carefully wrapped the gift in bright blue paper with a shiny bow.",
    ],
    "Medium": [
        "Programming is the art of telling a computer what to do through a sequence of precise instructions written in a language it understands.",
        "The ability to type quickly and accurately is an essential skill in the modern digital workplace where communication happens at lightning speed.",
        "Machine learning algorithms analyze vast amounts of data to discover hidden patterns and make intelligent decisions without being explicitly programmed.",
        "Open source software has revolutionized the technology industry by enabling developers worldwide to collaborate and build upon each other's work freely.",
        "Cloud computing provides on-demand access to shared pools of configurable resources including networks servers storage and applications over the internet.",
        "The history of the internet began with the development of electronic computers in the 1950s and the initial concepts of wide area networking.",
        "A balanced diet consists of consuming the right amount of calories and nutrients to maintain a healthy body and prevent various long-term diseases.",
        "Photography is not just about capturing light but also about framing a moment in time and telling a compelling story without using any words.",
        "Learning a second language can significantly improve cognitive skills such as problem-solving memory and the ability to multitask effectively.",
        "The global economy relies heavily on intricate supply chains that transport goods from manufacturers to consumers across vast geographical distances.",
    ],
    "Hard": [
        "Quantum computing leverages the principles of quantum mechanics, such as superposition and entanglement, to process information in fundamentally different ways than classical computers, potentially solving complex problems exponentially faster.",
        "The implementation of cryptographic algorithms requires meticulous attention to detail; even minor vulnerabilities in the codebase can be exploited by sophisticated adversaries to compromise entire security infrastructures.",
        "Asynchronous programming paradigms, including callbacks, promises, and async/await syntax, enable developers to write non-blocking code that efficiently handles concurrent operations without sacrificing readability or maintainability.",
        "Distributed systems architecture demands careful consideration of consistency, availability, and partition tolerance trade-offs, as described by the CAP theorem, when designing fault-tolerant applications at scale.",
        "Photosynthesis is a complex biochemical process used by plants, algae, and certain bacteria to harness energy from sunlight and convert it into chemical energy stored in carbohydrate molecules, such as sugars.",
        "The socio-economic implications of artificial intelligence are profound, raising critical questions about labor market displacement, algorithmic bias, and the urgent need for comprehensive regulatory frameworks to govern its deployment.",
        "In terrestrial ecosystems, biodiversity plays a crucial role in maintaining resilience against environmental perturbations, ensuring ecosystem services like pollination, nutrient cycling, and climate regulation remain stable over time.",
        "The psychological phenomenon known as cognitive dissonance occurs when an individual experiences discomfort due to holding conflicting beliefs, values, or attitudes, often leading to rationalization or attitude change to restore harmony.",
    ],
}


# ─── Helper Functions ──────────────────────────────────────────────────────────

def fetch_wikipedia_sentences(count=3):
    url = "https://en.wikipedia.org/w/api.php?action=query&format=json&list=random&rnnamespace=0&rnlimit=10"
    sentences = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (TypingSpeedTester/1.0)'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            pages = data.get('query', {}).get('random', [])
            
            for p in pages:
                title = p['title']
                e_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro&explaintext&titles={urllib.parse.quote(title)}"
                e_req = urllib.request.Request(e_url, headers={'User-Agent': 'Mozilla/5.0 (TypingSpeedTester/1.0)'})
                with urllib.request.urlopen(e_req, timeout=5) as e_resp:
                    e_data = json.loads(e_resp.read().decode())
                    pages_dict = e_data.get('query', {}).get('pages', {})
                    if not pages_dict: continue
                    extract = list(pages_dict.values())[0].get('extract', '')
                    
                    # Split into sentences using a simple regex
                    sents = re.split(r'(?<=[.!?])\s+', extract)
                    # Filter out super short fragments
                    sents = [s.strip() for s in sents if len(s) > 20]
                    sentences.extend(sents)
                    
                    if len(sentences) >= count:
                        break
        if not sentences:
            return "Failed to find suitable text on Wikipedia. Please try again."
        return " ".join(sentences[:count])
    except Exception as e:
        return f"Error fetching from Wikipedia: {str(e)}"


# ─── Color Palette ──────────────────────────────────────────────────────────────

COLORS = {
    "bg_dark": "#0F1923",
    "bg_card": "#1A2733",
    "bg_input": "#0D1B2A",
    "accent": "#E2B714",
    "accent_hover": "#F5CC33",
    "correct": "#4CAF50",
    "incorrect": "#E74C3C",
    "text_primary": "#D1D0C5",
    "text_secondary": "#646669",
    "text_dim": "#3A3D41",
    "border": "#2C3E50",
    "highlight_bg": "#2A1A1A",
    "cursor_color": "#E2B714",
    "btn_reset": "#3A3D41",
    "btn_reset_hover": "#555860",
    "btn_stop": "#E74C3C",
    "btn_stop_hover": "#C0392B",
}


# ─── Main Application ──────────────────────────────────────────────────────────

class TypingSpeedTester:
    def __init__(self, root):
        self.root = root
        self.root.title("⌨ Typing Speed Tester")
        self.root.geometry("1000x850")
        self.root.configure(bg=COLORS["bg_dark"])
        self.root.resizable(True, True)
        self.root.minsize(800, 750)

        # ── Fonts ────────────────────────────────────────────────────────────
        self.font_title = tkfont.Font(family="Segoe UI", size=22, weight="bold")
        self.font_subtitle = tkfont.Font(family="Segoe UI", size=11)
        self.font_passage = tkfont.Font(family="Consolas", size=16)
        self.font_input = tkfont.Font(family="Consolas", size=16)
        self.font_stat_value = tkfont.Font(family="Segoe UI", size=36, weight="bold")
        self.font_stat_label = tkfont.Font(family="Segoe UI", size=10)
        self.font_btn = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.font_diff_label = tkfont.Font(family="Segoe UI", size=10, weight="bold")

        # ── State ────────────────────────────────────────────────────────────
        self.mode = "Standard" # "Standard", "Custom", "Wikipedia"
        self.difficulty = "Medium"
        self.timer_setting = "60s" # "30s", "60s", "120s", "5m", "15m", "1h", "Unlimited"
        self.target_text = ""
        self.start_time = None
        self.timer_running = False
        self.time_elapsed = 0
        self.test_finished = False
        
        # Cumulative stats for Unlimited Mode
        self.total_correct_chars = 0
        self.total_typed_chars = 0

        self._build_ui()
        self._new_text()

    # ── UI Construction ─────────────────────────────────────────────────────
    def _build_ui(self):
        # Main container
        self.main_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # ── Header ───────────────────────────────────────────────────────────
        header = tk.Frame(self.main_frame, bg=COLORS["bg_dark"])
        header.pack(fill="x", pady=(0, 15))

        title_label = tk.Label(
            header, text="⌨  Typing Speed Tester",
            font=self.font_title, fg=COLORS["accent"], bg=COLORS["bg_dark"],
        )
        title_label.pack(side="left")

        subtitle = tk.Label(
            header, text="Test your typing speed and accuracy",
            font=self.font_subtitle, fg=COLORS["text_secondary"], bg=COLORS["bg_dark"],
        )
        subtitle.pack(side="left", padx=(15, 0), pady=(8, 0))

        # ── Mode Selector ────────────────────────────────────────────────────
        mode_frame = tk.Frame(self.main_frame, bg=COLORS["bg_dark"])
        mode_frame.pack(fill="x", pady=(0, 10))
        
        mode_label = tk.Label(
            mode_frame, text="MODE", font=self.font_diff_label,
            fg=COLORS["text_secondary"], bg=COLORS["bg_dark"],
        )
        mode_label.pack(side="left", padx=(0, 8))

        self.mode_buttons = {}
        for mode in ["Standard", "Custom", "Wikipedia"]:
            btn = tk.Label(
                mode_frame, text=mode, font=self.font_diff_label,
                fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                padx=14, pady=5, cursor="hand2",
            )
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, m=mode: self._set_mode(m))
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=COLORS["border"]))
            btn.bind("<Leave>", lambda e, b=btn, m=mode: self._style_mode_btn(b, m))
            self.mode_buttons[mode] = btn

        # ── Dynamic Controls Container ───────────────────────────────────────
        self.dynamic_controls_frame = tk.Frame(self.main_frame, bg=COLORS["bg_dark"])
        self.dynamic_controls_frame.pack(fill="x", pady=(0, 12))
        
        # Will be populated by _build_dynamic_controls()

        # ── Stats Bar ────────────────────────────────────────────────────────
        stats_frame = tk.Frame(self.main_frame, bg=COLORS["bg_card"], pady=12)
        stats_frame.pack(fill="x", pady=(0, 12))
        stats_frame.configure(highlightbackground=COLORS["border"], highlightthickness=1)

        # WPM
        wpm_col = tk.Frame(stats_frame, bg=COLORS["bg_card"])
        wpm_col.pack(side="left", expand=True)
        self.wpm_value = tk.Label(
            wpm_col, text="0", font=self.font_stat_value,
            fg=COLORS["accent"], bg=COLORS["bg_card"],
        )
        self.wpm_value.pack()
        tk.Label(
            wpm_col, text="WPM", font=self.font_stat_label,
            fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
        ).pack()

        tk.Frame(stats_frame, bg=COLORS["border"], width=1).pack(side="left", fill="y", padx=10, pady=5)

        # Accuracy
        acc_col = tk.Frame(stats_frame, bg=COLORS["bg_card"])
        acc_col.pack(side="left", expand=True)
        self.acc_value = tk.Label(
            acc_col, text="100%", font=self.font_stat_value,
            fg=COLORS["correct"], bg=COLORS["bg_card"],
        )
        self.acc_value.pack()
        tk.Label(
            acc_col, text="ACCURACY", font=self.font_stat_label,
            fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
        ).pack()

        tk.Frame(stats_frame, bg=COLORS["border"], width=1).pack(side="left", fill="y", padx=10, pady=5)

        # Time
        time_col = tk.Frame(stats_frame, bg=COLORS["bg_card"])
        time_col.pack(side="left", expand=True)
        self.time_value = tk.Label(
            time_col, text="0s", font=self.font_stat_value,
            fg=COLORS["text_primary"], bg=COLORS["bg_card"],
        )
        self.time_value.pack()
        self.time_title_label = tk.Label(
            time_col, text="TIME LEFT", font=self.font_stat_label,
            fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
        )
        self.time_title_label.pack()

        tk.Frame(stats_frame, bg=COLORS["border"], width=1).pack(side="left", fill="y", padx=10, pady=5)

        # Characters
        char_col = tk.Frame(stats_frame, bg=COLORS["bg_card"])
        char_col.pack(side="left", expand=True)
        self.char_value = tk.Label(
            char_col, text="0/0", font=self.font_stat_value,
            fg=COLORS["text_primary"], bg=COLORS["bg_card"],
        )
        self.char_value.pack()
        tk.Label(
            char_col, text="CORRECT/TOTAL", font=self.font_stat_label,
            fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
        ).pack()

        # ── Passage Display ──────────────────────────────────────────────────
        passage_frame = tk.Frame(
            self.main_frame, bg=COLORS["bg_input"],
            highlightbackground=COLORS["border"], highlightthickness=1,
        )
        passage_frame.pack(fill="x", pady=(0, 8))

        self.passage_display = tk.Text(
            passage_frame, font=self.font_passage, bg=COLORS["bg_input"],
            fg=COLORS["text_dim"], wrap="word", height=5,
            relief="flat", padx=18, pady=14,
            cursor="arrow", selectbackground=COLORS["bg_input"],
            spacing1=4, spacing3=4,
        )
        self.passage_display.pack(fill="x")
        self.passage_display.configure(state="disabled")

        self.passage_display.tag_configure("correct", foreground=COLORS["correct"])
        self.passage_display.tag_configure("incorrect", foreground=COLORS["incorrect"], underline=True)
        self.passage_display.tag_configure("current", foreground=COLORS["text_primary"], background=COLORS["border"])
        self.passage_display.tag_configure("untyped", foreground=COLORS["text_dim"])

        # ── Input Area ───────────────────────────────────────────────────────
        input_frame = tk.Frame(
            self.main_frame, bg=COLORS["bg_card"],
            highlightbackground=COLORS["accent"], highlightthickness=2,
        )
        input_frame.pack(fill="x", pady=(0, 12))

        self.input_text = tk.Text(
            input_frame, font=self.font_input, bg=COLORS["bg_card"],
            fg=COLORS["text_primary"], wrap="word", height=3,
            relief="flat", padx=18, pady=14,
            insertbackground=COLORS["cursor_color"], insertwidth=3,
            selectbackground=COLORS["accent"],
        )
        self.input_text.pack(fill="x")
        self.input_text.bind("<KeyRelease>", self._on_key_release)
        self.input_text.bind("<Key>", self._on_key_press)

        # ── Status / Hint ────────────────────────────────────────────────────
        self.status_label = tk.Label(
            self.main_frame, text="Start typing to begin the test...",
            font=self.font_subtitle, fg=COLORS["text_secondary"],
            bg=COLORS["bg_dark"],
        )
        self.status_label.pack(pady=(0, 8))

        # ── Buttons ──────────────────────────────────────────────────────────
        self.btn_frame = tk.Frame(self.main_frame, bg=COLORS["bg_dark"])
        self.btn_frame.pack(pady=(0, 5))

        self.restart_btn = tk.Label(
            self.btn_frame, text="↻  Restart", font=self.font_btn,
            fg=COLORS["text_primary"], bg=COLORS["btn_reset"],
            padx=24, pady=10, cursor="hand2",
        )
        self.restart_btn.pack(side="left", padx=6)
        self.restart_btn.bind("<Button-1>", lambda e: self._restart())
        self.restart_btn.bind("<Enter>", lambda e: self.restart_btn.configure(bg=COLORS["btn_reset_hover"]))
        self.restart_btn.bind("<Leave>", lambda e: self.restart_btn.configure(bg=COLORS["btn_reset"]))

        self.new_text_btn = tk.Label(
            self.btn_frame, text="⟳  New Text", font=self.font_btn,
            fg=COLORS["bg_dark"], bg=COLORS["accent"],
            padx=24, pady=10, cursor="hand2",
        )
        self.new_text_btn.pack(side="left", padx=6)
        self.new_text_btn.bind("<Button-1>", lambda e: self._new_text())
        self.new_text_btn.bind("<Enter>", lambda e: self.new_text_btn.configure(bg=COLORS["accent_hover"]))
        self.new_text_btn.bind("<Leave>", lambda e: self.new_text_btn.configure(bg=COLORS["accent"]))
        
        self.stop_btn = tk.Label(
            self.btn_frame, text="⏹ Stop Test", font=self.font_btn,
            fg=COLORS["text_primary"], bg=COLORS["btn_stop"],
            padx=24, pady=10, cursor="hand2",
        )
        self.stop_btn.bind("<Button-1>", lambda e: self._finish_test(self.input_text.get("1.0", "end-1c"), force_stop=True))
        self.stop_btn.bind("<Enter>", lambda e: self.stop_btn.configure(bg=COLORS["btn_stop_hover"]))
        self.stop_btn.bind("<Leave>", lambda e: self.stop_btn.configure(bg=COLORS["btn_stop"]))

        self._set_mode("Standard")

    # ── Dynamic Controls Building ───────────────────────────────────────────
    def _build_dynamic_controls(self):
        # Clear existing controls
        for widget in self.dynamic_controls_frame.winfo_children():
            widget.destroy()

        if self.mode == "Standard":
            self._build_standard_controls()
        elif self.mode == "Custom":
            self._build_custom_controls()
        elif self.mode == "Wikipedia":
            self._build_wikipedia_controls()
            
        # Add Timer selector (common to all modes)
        self._build_timer_selector()
        
    def _build_standard_controls(self):
        diff_frame = tk.Frame(self.dynamic_controls_frame, bg=COLORS["bg_dark"])
        diff_frame.pack(side="left", fill="y", pady=5)

        tk.Label(
            diff_frame, text="DIFFICULTY", font=self.font_diff_label,
            fg=COLORS["text_secondary"], bg=COLORS["bg_dark"],
        ).pack(side="left", padx=(0, 8))

        self.diff_buttons = {}
        for diff in ["Easy", "Medium", "Hard"]:
            btn = tk.Label(
                diff_frame, text=diff, font=self.font_diff_label,
                fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                padx=14, pady=5, cursor="hand2",
            )
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, d=diff: self._set_difficulty(d))
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=COLORS["border"]))
            btn.bind("<Leave>", lambda e, b=btn, d=diff: self._style_diff_btn(b, d))
            self.diff_buttons[diff] = btn

        self._highlight_difficulty()

    def _build_custom_controls(self):
        custom_frame = tk.Frame(self.dynamic_controls_frame, bg=COLORS["bg_dark"])
        custom_frame.pack(side="left", fill="both", expand=True, pady=5)
        
        tk.Label(
            custom_frame, text="PASTE TEXT:", font=self.font_diff_label,
            fg=COLORS["text_secondary"], bg=COLORS["bg_dark"],
        ).pack(side="left", padx=(0, 8))
        
        self.custom_entry = tk.Entry(
            custom_frame, bg=COLORS["bg_card"], fg=COLORS["text_primary"],
            font=self.font_subtitle, relief="flat", insertbackground=COLORS["cursor_color"]
        )
        self.custom_entry.pack(side="left", fill="x", expand=True, padx=5, ipady=3)
        self.custom_entry.insert(0, "Paste your custom sentence or paragraph here...")
        self.custom_entry.bind("<FocusIn>", lambda e: self._clear_placeholder(self.custom_entry))
        
        set_btn = tk.Button(
            custom_frame, text="Set Text", bg=COLORS["accent"], fg=COLORS["bg_dark"],
            font=self.font_diff_label, relief="flat", cursor="hand2",
            command=self._apply_custom_text
        )
        set_btn.pack(side="left", padx=5)

    def _build_wikipedia_controls(self):
        wiki_frame = tk.Frame(self.dynamic_controls_frame, bg=COLORS["bg_dark"])
        wiki_frame.pack(side="left", fill="y", pady=5)
        
        tk.Label(
            wiki_frame, text="SENTENCES:", font=self.font_diff_label,
            fg=COLORS["text_secondary"], bg=COLORS["bg_dark"],
        ).pack(side="left", padx=(0, 8))
        
        self.wiki_spinbox = tk.Spinbox(
            wiki_frame, from_=1, to=20, width=5, font=self.font_subtitle,
            bg=COLORS["bg_card"], fg=COLORS["text_primary"], relief="flat",
            buttonbackground=COLORS["border"]
        )
        self.wiki_spinbox.delete(0, "end")
        self.wiki_spinbox.insert(0, "3")
        self.wiki_spinbox.pack(side="left", padx=5)
        
        fetch_btn = tk.Button(
            wiki_frame, text="Fetch Random Article", bg=COLORS["accent"], fg=COLORS["bg_dark"],
            font=self.font_diff_label, relief="flat", cursor="hand2",
            command=self._fetch_wikipedia
        )
        fetch_btn.pack(side="left", padx=5)

    def _build_timer_selector(self):
        timer_frame = tk.Frame(self.dynamic_controls_frame, bg=COLORS["bg_dark"])
        timer_frame.pack(side="right", fill="y", pady=5)

        tk.Label(
            timer_frame, text="TIMER", font=self.font_diff_label,
            fg=COLORS["text_secondary"], bg=COLORS["bg_dark"],
        ).pack(side="left", padx=(0, 8))

        self.timer_buttons = {}
        for sec in ["30s", "60s", "120s", "5m", "15m", "1h", "Unlimited"]:
            btn = tk.Label(
                timer_frame, text=sec, font=self.font_diff_label,
                fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                padx=8, pady=5, cursor="hand2",
            )
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, s=sec: self._set_timer(s))
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=COLORS["border"]))
            btn.bind("<Leave>", lambda e, b=btn, s=sec: self._style_timer_btn(b, s))
            self.timer_buttons[sec] = btn

        self._highlight_timer()

    def _clear_placeholder(self, entry):
        if entry.get() == "Paste your custom sentence or paragraph here...":
            entry.delete(0, "end")

    # ── Mode Handlers ────────────────────────────────────────────────────────
    def _set_mode(self, mode):
        self.mode = mode
        self._highlight_mode()
        self._build_dynamic_controls()
        
        if mode == "Standard":
            self.new_text_btn.configure(state="normal")
            self._new_text()
        elif mode == "Custom":
            self.new_text_btn.configure(state="disabled")
            self.target_text = "Please paste a text and click 'Set Text'."
            self._restart()
        elif mode == "Wikipedia":
            self.new_text_btn.configure(state="normal")
            self.target_text = "Click 'Fetch Random Article' or 'New Text' to pull from Wikipedia."
            self._restart()

    def _highlight_mode(self):
        for m, btn in self.mode_buttons.items():
            if m == self.mode:
                btn.configure(bg=COLORS["accent"], fg=COLORS["bg_dark"])
            else:
                btn.configure(bg=COLORS["bg_card"], fg=COLORS["text_primary"])

    def _style_mode_btn(self, btn, mode):
        if mode == self.mode:
            btn.configure(bg=COLORS["accent"], fg=COLORS["bg_dark"])
        else:
            btn.configure(bg=COLORS["bg_card"], fg=COLORS["text_primary"])

    def _set_difficulty(self, diff):
        self.difficulty = diff
        self._highlight_difficulty()
        self._new_text()

    def _highlight_difficulty(self):
        if not hasattr(self, 'diff_buttons'): return
        for d, btn in self.diff_buttons.items():
            if d == self.difficulty:
                btn.configure(bg=COLORS["accent"], fg=COLORS["bg_dark"])
            else:
                btn.configure(bg=COLORS["bg_card"], fg=COLORS["text_primary"])

    def _style_diff_btn(self, btn, diff):
        if diff == self.difficulty:
            btn.configure(bg=COLORS["accent"], fg=COLORS["bg_dark"])
        else:
            btn.configure(bg=COLORS["bg_card"], fg=COLORS["text_primary"])

    def _set_timer(self, setting):
        self.timer_setting = setting
        self._highlight_timer()
        self._restart()

    def _get_timer_seconds(self):
        if self.timer_setting == "Unlimited": return 0
        if self.timer_setting.endswith('s'): return int(self.timer_setting[:-1])
        if self.timer_setting.endswith('m'): return int(self.timer_setting[:-1]) * 60
        if self.timer_setting.endswith('h'): return int(self.timer_setting[:-1]) * 3600
        return 60

    def _highlight_timer(self):
        if not hasattr(self, 'timer_buttons'): return
        for s, btn in self.timer_buttons.items():
            if s == self.timer_setting:
                btn.configure(bg=COLORS["accent"], fg=COLORS["bg_dark"])
            else:
                btn.configure(bg=COLORS["bg_card"], fg=COLORS["text_primary"])

    def _style_timer_btn(self, btn, sec):
        if sec == self.timer_setting:
            btn.configure(bg=COLORS["accent"], fg=COLORS["bg_dark"])
        else:
            btn.configure(bg=COLORS["bg_card"], fg=COLORS["text_primary"])

    # ── Text Fetching & Setting ──────────────────────────────────────────────
    def _new_text(self):
        if self.mode == "Standard":
            texts = SAMPLE_TEXTS.get(self.difficulty, SAMPLE_TEXTS["Medium"])
            self.target_text = random.choice(texts)
            self._restart()
        elif self.mode == "Wikipedia":
            self._fetch_wikipedia()
            
    def _apply_custom_text(self):
        text = self.custom_entry.get().strip()
        if not text or text == "Paste your custom sentence or paragraph here...":
            messagebox.showwarning("Empty Text", "Please paste some text first.")
            return
        self.target_text = text
        self._restart()

    def _fetch_wikipedia(self):
        self.status_label.configure(text="Fetching Wikipedia article...", fg=COLORS["accent"])
        self.root.update()
        
        try:
            count = int(self.wiki_spinbox.get())
            if count <= 0: count = 3
        except ValueError:
            count = 3
            
        def fetch():
            text = fetch_wikipedia_sentences(count)
            self.root.after(0, self._on_wiki_fetched, text)
            
        threading.Thread(target=fetch, daemon=True).start()

    def _on_wiki_fetched(self, text):
        self.target_text = text
        self._restart()

    # ── Test Lifecycle ───────────────────────────────────────────────────────
    def _restart(self):
        self.start_time = None
        self.timer_running = False
        self.time_elapsed = 0
        self.test_finished = False
        
        self.total_correct_chars = 0
        self.total_typed_chars = 0

        # Reset input
        self.input_text.configure(state="normal")
        self.input_text.delete("1.0", "end")
        self.input_text.focus_set()

        # Reset stats UI
        self.wpm_value.configure(text="0")
        self.acc_value.configure(text="100%", fg=COLORS["correct"])
        self.char_value.configure(text="0/0")
        self.status_label.configure(text="Start typing to begin the test...", fg=COLORS["text_secondary"])
        
        if self.timer_setting == "Unlimited":
            self.time_title_label.configure(text="TIME ELAPSED")
            self.time_value.configure(text="0s")
            self.stop_btn.pack_forget() # Hide until started
        else:
            self.time_title_label.configure(text="TIME LEFT")
            self.time_value.configure(text=f"{self._get_timer_seconds()}s")
            self.stop_btn.pack_forget() # Don't need stop button in timed mode

        # Render passage
        self._render_passage("")

    def _render_passage(self, typed):
        self.passage_display.configure(state="normal")
        self.passage_display.delete("1.0", "end")
        self.passage_display.insert("1.0", self.target_text)

        # Remove all tags
        for tag in ("correct", "incorrect", "current", "untyped"):
            self.passage_display.tag_remove(tag, "1.0", "end")

        typed_len = len(typed)

        for i, char in enumerate(self.target_text):
            start = f"1.{i}"
            end = f"1.{i + 1}"

            if i < typed_len:
                if typed[i] == char:
                    self.passage_display.tag_add("correct", start, end)
                else:
                    self.passage_display.tag_add("incorrect", start, end)
            elif i == typed_len:
                self.passage_display.tag_add("current", start, end)
            else:
                self.passage_display.tag_add("untyped", start, end)

        self.passage_display.configure(state="disabled")

    # ── Input Handling ───────────────────────────────────────────────────────
    def _on_key_press(self, event):
        if self.test_finished:
            return "break"

        # Prevent pasting
        if event.keysym == "v" and (event.state & 0x4):  # Ctrl+V
            return "break"

    def _on_key_release(self, event):
        if self.test_finished:
            return
            
        # Ignore empty target text
        if not self.target_text or self.target_text.startswith("Please paste") or self.target_text.startswith("Click 'Fetch"):
            return

        typed = self.input_text.get("1.0", "end-1c")

        # Start timer on first keystroke
        if not self.timer_running and typed:
            self.start_time = time.time()
            self.timer_running = True
            
            if self.timer_setting == "Unlimited":
                self.stop_btn.pack(side="left", padx=6)
                
            self._tick_timer()

        self._render_passage(typed)
        self._update_stats(typed)

        # Check completion of current passage
        if len(typed) >= len(self.target_text):
            if self.timer_setting == "Unlimited":
                self._load_next_unlimited_passage(typed)
            else:
                self._finish_test(typed)

    def _load_next_unlimited_passage(self, typed):
        # Tally up the score for the current passage
        correct = sum(1 for i in range(min(len(typed), len(self.target_text))) if typed[i] == self.target_text[i])
        self.total_correct_chars += correct
        self.total_typed_chars += len(typed)
        
        # Clear input box
        self.input_text.delete("1.0", "end")
        
        # Generate new text based on mode
        if self.mode == "Standard":
            texts = SAMPLE_TEXTS.get(self.difficulty, SAMPLE_TEXTS["Medium"])
            self.target_text = random.choice(texts)
            self._render_passage("")
        elif self.mode == "Wikipedia":
            self.target_text = "Fetching next Wikipedia article..."
            self._render_passage("")
            self._fetch_wikipedia()
        elif self.mode == "Custom":
            # For custom, just let them retype the same thing over and over if they want
            self._render_passage("")

    def _tick_timer(self):
        if not self.timer_running:
            return

        elapsed = time.time() - self.start_time
        self.time_elapsed = elapsed
        
        if self.timer_setting == "Unlimited":
            # Count up
            mins, secs = divmod(int(elapsed), 60)
            if mins > 0:
                self.time_value.configure(text=f"{mins}m {secs}s", fg=COLORS["text_primary"])
            else:
                self.time_value.configure(text=f"{secs}s", fg=COLORS["text_primary"])
        else:
            # Count down
            duration = self._get_timer_seconds()
            remaining = max(0, duration - int(elapsed))
            
            mins, secs = divmod(remaining, 60)
            if mins > 0:
                self.time_value.configure(text=f"{mins}m {secs}s")
            else:
                self.time_value.configure(text=f"{secs}s")

            # Color the timer when running low
            if remaining <= 10:
                self.time_value.configure(fg=COLORS["incorrect"])
            elif remaining <= 20:
                self.time_value.configure(fg=COLORS["accent"])
            else:
                self.time_value.configure(fg=COLORS["text_primary"])

            if remaining <= 0:
                typed = self.input_text.get("1.0", "end-1c")
                self._finish_test(typed)
                return

        self.root.after(200, self._tick_timer)

    def _update_stats(self, typed):
        if not typed and self.total_typed_chars == 0:
            self.wpm_value.configure(text="0")
            self.acc_value.configure(text="100%", fg=COLORS["correct"])
            self.char_value.configure(text="0/0")
            return

        # Calculate correct characters for current passage
        current_correct = 0
        current_total = len(typed)
        for i in range(min(current_total, len(self.target_text))):
            if typed[i] == self.target_text[i]:
                current_correct += 1
                
        total_correct = self.total_correct_chars + current_correct
        total_typed = self.total_typed_chars + current_total

        # Accuracy
        accuracy = (total_correct / total_typed * 100) if total_typed > 0 else 100
        acc_text = f"{accuracy:.0f}%"

        if accuracy >= 95:
            acc_color = COLORS["correct"]
        elif accuracy >= 80:
            acc_color = COLORS["accent"]
        else:
            acc_color = COLORS["incorrect"]

        self.acc_value.configure(text=acc_text, fg=acc_color)
        self.char_value.configure(text=f"{total_correct}/{total_typed}")

        # WPM
        if self.start_time:
            elapsed = max(time.time() - self.start_time, 1)
            minutes = elapsed / 60
            net_wpm = max(0, (total_correct / 5) / minutes)
            self.wpm_value.configure(text=f"{int(net_wpm)}")

    def _finish_test(self, typed, force_stop=False):
        self.test_finished = True
        self.timer_running = False
        self.input_text.configure(state="disabled")
        
        if self.timer_setting == "Unlimited":
            self.stop_btn.pack_forget()

        elapsed = time.time() - self.start_time if self.start_time else 1
        minutes = elapsed / 60

        current_total = len(typed)
        current_correct = sum(
            1 for i in range(min(current_total, len(self.target_text)))
            if typed[i] == self.target_text[i]
        )
        
        total_correct = self.total_correct_chars + current_correct
        total_typed = self.total_typed_chars + current_total
        
        accuracy = (total_correct / total_typed * 100) if total_typed > 0 else 0
        net_wpm = max(0, (total_correct / 5) / minutes)

        self.wpm_value.configure(text=f"{int(net_wpm)}")

        # Final status message
        if net_wpm >= 80:
            msg = "🏆  Incredible! You're a speed demon!"
            color = COLORS["accent"]
        elif net_wpm >= 60:
            msg = "🔥  Great job! Above average typing speed!"
            color = COLORS["correct"]
        elif net_wpm >= 40:
            msg = "👍  Good effort! Keep practicing!"
            color = COLORS["text_primary"]
        else:
            msg = "💪  Keep going! Practice makes perfect!"
            color = COLORS["text_secondary"]
            
        time_str = "Unlimited" if self.timer_setting == "Unlimited" else self.timer_setting

        self.status_label.configure(
            text=f"Test Complete! ({time_str})  —  {int(net_wpm)} WPM  |  {accuracy:.1f}% Accuracy  |  {msg}",
            fg=color,
        )

        self._flash_stat(self.wpm_value, 0)

    def _flash_stat(self, widget, count):
        if count >= 6:
            widget.configure(fg=COLORS["accent"])
            return
        color = COLORS["accent"] if count % 2 == 0 else COLORS["bg_dark"]
        widget.configure(fg=color)
        self.root.after(200, self._flash_stat, widget, count + 1)


if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSpeedTester(root)
    root.mainloop()
