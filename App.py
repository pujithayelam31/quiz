import tkinter as tk
from tkinter import font as tkfont
import sys
import os
import threading
import time

sys.path.insert(0, os.path.dirname(__file__))
from logic import load_questions, check_answer, calculate_score, get_difficulty_config

# ─── THEME ────────────────────────────────────────────────────────────────────
BG       = "#0a0a0f"
CARD_BG  = "#12121a"
BORDER   = "#1e1e2e"
TEXT     = "#e8e8f0"
SUBTEXT  = "#6e6e8e"
WHITE    = "#ffffff"

OPTION_BG      = "#16162a"
OPTION_HOVER   = "#1e1e3a"
OPTION_CORRECT = "#0d3320"
OPTION_WRONG   = "#3a0d0d"

# ─── APP ──────────────────────────────────────────────────────────────────────
class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QuizMaster Pro")
        self.configure(bg=BG)

        # Fullscreen
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.toggle_fullscreen())
        self.bind("<F11>",    lambda e: self.toggle_fullscreen())
        self._is_fullscreen = True

        # State
        self.difficulty   = tk.StringVar(value="easy")
        self.questions    = []
        self.current_idx  = 0
        self.score        = 0
        self.answered     = False
        self.timer_val    = 0
        self.timer_thread = None
        self.timer_running = False

        # Fonts
        self.f_title   = tkfont.Font(family="Courier New", size=36, weight="bold")
        self.f_sub     = tkfont.Font(family="Courier New", size=14)
        self.f_label   = tkfont.Font(family="Courier New", size=11)
        self.f_q       = tkfont.Font(family="Courier New", size=18, weight="bold")
        self.f_opt     = tkfont.Font(family="Courier New", size=14)
        self.f_btn     = tkfont.Font(family="Courier New", size=13, weight="bold")
        self.f_score   = tkfont.Font(family="Courier New", size=48, weight="bold")
        self.f_grade   = tkfont.Font(family="Courier New", size=22, weight="bold")
        self.f_stat    = tkfont.Font(family="Courier New", size=16)

        self.show_home()

    # ── FULLSCREEN TOGGLE ──────────────────────────────────────────────────────
    def toggle_fullscreen(self):
        self._is_fullscreen = not self._is_fullscreen
        self.attributes("-fullscreen", self._is_fullscreen)

    # ── CLEAR WINDOW ──────────────────────────────────────────────────────────
    def clear(self):
        self.stop_timer()
        for w in self.winfo_children():
            w.destroy()

    # ── EXIT BUTTON ───────────────────────────────────────────────────────────
    def add_exit_btn(self, parent):
        bar = tk.Frame(parent, bg=BG)
        bar.pack(fill="x", padx=20, pady=(10, 0))

        tk.Button(
            bar, text="✕  EXIT", font=self.f_label,
            bg="#1a0a0a", fg="#f44336",
            activebackground="#2a1010", activeforeground="#ff6659",
            bd=0, padx=16, pady=6, cursor="hand2",
            command=self.destroy
        ).pack(side="right")

        tk.Button(
            bar, text="⛶  FULLSCREEN", font=self.f_label,
            bg="#0a0a1a", fg=SUBTEXT,
            activebackground="#10102a", activeforeground=TEXT,
            bd=0, padx=16, pady=6, cursor="hand2",
            command=self.toggle_fullscreen
        ).pack(side="right", padx=(0, 8))

    # ══════════════════════════════════════════════════════════════════════════
    #  HOME SCREEN
    # ══════════════════════════════════════════════════════════════════════════
    def show_home(self):
        self.clear()
        self.configure(bg=BG)

        # Exit / fullscreen row
        self.add_exit_btn(self)

        # ── Center wrapper
        center = tk.Frame(self, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        # ── Logo / Title
        tk.Label(center, text="⚡", font=tkfont.Font(size=60), bg=BG, fg="#7c6fff").pack()
        tk.Label(center, text="QUIZMASTER PRO", font=self.f_title,
                 bg=BG, fg=WHITE).pack(pady=(4, 2))
        tk.Label(center, text="Test your knowledge across difficulty levels",
                 font=self.f_sub, bg=BG, fg=SUBTEXT).pack(pady=(0, 40))

        # ── Difficulty selector label
        tk.Label(center, text="SELECT DIFFICULTY", font=self.f_label,
                 bg=BG, fg=SUBTEXT, letter_spacing=4).pack(pady=(0, 12))

        # ── Difficulty cards row
        diff_row = tk.Frame(center, bg=BG)
        diff_row.pack(pady=(0, 40))

        difficulties = [
            ("easy",   "🟢", "EASY",   "#00e676", "30s / question\nRelaxed paced"),
            ("medium", "🟡", "MEDIUM", "#ffeb3b", "20s / question\nNormal paced"),
            ("hard",   "🔴", "HARD",   "#f44336", "15s / question\nSpeed round"),
        ]

        self._diff_frames = {}
        for val, emoji, label, color, desc in difficulties:
            frame = tk.Frame(
                diff_row, bg=CARD_BG, bd=0,
                highlightthickness=2,
                highlightbackground=BORDER,
                cursor="hand2", width=200, height=170
            )
            frame.pack(side="left", padx=14, ipadx=20, ipady=20)
            frame.pack_propagate(False)

            tk.Label(frame, text=emoji, font=tkfont.Font(size=28),
                     bg=CARD_BG, fg=color).pack(pady=(20, 4))
            tk.Label(frame, text=label, font=tkfont.Font(family="Courier New", size=15, weight="bold"),
                     bg=CARD_BG, fg=color).pack()
            tk.Label(frame, text=desc, font=tkfont.Font(family="Courier New", size=10),
                     bg=CARD_BG, fg=SUBTEXT, justify="center").pack(pady=(6, 0))

            self._diff_frames[val] = (frame, color)

            # Click binding
            def on_click(v=val):
                self.difficulty.set(v)
                self._update_diff_highlight()
            frame.bind("<Button-1>", lambda e, v=val: on_click(v))
            for child in frame.winfo_children():
                child.bind("<Button-1>", lambda e, v=val: on_click(v))

        self._update_diff_highlight()

        # ── Start button
        start_btn = tk.Button(
            center, text="▶   START QUIZ",
            font=self.f_btn,
            bg="#7c6fff", fg=WHITE,
            activebackground="#9b8fff", activeforeground=WHITE,
            bd=0, padx=40, pady=16,
            cursor="hand2",
            command=self.start_quiz
        )
        start_btn.pack()

        # Hover effect
        start_btn.bind("<Enter>", lambda e: start_btn.config(bg="#9b8fff"))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg="#7c6fff"))

        # ── Keyboard shortcut hint
        tk.Label(center, text="ESC to toggle fullscreen  •  F11 to toggle fullscreen",
                 font=tkfont.Font(family="Courier New", size=10),
                 bg=BG, fg="#333355").pack(pady=(30, 0))

    def _update_diff_highlight(self):
        selected = self.difficulty.get()
        for val, (frame, color) in self._diff_frames.items():
            if val == selected:
                frame.config(highlightbackground=color, bg="#1a1a2e")
                for c in frame.winfo_children():
                    c.config(bg="#1a1a2e")
            else:
                frame.config(highlightbackground=BORDER, bg=CARD_BG)
                for c in frame.winfo_children():
                    c.config(bg=CARD_BG)

    # ══════════════════════════════════════════════════════════════════════════
    #  START QUIZ
    # ══════════════════════════════════════════════════════════════════════════
    def start_quiz(self):
        diff = self.difficulty.get()
        self.questions  = load_questions(diff)
        self.current_idx = 0
        self.score       = 0
        self.diff_config = get_difficulty_config(diff)
        self.show_question()

    # ══════════════════════════════════════════════════════════════════════════
    #  QUESTION SCREEN
    # ══════════════════════════════════════════════════════════════════════════
    def show_question(self):
        self.clear()
        self.answered = False
        q_data = self.questions[self.current_idx]
        total  = len(self.questions)
        color  = self.diff_config["color"]

        # ── Top bar
        topbar = tk.Frame(self, bg=BG, pady=12)
        topbar.pack(fill="x", padx=30)

        # Difficulty badge
        tk.Label(topbar,
                 text=f"  {self.diff_config['emoji']} {self.diff_config['label']}  ",
                 font=self.f_label, bg=color, fg="#000000", padx=8, pady=4).pack(side="left")

        # Score
        tk.Label(topbar, text=f"Score: {self.score}/{self.current_idx}",
                 font=self.f_label, bg=BG, fg=SUBTEXT).pack(side="left", padx=20)

        # Exit
        self.add_exit_btn(topbar)

        # ── Progress bar
        prog_bg = tk.Frame(self, bg=BORDER, height=6)
        prog_bg.pack(fill="x", padx=30, pady=(0, 4))
        prog_bg.pack_propagate(False)
        prog_pct = (self.current_idx / total)
        prog_fill = tk.Frame(prog_bg, bg=color, height=6)
        prog_fill.place(relwidth=prog_pct, relheight=1)

        # ── Progress text
        tk.Label(self, text=f"Question {self.current_idx + 1} of {total}",
                 font=self.f_label, bg=BG, fg=SUBTEXT).pack(pady=(4, 0))

        # ── Timer
        timer_frame = tk.Frame(self, bg=BG)
        timer_frame.pack(pady=(6, 0))
        self.timer_label = tk.Label(
            timer_frame,
            text=f"⏱ {self.diff_config['time']}s",
            font=tkfont.Font(family="Courier New", size=20, weight="bold"),
            bg=BG, fg=color
        )
        self.timer_label.pack()

        # ── Question card
        q_card = tk.Frame(self, bg=CARD_BG,
                          highlightthickness=1, highlightbackground=BORDER)
        q_card.pack(fill="x", padx=80, pady=20, ipady=24, ipadx=20)

        tk.Label(q_card, text=q_data["question"],
                 font=self.f_q, bg=CARD_BG, fg=WHITE,
                 wraplength=900, justify="center").pack(pady=14, padx=20)

        # ── Options
        opt_frame = tk.Frame(self, bg=BG)
        opt_frame.pack(padx=80, pady=10, fill="x")

        self._opt_btns = []
        opts = q_data["options"]

        for i, opt in enumerate(opts):
            row = i // 2
            col = i % 2
            opt_frame.columnconfigure(col, weight=1)

            btn_frame = tk.Frame(
                opt_frame, bg=OPTION_BG,
                highlightthickness=1, highlightbackground=BORDER,
                cursor="hand2"
            )
            btn_frame.grid(row=row, column=col, padx=10, pady=8, sticky="ew", ipady=12, ipadx=12)

            prefix = ["A", "B", "C", "D"][i]
            lbl = tk.Label(btn_frame,
                           text=f"  {prefix}.  {opt}",
                           font=self.f_opt, bg=OPTION_BG, fg=TEXT,
                           anchor="w", cursor="hand2")
            lbl.pack(fill="x", padx=10, pady=6)

            def on_click(selected=opt, b=btn_frame, l=lbl):
                self.handle_answer(selected, b, l, q_data)

            def on_enter(e, b=btn_frame, l=lbl):
                if not self.answered:
                    b.config(bg=OPTION_HOVER)
                    l.config(bg=OPTION_HOVER)

            def on_leave(e, b=btn_frame, l=lbl):
                if not self.answered:
                    b.config(bg=OPTION_BG)
                    l.config(bg=OPTION_BG)

            btn_frame.bind("<Button-1>", lambda e, s=opt, b=btn_frame, l=lbl: self.handle_answer(s, b, l, q_data))
            lbl.bind("<Button-1>",       lambda e, s=opt, b=btn_frame, l=lbl: self.handle_answer(s, b, l, q_data))
            btn_frame.bind("<Enter>", on_enter)
            btn_frame.bind("<Leave>", on_leave)
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)

            self._opt_btns.append((btn_frame, lbl, opt))

        # ── Feedback label
        self.feedback_label = tk.Label(self, text="", font=self.f_sub, bg=BG, fg=TEXT)
        self.feedback_label.pack(pady=8)

        # ── Next button (hidden initially)
        self.next_btn = tk.Button(
            self, text="NEXT QUESTION  →",
            font=self.f_btn,
            bg="#7c6fff", fg=WHITE,
            activebackground="#9b8fff",
            bd=0, padx=36, pady=14, cursor="hand2",
            command=self.next_question
        )
        self.next_btn.pack_forget()

        # Start countdown
        self.start_timer(self.diff_config["time"], q_data)

    # ── Timer ──────────────────────────────────────────────────────────────────
    def start_timer(self, seconds, q_data):
        self.timer_running = True
        self.timer_val = seconds

        def countdown():
            while self.timer_val > 0 and self.timer_running:
                time.sleep(1)
                self.timer_val -= 1
                if not self.timer_running:
                    break
                try:
                    color = self.diff_config["color"]
                    if self.timer_val <= 5:
                        color = "#f44336"
                    self.timer_label.config(
                        text=f"⏱ {self.timer_val}s",
                        fg=color
                    )
                except Exception:
                    break
            if self.timer_running and self.timer_val == 0:
                try:
                    self.time_up(q_data)
                except Exception:
                    pass

        self.timer_thread = threading.Thread(target=countdown, daemon=True)
        self.timer_thread.start()

    def stop_timer(self):
        self.timer_running = False

    def time_up(self, q_data):
        if self.answered:
            return
        self.answered = True
        self.stop_timer()
        correct = q_data["answer"]
        self.feedback_label.config(text=f"⏰ Time's up! Correct answer: {correct}", fg="#ff9800")
        # Highlight correct
        for (bf, lbl, opt) in self._opt_btns:
            if opt == correct:
                bf.config(bg=OPTION_CORRECT, highlightbackground="#00e676")
                lbl.config(bg=OPTION_CORRECT, fg="#00e676")
        self.next_btn.pack(pady=(10, 20))

    # ── Answer handling ────────────────────────────────────────────────────────
    def handle_answer(self, selected, btn_frame, lbl, q_data):
        if self.answered:
            return
        self.answered = True
        self.stop_timer()

        correct = q_data["answer"]
        is_correct = check_answer(q_data, selected)

        if is_correct:
            self.score += 1
            btn_frame.config(bg=OPTION_CORRECT, highlightbackground="#00e676")
            lbl.config(bg=OPTION_CORRECT, fg="#00e676")
            self.feedback_label.config(text="✔  Correct!", fg="#00e676")
        else:
            btn_frame.config(bg=OPTION_WRONG, highlightbackground="#f44336")
            lbl.config(bg=OPTION_WRONG, fg="#f44336")
            self.feedback_label.config(text=f"✘  Wrong!  Correct: {correct}", fg="#f44336")
            # Show correct
            for (bf, lb, opt) in self._opt_btns:
                if opt == correct:
                    bf.config(bg=OPTION_CORRECT, highlightbackground="#00e676")
                    lb.config(bg=OPTION_CORRECT, fg="#00e676")

        self.next_btn.pack(pady=(10, 20))

    def next_question(self):
        self.current_idx += 1
        if self.current_idx < len(self.questions):
            self.show_question()
        else:
            self.show_results()

    # ══════════════════════════════════════════════════════════════════════════
    #  RESULTS SCREEN
    # ══════════════════════════════════════════════════════════════════════════
    def show_results(self):
        self.clear()
        data  = calculate_score(self.score, len(self.questions))
        color = data["color"]
        diff  = self.difficulty.get()

        self.add_exit_btn(self)

        center = tk.Frame(self, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Trophy / icon
        tk.Label(center, text="🏁", font=tkfont.Font(size=56), bg=BG).pack()
        tk.Label(center, text="QUIZ COMPLETE", font=self.f_title,
                 bg=BG, fg=WHITE).pack(pady=(8, 4))
        tk.Label(center, text=f"Difficulty: {diff.upper()}",
                 font=self.f_label, bg=BG, fg=SUBTEXT).pack(pady=(0, 30))

        # Score ring
        score_card = tk.Frame(center, bg=CARD_BG,
                              highlightthickness=2, highlightbackground=color)
        score_card.pack(pady=(0, 30), ipadx=60, ipady=30)

        tk.Label(score_card,
                 text=f"{data['correct']}/{data['total']}",
                 font=self.f_score, bg=CARD_BG, fg=color).pack()
        tk.Label(score_card,
                 text=f"{data['percentage']}%",
                 font=tkfont.Font(family="Courier New", size=22),
                 bg=CARD_BG, fg=SUBTEXT).pack()
        tk.Label(score_card,
                 text=data["grade"],
                 font=self.f_grade, bg=CARD_BG, fg=color).pack(pady=(8, 0))

        # Stats row
        stats_frame = tk.Frame(center, bg=BG)
        stats_frame.pack(pady=(0, 30))

        def stat_box(parent, label, val, clr):
            f = tk.Frame(parent, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
            f.pack(side="left", padx=10, ipadx=20, ipady=14)
            tk.Label(f, text=val,   font=self.f_stat, bg=CARD_BG, fg=clr).pack()
            tk.Label(f, text=label, font=self.f_label, bg=CARD_BG, fg=SUBTEXT).pack()

        stat_box(stats_frame, "Correct",   str(data["correct"]),               "#00e676")
        stat_box(stats_frame, "Wrong",     str(data["total"] - data["correct"]), "#f44336")
        stat_box(stats_frame, "Questions", str(data["total"]),                  "#7c6fff")

        # Buttons
        btn_row = tk.Frame(center, bg=BG)
        btn_row.pack()

        tk.Button(
            btn_row, text="↺  PLAY AGAIN",
            font=self.f_btn, bg="#7c6fff", fg=WHITE,
            activebackground="#9b8fff",
            bd=0, padx=30, pady=14, cursor="hand2",
            command=self.start_quiz
        ).pack(side="left", padx=10)

        tk.Button(
            btn_row, text="⌂  HOME",
            font=self.f_btn, bg=CARD_BG, fg=TEXT,
            activebackground=OPTION_HOVER,
            bd=0, padx=30, pady=14, cursor="hand2",
            command=self.show_home
        ).pack(side="left", padx=10)

        tk.Button(
            btn_row, text="✕  EXIT",
            font=self.f_btn, bg="#1a0a0a", fg="#f44336",
            activebackground="#2a1010",
            bd=0, padx=30, pady=14, cursor="hand2",
            command=self.destroy
        ).pack(side="left", padx=10)


# ── ENTRY POINT ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()