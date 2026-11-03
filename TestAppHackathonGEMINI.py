#!/usr/bin/env python3
"""
YouthAI: Growth & Wellbeing Platform
Functional AI Chatbox with Google Gemini API + Local Fallback
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import random
import threading
import queue
import os

# ════════════════════════════════════════════════════════════════
# CHANGE 1 OF 4: Replace OpenAI import with Gemini
# ════════════════════════════════════════════════════════════════
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# ════════════════════════════════════════════════════════════════
# COLORS  (unchanged)
# ════════════════════════════════════════════════════════════════
class C:
    BG="#FFF8F0"; SIDEBAR="#FFF0E8"; CARD="#FFFFFF"; SHADOW="#E8E0D8"
    PINK="#FF8A9E"; PINK_LT="#FFE0E8"; PINK_DK="#E8637E"
    TEAL="#7EC8C8"; TEAL_LT="#E0F5F5"; TEAL_DK="#5AA8A8"
    YELLOW="#FFD166"; YELLOW_LT="#FFF5D6"
    LAV="#B8B5FF"; LAV_LT="#EDEAFF"
    MINT="#98D8AA"; MINT_LT="#E0F8E8"
    PEACH="#FFB7A5"; PEACH_LT="#FFE8E0"
    TEXT="#4A4A6A"; TEXT_LT="#8E8EA0"; TEXT_DK="#2D2D4A"; WHITE="#FFFFFF"
    CHAT_U="#FFE0E8"; CHAT_A="#E0F5F5"
    M1="#FF7F7F"; M2="#FFB7A5"; M3="#FFD166"; M4="#98D8AA"; M5="#7EC8C8"; M6="#B8B5FF"

def darker(c):
    return {C.PINK:C.PINK_DK, C.TEAL:C.TEAL_DK, C.MINT:C.TEAL,
            C.LAV:C.LAV, C.YELLOW:C.PEACH}.get(c, C.PINK_DK)

# ════════════════════════════════════════════════════════════════
# AI SYSTEM PROMPT  (unchanged)
# ════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """You are YouthAI, a friendly, warm, and supportive AI wellbeing buddy 
for university students. Your personality traits:
- Warm and empathetic, like a caring friend
- Use emojis naturally (😊🌟💡🌱💚 but don't overdo it)
- Keep responses concise: 2-4 sentences maximum
- Always supportive, never judgmental
- You specialize in: emotional wellbeing, stress management, career guidance, 
  study tips, motivation, and campus life
- When user seems stressed/sad, acknowledge feelings first, then offer gentle suggestion
- When user is happy, celebrate with them
- For career questions, give practical but encouraging advice
- For study questions, share actionable tips
- Never say "As an AI" — you are YouthAI, their buddy
- If they mention serious mental health concerns (self-harm, suicide), 
  gently encourage them to seek professional help and provide a hotline number
- You know the user is a university student at UKM (National University of Malaysia)
- Address them informally and warmly"""

# ════════════════════════════════════════════════════════════════
# DATA  (unchanged — MOODS, PROGRAMS, CAREERS, CAREER_Q, AI_RESP, TIPS, CAT_COL)
# ════════════════════════════════════════════════════════════════
MOODS = {
    "Terrible":{"emoji":"😢","color":C.M1,"v":1},
    "Bad":     {"emoji":"😟","color":C.M2,"v":2},
    "Okay":    {"emoji":"😐","color":C.M3,"v":3},
    "Good":    {"emoji":"🙂","color":C.M4,"v":4},
    "Great":   {"emoji":"😊","color":C.M5,"v":5},
    "Amazing": {"emoji":"😄","color":C.M6,"v":6},
}

PROGRAMS = [
    {"id":1,"title":"Python Programming Workshop","cat":"Workshop","date":"2025-02-15",
     "time":"2:00 PM – 4:00 PM","loc":"Lab FSKTM 1",
     "desc":"Learn Python basics from scratch. No prior experience needed!","slots":30,"reg":18},
    {"id":2,"title":"Mental Health Awareness Talk","cat":"Wellbeing","date":"2025-02-18",
     "time":"10:00 AM – 12:00 PM","loc":"Dewan Seminar",
     "desc":"Understanding stress management and self-care techniques for students.","slots":100,"reg":65},
    {"id":3,"title":"Campus Run 5K","cat":"Sports","date":"2025-02-20",
     "time":"7:00 AM – 9:00 AM","loc":"Padang UKM",
     "desc":"Join the fun run around campus! All fitness levels welcome.","slots":200,"reg":142},
    {"id":4,"title":"Volunteer: River Cleanup","cat":"Volunteering","date":"2025-02-22",
     "time":"8:00 AM – 1:00 PM","loc":"Sungai Langat",
     "desc":"Help clean up the local river ecosystem. Transportation provided.","slots":50,"reg":32},
    {"id":5,"title":"Career Fair 2025","cat":"Career","date":"2025-02-25",
     "time":"9:00 AM – 5:00 PM","loc":"Dewan Canselori",
     "desc":"Meet employers, explore opportunities, and polish your resume.","slots":500,"reg":280},
    {"id":6,"title":"UI/UX Design Bootcamp","cat":"Workshop","date":"2025-02-28",
     "time":"9:00 AM – 5:00 PM","loc":"Lab FSKTM 2",
     "desc":"Design beautiful interfaces using Figma. Beginners welcome!","slots":25,"reg":25},
    {"id":7,"title":"Open Mic Night","cat":"Social","date":"2025-03-01",
     "time":"7:00 PM – 10:00 PM","loc":"Cafe Kampus",
     "desc":"Share your talent! Sing, poetry, comedy — all acts welcome.","slots":80,"reg":45},
    {"id":8,"title":"Study Skills Seminar","cat":"Academic","date":"2025-03-03",
     "time":"2:00 PM – 4:00 PM","loc":"Dewan Kuliah A",
     "desc":"Learn effective study techniques and time management strategies.","slots":60,"reg":38},
    {"id":9,"title":"Yoga & Mindfulness Session","cat":"Wellbeing","date":"2025-03-05",
     "time":"6:00 AM – 7:30 AM","loc":"Gym UKM",
     "desc":"Start your day with guided yoga and mindfulness meditation.","slots":20,"reg":12},
    {"id":10,"title":"Hackathon: Solve for SDG","cat":"Workshop","date":"2025-03-08",
     "time":"9:00 AM – 9:00 PM","loc":"FSKTM",
     "desc":"48-hour hackathon addressing Sustainable Development Goals.","slots":100,"reg":78},
]

CAREERS = {
    "Technology":{"icon":"💻","color":C.TEAL,
        "roles":["Software Engineer","Data Scientist","UI/UX Designer","DevOps Engineer","Cybersecurity Analyst"],
        "skills":["Python","JavaScript","SQL","Machine Learning","Cloud Computing"],
        "courses":["CS101 Programming","Data Structures","Web Development","AI Fundamentals"]},
    "Business":{"icon":"📊","color":C.YELLOW,
        "roles":["Business Analyst","Marketing Manager","Entrepreneur","Financial Analyst","HR Manager"],
        "skills":["Financial Analysis","Digital Marketing","Project Management","Communication","Leadership"],
        "courses":["Business Fundamentals","Marketing 101","Financial Accounting","Strategic Management"]},
    "Creative Arts":{"icon":"🎨","color":C.LAV,
        "roles":["Graphic Designer","Content Creator","Film Director","Animator","UX Researcher"],
        "skills":["Adobe Creative Suite","Video Editing","Illustration","Storytelling","Design Thinking"],
        "courses":["Digital Art","Multimedia Design","Photography","Creative Writing"]},
    "Science":{"icon":"🔬","color":C.MINT,
        "roles":["Research Scientist","Lab Technician","Environmental Analyst","Pharmacist","Biotechnologist"],
        "skills":["Research Methods","Data Analysis","Lab Techniques","Scientific Writing","Critical Thinking"],
        "courses":["Biology 101","Chemistry","Research Methodology","Statistics"]},
    "Social Impact":{"icon":"💝","color":C.PINK,
        "roles":["Social Worker","Community Manager","NGO Coordinator","Counselor","Policy Analyst"],
        "skills":["Empathy","Community Engagement","Public Speaking","Advocacy","Case Management"],
        "courses":["Psychology","Sociology","Community Development","Public Policy"]},
}

CAREER_Q = [
    {"q":"What excites you the most? 🌟","opts":[
        ("Building & creating with technology","Technology"),("Strategy, plans & making deals","Business"),
        ("Expressing ideas creatively","Creative Arts"),("Discovering how things work","Science"),
        ("Helping others & making a difference","Social Impact")]},
    {"q":"How do you prefer to work? 🛠️","opts":[
        ("Solving problems with code/tools","Technology"),("Leading teams & projects","Business"),
        ("Designing & brainstorming visually","Creative Arts"),("Conducting experiments & analysis","Science"),
        ("Collaborating with people directly","Social Impact")]},
    {"q":"What matters most to you? 💭","opts":[
        ("Innovation & cutting-edge tech","Technology"),("Growth & financial success","Business"),
        ("Creativity & self-expression","Creative Arts"),("Knowledge & discovery","Science"),
        ("Impact & social change","Social Impact")]},
]

AI_RESP = {
    "greeting":["Hey there! 😊 I'm your YouthAI buddy! How are you feeling today?",
        "Hi! 💖 Welcome back! What's on your mind today?",
        "Hello! 🌈 I'm here to help you grow and thrive! How can I support you?"],
    "sad":["I hear you 💙 It sounds like you're going through a tough time. Remember, it's okay to not be okay. Want to talk about what's bothering you?",
        "I'm sorry you're feeling this way 🤗 Take a deep breath. Sometimes writing down what's stressing you helps.",
        "That sounds really hard 💜 You're not alone. Have you tried taking a short break or talking to someone you trust?"],
    "stressed":["Stress can feel overwhelming 😮‍💨 Let's break things down. What's the biggest thing on your plate right now?",
        "I understand the pressure 😰 Try the 5-4-3-2-1 technique: 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste.",
        "When stress hits hard, even small wins matter 🌱 Can you identify one small task you can complete right now?"],
    "happy":["That's wonderful! 🎉 Your positive energy is contagious! What's making you feel so good?",
        "Yay! 😄 I love seeing you happy! Keep riding that wave — what's been the highlight?",
        "Amazing! 🌟 Jot down what's going well so you can revisit it on tougher days."],
    "confused":["Feeling lost is completely normal 🧭 Many students go through this. What areas feel uncertain?",
        "It's okay to not have all the answers 💭 Tell me more — talking it out often helps clarify things.",
        "Uncertainty is where growth happens 🌱 What if we list out your options together?"],
    "career":["Great question about careers! 🎯 Try our Career Guide — it matches interests to paths. What fields interest you?",
        "Career decisions are big! 🚀 What are your top 3 interests or skills?",
        "I'd love to help with career planning! 💼 What matters most — passion, stability, growth, or impact?"],
    "study":["Study challenges are super common! 📚 Try Pomodoro: 25 min focus, 5 min break. What subject?",
        "You've got this! 📝 Starting is the hardest part. Break your task into smaller chunks.",
        "Academic pressure is real 😅 Make sure you're also resting. Have you tried studying with a group?"],
    "default":["That's interesting! 😊 Tell me more — I'm here to listen and help.",
        "Thanks for sharing 💚 How can I help? Wellbeing, career guidance, or campus activities?",
        "I appreciate you telling me! 🌻 I'm your buddy for wellbeing, career, and campus life."],
}

TIPS = [
    "💡 Take a 5-minute break every hour to stretch and breathe!",
    "🌟 Write down 3 things you're grateful for today",
    "🌱 Growth happens outside your comfort zone",
    "💤 Aim for 7-8 hours of sleep tonight",
    "🚶 A 15-minute walk boosts mood and creativity",
    "📱 Try a digital detox for 1 hour today",
    "📚 Reading for 20 minutes reduces stress by 68%",
    "🧘 Deep breathing: 4 sec in, 7 hold, 8 out",
    "🎯 Set one small, achievable goal for today",
    "💬 Reach out to someone you haven't talked to in a while",
]

CAT_COL = {"Workshop":C.TEAL,"Wellbeing":C.PINK,"Sports":C.MINT,
           "Volunteering":C.LAV,"Career":C.YELLOW,"Social":C.PEACH,"Academic":C.TEAL_DK}

# ════════════════════════════════════════════════════════════════
# HELPERS  (unchanged)
# ════════════════════════════════════════════════════════════════
def detect_mood(text):
    t = text.lower()
    cats = [("sad",["sad","cry","depressed","lonely","alone","heartbroken","hurt","down","unhappy","miss"]),
            ("stressed",["stress","overwhelm","anxious","worried","panic","pressure","tired","exhausted","burnout","headache"]),
            ("happy",["happy","great","wonderful","amazing","fantastic","excited","joy","love","awesome","good"]),
            ("confused",["confused","lost","uncertain","unsure","don't know","clueless","undecided"]),
            ("career",["career","job","work","profession","future","employ","intern","resume","interview"]),
            ("study",["study","exam","assignment","lecture","homework","class","grade","gpa","test","deadline"])]
    for cat, kws in cats:
        if any(w in t for w in kws): return cat
    return "default"

def make_card(parent, bg=C.CARD, c_pad=16, shadow=True, **kw):
    if shadow:
        outer = tk.Frame(parent, bg=C.SHADOW, padx=2, pady=2)
        outer.pack(**kw)
        inner = tk.Frame(outer, bg=bg, padx=c_pad, pady=c_pad)
        inner.pack(fill="both", expand=True)
        return inner
    f = tk.Frame(parent, bg=bg, padx=c_pad, pady=c_pad)
    f.pack(**kw)
    return f

def hover_btn(parent, text, color, command, fg=C.WHITE, fs=11):
    dk = darker(color)
    f = tk.Frame(parent, bg=color, cursor="hand2"); f.pack(pady=(6,0))
    lbl = tk.Label(f, text=text, bg=color, fg=fg, font=("Segoe UI",fs,"bold"),
                   padx=20, pady=8, cursor="hand2"); lbl.pack()
    for w in (f, lbl):
        w.bind("<Enter>", lambda e, l=lbl, d=dk: l.configure(bg=d))
        w.bind("<Leave>", lambda e, l=lbl, c=color: l.configure(bg=c))
    lbl.bind("<Button-1>", lambda e, cmd=command: cmd())
    return f

# ════════════════════════════════════════════════════════════════
# CHANGE 2 OF 4: Rewrite ChatEngine for Gemini API
# ════════════════════════════════════════════════════════════════
class ChatEngine:
    """Handles AI responses — Google Gemini API when available, local fallback otherwise."""

    def __init__(self):
        # Keep credentials outside source control; the profile field also accepts a key.
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = "gemini-3-flash-preview"          # Gemini model name
        self.response_queue = queue.Queue()
        self._typing_active = False

    def is_api_ready(self):
        return bool(self.api_key and self.api_key != "YOUR_GEMINI_API_KEY_HERE" and HAS_GEMINI)
        # ↑ also checks that you've actually replaced the placeholder

    def get_response_async(self, user_msg, chat_history):
        """Start getting a response in a background thread."""
        self.response_queue = queue.Queue()
        t = threading.Thread(target=self._worker, args=(user_msg, chat_history), daemon=True)
        t.start()

    def _worker(self, user_msg, chat_history):
        if self.is_api_ready():
            try:
                # ── Configure Gemini ──
                genai.configure(api_key=self.api_key)

                # Build chat history for Gemini format
                # Gemini uses "user" and "model" roles (not "assistant")
                gemini_history = []
                for sender, msg in chat_history[-10:]:
                    role = "model" if sender == "ai" else "user"
                    gemini_history.append({"role": role, "parts": [msg]})

                # Create model with system instruction
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=SYSTEM_PROMPT,
                )

                # Start chat with history context
                chat = model.start_chat(history=gemini_history)

                # Send the user's message
                response = chat.send_message(user_msg)

                # Extract text from response
                result = response.text.strip()

            except Exception as e:
                result = f"Oops, I had a small hiccup 😅 ({str(e)[:40]}). Using local mode for now..."
                result += "\n\n" + random.choice(AI_RESP.get(detect_mood(user_msg), AI_RESP["default"]))
        else:
            # Local fallback (keyword matching)
            import time; time.sleep(0.6)
            result = random.choice(AI_RESP.get(detect_mood(user_msg), AI_RESP["default"]))
        self.response_queue.put(result)

    def poll(self):
        """Non-blocking check for response. Returns string or None."""
        try:
            return self.response_queue.get_nowait()
        except queue.Empty:
            return None


# ════════════════════════════════════════════════════════════════
# LOGIN SCREEN  (unchanged)
# ════════════════════════════════════════════════════════════════
class LoginScreen:
    def __init__(self, root, on_login):
        self.root = root; self.on_login = on_login
        self.frame = tk.Frame(root, bg=C.BG); self.frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(self.frame, bg=C.BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self._draw_bubbles()
        self.card = tk.Frame(self.canvas, bg=C.CARD, padx=44, pady=32)
        self.cw = self.canvas.create_window(550, 350, window=self.card, anchor="center")
        self._build(); root.bind("<Configure>", self._resize)

    def _resize(self, e): self.canvas.coords(self.cw, e.width//2, e.height//2)

    def _draw_bubbles(self):
        rng = random.Random(42)
        for _ in range(20):
            x, y, r = rng.randint(20,1080), rng.randint(20,680), rng.randint(10,40)
            col = rng.choice([C.PINK_LT,C.TEAL_LT,C.YELLOW_LT,C.LAV_LT,C.MINT_LT,C.PEACH_LT])
            self.canvas.create_oval(x-r,y-r,x+r,y+r,fill=col,outline="")

    def _build(self):
        tk.Label(self.card, text="☁️  YouthAI  ☁️", bg=C.CARD, fg=C.PINK,
                 font=("Segoe UI",28,"bold")).pack(pady=(0,2))
        tk.Label(self.card, text="Growth & Wellbeing Platform", bg=C.CARD, fg=C.TEXT_LT,
                 font=("Segoe UI",11)).pack(pady=(0,24))
        uf = tk.Frame(self.card, bg=C.PINK_LT, padx=14, pady=8); uf.pack(fill="x", pady=(0,8))
        tk.Label(uf, text="👤", bg=C.PINK_LT, font=("Segoe UI",14)).pack(side="left")
        self.u_ent = tk.Entry(uf, bg=C.PINK_LT, fg=C.TEXT, font=("Segoe UI",12),
                              relief="flat", insertbackground=C.TEXT)
        self.u_ent.pack(side="left", fill="x", expand=True, padx=(8,0)); self.u_ent.insert(0, "Student")
        pf = tk.Frame(self.card, bg=C.TEAL_LT, padx=14, pady=8); pf.pack(fill="x", pady=(0,18))
        tk.Label(pf, text="🔒", bg=C.TEAL_LT, font=("Segoe UI",14)).pack(side="left")
        self.p_ent = tk.Entry(pf, bg=C.TEAL_LT, fg=C.TEXT, font=("Segoe UI",12),
                              relief="flat", show="•", insertbackground=C.TEXT)
        self.p_ent.pack(side="left", fill="x", expand=True, padx=(8,0)); self.p_ent.insert(0, "password")
        bf = tk.Frame(self.card, bg=C.PINK, cursor="hand2"); bf.pack(fill="x", pady=(4,14))
        bl = tk.Label(bf, text="Let's Go! 🚀", bg=C.PINK, fg=C.WHITE,
                      font=("Segoe UI",15,"bold"), pady=12, cursor="hand2"); bl.pack(fill="x")
        for w in (bf, bl):
            w.bind("<Enter>", lambda e: bl.configure(bg=C.PINK_DK))
            w.bind("<Leave>", lambda e: bl.configure(bg=C.PINK))
        bl.bind("<Button-1>", lambda e: self._login())
        self.p_ent.bind("<Return>", lambda e: self._login())
        tk.Label(self.card, text="New here? Sign up! 💖", bg=C.CARD, fg=C.TEAL,
                 font=("Segoe UI",10,"underline"), cursor="hand2").pack()
        tk.Label(self.card, text="🌈 Your AI buddy for growth 🌈", bg=C.CARD, fg=C.TEXT_LT,
                 font=("Segoe UI",9)).pack(pady=(10,0))

    def _login(self):
        name = self.u_ent.get().strip()
        if not name: messagebox.showwarning("Oops!","Please enter your name 😊"); return
        self.frame.destroy(); self.on_login(name)


# ════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ════════════════════════════════════════════════════════════════
class YouthAIApp:
    def __init__(self, root, username):
        self.root = root; self.root.configure(bg=C.BG)
        self.username = username; self.current_page = None
        self.mood_history = self._sample_moods()
        self.registered = set(); self.chat_msgs = []
        self.career_scores = {}; self.career_step = 0
        self.selected_cat = "All"
        self.chat_engine = ChatEngine()
        self.typing_frame = None; self.typing_job = None
        self._build_sidebar()
        self.content = tk.Frame(self.root, bg=C.BG)
        self.content.pack(side="right", fill="both", expand=True)
        self.navigate("dashboard")

    def _sample_moods(self):
        pool = ["Okay"]*3+["Good"]*3+["Great"]*2+["Bad"]+["Amazing"]
        return [{"date":(datetime.now()-timedelta(days=i)).strftime("%Y-%m-%d"),
                 "mood":random.choice(pool),"note":""} for i in range(6,-1,-1)]

    # ─── Sidebar  (unchanged) ──────────────────────────
    def _build_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=C.SIDEBAR, width=220)
        self.sidebar.pack(side="left", fill="y"); self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="☁️ YouthAI", bg=C.SIDEBAR, fg=C.PINK,
                 font=("Segoe UI",18,"bold")).pack(pady=(22,0))
        tk.Label(self.sidebar, text="Growth & Wellbeing", bg=C.SIDEBAR, fg=C.TEXT_LT,
                 font=("Segoe UI",8)).pack(pady=(0,18))
        tk.Frame(self.sidebar, bg=C.PEACH, height=2).pack(fill="x", padx=20, pady=(0,12))
        self.nav_items = [("🏠","Dashboard","dashboard"),("💬","AI Chat","chat"),
            ("😊","Mood Tracker","mood"),("🎯","Career Guide","career"),
            ("📋","Programs","programs"),("👤","Profile","profile")]
        self.nav_labels = {}
        for emo, lbl, key in self.nav_items:
            f = tk.Frame(self.sidebar, bg=C.SIDEBAR, cursor="hand2", padx=12, pady=9)
            f.pack(fill="x", padx=10)
            l = tk.Label(f, text=f"  {emo}  {lbl}", bg=C.SIDEBAR, fg=C.TEXT,
                         font=("Segoe UI",11), anchor="w", cursor="hand2"); l.pack(fill="x")
            self.nav_labels[key] = (f, l)
            for w in (f, l):
                w.bind("<Enter>", lambda e, k=key: self._nav_h(k, True))
                w.bind("<Leave>", lambda e, k=key: self._nav_h(k, False))
                w.bind("<Button-1>", lambda e, k=key: self.navigate(k))
        tk.Frame(self.sidebar, bg=C.BG, height=1).pack(side="bottom", fill="x")
        uf = tk.Frame(self.sidebar, bg=C.SIDEBAR); uf.pack(side="bottom", fill="x", padx=15, pady=14)
        tk.Label(uf, text="🧑‍🎓", bg=C.PINK_LT, font=("Segoe UI",16), padx=5, pady=2).pack(side="left")
        tk.Label(uf, text=self.username, bg=C.SIDEBAR, fg=C.TEXT_DK,
                 font=("Segoe UI",10,"bold")).pack(side="left", padx=6)

    def _nav_h(self, key, enter):
        f, l = self.nav_labels[key]
        if enter: f.configure(bg=C.PINK_LT); l.configure(bg=C.PINK_LT, fg=C.PINK_DK)
        elif key == self.current_page: f.configure(bg=C.PINK_LT); l.configure(bg=C.PINK_LT, fg=C.PINK_DK)
        else: f.configure(bg=C.SIDEBAR); l.configure(bg=C.SIDEBAR, fg=C.TEXT)

    def _hl_nav(self, key):
        for k, (f, l) in self.nav_labels.items():
            if k == key: f.configure(bg=C.PINK_LT); l.configure(bg=C.PINK_LT, fg=C.PINK_DK)
            else: f.configure(bg=C.SIDEBAR); l.configure(bg=C.SIDEBAR, fg=C.TEXT)

    def navigate(self, page):
        try: self.root.unbind_all("<MouseWheel>")
        except: pass
        self._stop_typing()
        if page == self.current_page: return
        self.current_page = page; self._hl_nav(page)
        {"dashboard":self._pg_dash,"chat":self._pg_chat,"mood":self._pg_mood,
         "career":self._pg_career,"programs":self._pg_prog,"profile":self._pg_profile}[page]()

    def _clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def _scrwrap(self, parent):
        c = tk.Canvas(parent, bg=C.BG, highlightthickness=0)
        sb = tk.Scrollbar(parent, orient="vertical", command=c.yview)
        inner = tk.Frame(c, bg=C.BG)
        inner.bind("<Configure>", lambda e: c.configure(scrollregion=c.bbox("all")))
        wid = c.create_window((0,0), window=inner, anchor="nw")
        c.bind("<Configure>", lambda e: c.itemconfigure(wid, width=e.width))
        c.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); c.pack(side="left", fill="both", expand=True)
        c.bind_all("<MouseWheel>", lambda e: c.yview_scroll(int(-e.delta/120),"units"))
        return c, inner

    # ═══════════════════ DASHBOARD ═══════════════════
    def _pg_dash(self):
        self._clear()
        cv, pad = self._scrwrap(self.content)
        ban = tk.Frame(pad, bg=C.PINK, padx=24, pady=16); ban.pack(fill="x", padx=20, pady=(18,8))
        tk.Label(ban, text=f"👋 Hi, {self.username}!", bg=C.PINK, fg=C.WHITE,
                 font=("Segoe UI",20,"bold"), anchor="w").pack(anchor="w")
        tk.Label(ban, text="How are you feeling today? Let's make it a great day! 🌟",
                 bg=C.PINK, fg=C.WHITE, font=("Segoe UI",11), anchor="w").pack(anchor="w")

        # ══════════════════════════════════════════════════════
        # CHANGE 3 OF 4: Update dashboard label "Ollama" → "Gemini"
        # ══════════════════════════════════════════════════════
        sf = tk.Frame(pad, bg=C.BG); sf.pack(fill="x", padx=20, pady=6)
        avg = sum(MOODS[m["mood"]]["v"] for m in self.mood_history)/max(len(self.mood_history),1)
        ml = "😊 Good" if avg>=4 else "😐 Okay" if avg>=3 else "😟 Low"
        mode_label = "✨ Gemini" if self.chat_engine.is_api_ready() else "💬 Local"
        # was: mode_label = "✨ Ollama" if ...
        for emo,t,v,bg,fg in [("📊","Mood Avg",ml,C.TEAL_LT,C.TEAL_DK),
            ("🎯","Programs",f"{len(self.registered)} joined",C.YELLOW_LT,C.YELLOW),
            ("🤖","AI Mode",mode_label,C.LAV_LT,C.LAV),
            ("🔥","Streak",f"{len(self.mood_history)} days",C.MINT_LT,C.MINT)]:
            cd = tk.Frame(sf, bg=bg, padx=12, pady=10)
            cd.pack(side="left", fill="both", expand=True, padx=(0,6))
            tk.Label(cd, text=emo, bg=bg, font=("Segoe UI",18)).pack(anchor="w")
            tk.Label(cd, text=t, bg=bg, fg=C.TEXT_LT, font=("Segoe UI",9)).pack(anchor="w")
            tk.Label(cd, text=v, bg=bg, fg=fg, font=("Segoe UI",11,"bold")).pack(anchor="w")

        r2 = tk.Frame(pad, bg=C.BG); r2.pack(fill="x", padx=20, pady=6)
        mc = make_card(r2, c_pad=16, side="left", fill="both", expand=True, padx=(0,8))
        tk.Label(mc, text="Quick Mood Check ☀️", bg=C.CARD, fg=C.TEXT_DK,
                 font=("Segoe UI",12,"bold")).pack(anchor="w", pady=(0,8))
        mf = tk.Frame(mc, bg=C.CARD); mf.pack(anchor="w")
        for name, info in MOODS.items():
            b = tk.Label(mf, text=info["emoji"], bg=info["color"], font=("Segoe UI",16),
                         padx=8, pady=4, cursor="hand2"); b.pack(side="left", padx=2)
            b.bind("<Button-1>", lambda e, n=name: self._qk_mood(n))
        tc = make_card(r2, c_pad=16, side="right", fill="both", expand=True)
        tk.Label(tc, text="Daily Tip 🌱", bg=C.CARD, fg=C.TEXT_DK,
                 font=("Segoe UI",12,"bold")).pack(anchor="w", pady=(0,6))
        tk.Label(tc, text=random.choice(TIPS), bg=C.CARD, fg=C.TEXT,
                 font=("Segoe UI",10), wraplength=280, justify="left").pack(anchor="w")
        tk.Label(pad, text="📋 Upcoming Programs", bg=C.BG, fg=C.TEXT_DK,
                 font=("Segoe UI",14,"bold")).pack(anchor="w", padx=20, pady=(14,6))
        for prog in PROGRAMS[:4]:
            cc = CAT_COL.get(prog["cat"], C.TEAL)
            pc = tk.Frame(pad, bg=C.CARD, padx=14, pady=10); pc.pack(fill="x", padx=20, pady=3)
            tk.Frame(pc, bg=cc, width=4).pack(side="left", fill="y", padx=(0,12))
            inf = tk.Frame(pc, bg=C.CARD); inf.pack(side="left", fill="both", expand=True)
            tk.Label(inf, text=prog["title"], bg=C.CARD, fg=C.TEXT_DK,
                     font=("Segoe UI",10,"bold"), anchor="w").pack(anchor="w")
            tk.Label(inf, text=f"{prog['date']}  •  {prog['time']}  •  {prog['loc']}",
                     bg=C.CARD, fg=C.TEXT_LT, font=("Segoe UI",8), anchor="w").pack(anchor="w")
            tk.Label(pc, text=prog["cat"], bg=cc, fg=C.WHITE,
                     font=("Segoe UI",8,"bold"), padx=8, pady=2).pack(side="right")

    def _qk_mood(self, mood):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.mood_history and self.mood_history[-1]["date"] == today:
            self.mood_history[-1]["mood"] = mood
        else:
            self.mood_history.append({"date":today,"mood":mood,"note":""})
        messagebox.showinfo("Mood Saved! 🎉", f"Your mood: {MOODS[mood]['emoji']} {mood}\nKeep tracking for insights!")

    # ═══════════════════ CHAT ═══════════════════
    def _pg_chat(self):
        self._clear()
        pad = self.content

        hdr = tk.Frame(pad, bg=C.TEAL, padx=20, pady=12); hdr.pack(fill="x")
        tk.Label(hdr, text="🤖 YouthAI Chat", bg=C.TEAL, fg=C.WHITE,
                 font=("Segoe UI",14,"bold")).pack(side="left")

        # ══════════════════════════════════════════════════════
        # CHANGE 4 OF 4: Update chat header "Ollama Connected" → "Gemini Connected"
        # ══════════════════════════════════════════════════════
        if self.chat_engine.is_api_ready():
            tk.Label(hdr, text="  ✅ Gemini Connected", bg=C.TEAL, fg=C.WHITE,
                     font=("Segoe UI",9)).pack(side="left")
            # was: "  ✅ Ollama Connected"
        else:
            tk.Label(hdr, text="  ⚡ Local Mode", bg=C.TEAL, fg=C.YELLOW,
                     font=("Segoe UI",9)).pack(side="left")

        # Clear chat button
        clr_f = tk.Frame(hdr, bg=C.TEAL_DK, cursor="hand2"); clr_f.pack(side="right")
        clr_l = tk.Label(clr_f, text="🗑 Clear", bg=C.TEAL_DK, fg=C.WHITE,
                         font=("Segoe UI",9,"bold"), padx=10, pady=3, cursor="hand2")
        clr_l.pack()
        for w in (clr_f, clr_l):
            w.bind("<Button-1>", lambda e: self._clear_chat())
            w.bind("<Enter>", lambda e: clr_l.configure(bg=C.PINK))
            w.bind("<Leave>", lambda e: clr_l.configure(bg=C.TEAL_DK))

        # API status banner — updated text for Gemini
        if not self.chat_engine.is_api_ready():
            ban = tk.Frame(pad, bg=C.YELLOW_LT, padx=14, pady=6); ban.pack(fill="x")
            if HAS_GEMINI:
                msg = "⚠️ Running in local mode (keyword matching). "
            else:
                msg = "⚠️ Install Gemini package first: pip install google-generativeai. "
            msg += "Add your Gemini API key in Profile → API Settings for full AI-powered chat! 🔑"
            tk.Label(ban, text=msg, bg=C.YELLOW_LT, fg=C.TEXT_DK,
                     font=("Segoe UI",9), anchor="w").pack(anchor="w")

        # Chat messages area
        co = tk.Frame(pad, bg=C.BG); co.pack(fill="both", expand=True, padx=10, pady=6)
        self.chat_cv = tk.Canvas(co, bg=C.BG, highlightthickness=0)
        csb = tk.Scrollbar(co, orient="vertical", command=self.chat_cv.yview)
        self.chat_in = tk.Frame(self.chat_cv, bg=C.BG)
        self.chat_in.bind("<Configure>", lambda e: self.chat_cv.configure(scrollregion=self.chat_cv.bbox("all")))
        self.chat_wid = self.chat_cv.create_window((0,0), window=self.chat_in, anchor="nw")
        self.chat_cv.bind("<Configure>", lambda e: self.chat_cv.itemconfigure(self.chat_wid, width=e.width))
        self.chat_cv.configure(yscrollcommand=csb.set)
        csb.pack(side="right", fill="y"); self.chat_cv.pack(side="left", fill="both", expand=True)

        if not self.chat_msgs:
            self.chat_msgs.append(("ai", random.choice(AI_RESP["greeting"])))
        self._render_chat()

        # Input area
        inp = tk.Frame(pad, bg=C.CARD, padx=12, pady=10)
        inp.pack(fill="x", padx=10, pady=(0,10))
        self.chat_e = tk.Entry(inp, bg=C.BG, fg=C.TEXT, font=("Segoe UI",11),
                               relief="flat", insertbackground=C.TEXT)
        self.chat_e.pack(side="left", fill="x", expand=True, ipady=6)
        self.chat_e.insert(0, "Type your message...")
        self.chat_e.bind("<FocusIn>", self._chat_focus_in)
        self.chat_e.bind("<Return>", lambda e: self._send_chat())
        sf = tk.Frame(inp, bg=C.PINK, cursor="hand2"); sf.pack(side="right", padx=(8,0))
        sl = tk.Label(sf, text="Send 💬", bg=C.PINK, fg=C.WHITE,
                      font=("Segoe UI",10,"bold"), padx=14, pady=6, cursor="hand2"); sl.pack()
        for w in (sf, sl):
            w.bind("<Enter>", lambda e: sl.configure(bg=C.PINK_DK))
            w.bind("<Leave>", lambda e: sl.configure(bg=C.PINK))
            w.bind("<Button-1>", lambda e: self._send_chat())

    def _chat_focus_in(self, e):
        if self.chat_e.get() == "Type your message...":
            self.chat_e.delete(0, "end")

    def _clear_chat(self):
        self.chat_msgs = []
        self.chat_msgs.append(("ai", random.choice(AI_RESP["greeting"])))
        self._render_chat()

    def _render_chat(self):
        for w in self.chat_in.winfo_children(): w.destroy()
        for sender, msg in self.chat_msgs:
            if sender == "ai":
                mf = tk.Frame(self.chat_in, bg=C.CHAT_A, padx=14, pady=10)
                mf.pack(anchor="w", padx=10, pady=4, fill="x")
                tk.Label(mf, text="🤖 YouthAI", bg=C.CHAT_A, fg=C.TEAL_DK,
                         font=("Segoe UI",8,"bold"), anchor="w").pack(anchor="w")
                tk.Label(mf, text=msg, bg=C.CHAT_A, fg=C.TEXT, font=("Segoe UI",10),
                         wraplength=480, justify="left", anchor="w").pack(anchor="w")
            else:
                mf = tk.Frame(self.chat_in, bg=C.CHAT_U, padx=14, pady=10)
                mf.pack(anchor="e", padx=10, pady=4, fill="x")
                tk.Label(mf, text="You 👤", bg=C.CHAT_U, fg=C.PINK_DK,
                         font=("Segoe UI",8,"bold"), anchor="e").pack(anchor="e")
                tk.Label(mf, text=msg, bg=C.CHAT_U, fg=C.TEXT, font=("Segoe UI",10),
                         wraplength=480, justify="right", anchor="e").pack(anchor="e")
        self.chat_in.update_idletasks()
        self.chat_cv.configure(scrollregion=self.chat_cv.bbox("all"))
        self.chat_cv.yview_moveto(1.0)

    # ─── Typing Indicator  (unchanged) ────────────────
    def _show_typing(self):
        self._stop_typing()
        self.typing_frame = tk.Frame(self.chat_in, bg=C.CHAT_A, padx=14, pady=10)
        self.typing_frame.pack(anchor="w", padx=10, pady=4)
        tk.Label(self.typing_frame, text="🤖 YouthAI", bg=C.CHAT_A, fg=C.TEAL_DK,
                 font=("Segoe UI",8,"bold")).pack(anchor="w")
        self.typing_label = tk.Label(self.typing_frame, text="thinking", bg=C.CHAT_A,
                                     fg=C.TEXT_LT, font=("Segoe UI",10))
        self.typing_label.pack(anchor="w")
        self._animate_typing(0)
        self.chat_cv.yview_moveto(1.0)

    def _animate_typing(self, step):
        if self.typing_frame and self.typing_frame.winfo_exists():
            dots = "." * (step % 4)
            self.typing_label.configure(text=f"thinking{dots}")
            self.typing_job = self.root.after(350, self._animate_typing, step + 1)

    def _stop_typing(self):
        if self.typing_job:
            try: self.root.after_cancel(self.typing_job)
            except: pass
            self.typing_job = None
        if self.typing_frame and self.typing_frame.winfo_exists():
            self.typing_frame.destroy()
        self.typing_frame = None

    # ─── Send Message  (unchanged) ────────────────────
    def _send_chat(self):
        text = self.chat_e.get().strip()
        if not text or text == "Type your message...": return
        self.chat_e.delete(0, "end")
        self.chat_msgs.append(("user", text))
        self._render_chat()
        self.chat_e.configure(state="disabled")
        self._show_typing()
        self.chat_engine.get_response_async(text, self.chat_msgs)
        self._poll_response()

    def _poll_response(self):
        result = self.chat_engine.poll()
        if result is not None:
            self._stop_typing()
            self.chat_msgs.append(("ai", result))
            self._render_chat()
            self.chat_e.configure(state="normal")
            self.chat_e.focus_set()
        else:
            self.root.after(100, self._poll_response)

    # ═══════════════════ MOOD TRACKER ═══════════════════
    def _pg_mood(self):
        self._clear()
        pad = self.content
        hdr = tk.Frame(pad, bg=C.LAV, padx=20, pady=12); hdr.pack(fill="x")
        tk.Label(hdr, text="😊 Mood Tracker", bg=C.LAV, fg=C.WHITE,
                 font=("Segoe UI",14,"bold")).pack(side="left")
        wrapper = tk.Frame(pad, bg=C.BG); wrapper.pack(fill="both", expand=True)
        cv, inner = self._scrwrap(wrapper)
        lc = make_card(inner, c_pad=20)
        tk.Label(lc, text="How are you feeling right now? 💭", bg=C.CARD, fg=C.TEXT_DK,
                 font=("Segoe UI",13,"bold")).pack(anchor="w", pady=(0,10))
        self.mood_btns = {}; mf = tk.Frame(lc, bg=C.CARD); mf.pack(anchor="w")
        for name, info in MOODS.items():
            f = tk.Frame(mf, bg=C.CARD, cursor="hand2"); f.pack(side="left", padx=4)
            l = tk.Label(f, text=f"{info['emoji']}\n{name}", bg=info["color"], fg=C.TEXT,
                         font=("Segoe UI",9,"bold"), padx=12, pady=8, cursor="hand2", justify="center")
            l.pack(); self.mood_btns[name] = l
            for w in (f, l): w.bind("<Button-1>", lambda e, n=name: self._sel_mood(n))
        self.sel_mood = None
        self.mood_st = tk.Label(lc, text="", bg=C.CARD, fg=C.TEXT_LT, font=("Segoe UI",9))
        self.mood_st.pack(anchor="w", pady=(8,0))
        tk.Label(lc, text="Add a note (optional):", bg=C.CARD, fg=C.TEXT_LT,
                 font=("Segoe UI",9)).pack(anchor="w", pady=(10,2))
        self.mood_note = tk.Entry(lc, bg=C.BG, fg=C.TEXT, font=("Segoe UI",10),
                                  relief="flat", insertbackground=C.TEXT)
        self.mood_note.pack(fill="x", ipady=5)
        hover_btn(lc, "Save Mood ✨", C.MINT, self._save_mood)
        cc = make_card(inner, c_pad=20)
        tk.Label(cc, text="Your Mood Journey (Last 7 Days) 📈", bg=C.CARD, fg=C.TEXT_DK,
                 font=("Segoe UI",12,"bold")).pack(anchor="w", pady=(0,10))
        self.mood_cv = tk.Canvas(cc, bg=C.CARD, height=210, highlightthickness=0)
        self.mood_cv.pack(fill="x")
        self.root.after(100, self._draw_chart)

    def _sel_mood(self, name):
        self.sel_mood = name; info = MOODS[name]
        for n, l in self.mood_btns.items(): l.configure(relief="solid" if n==name else "flat", bd=3 if n==name else 0)
        self.mood_st.configure(text=f"Selected: {info['emoji']} {name}", fg=info["color"])

    def _save_mood(self):
        if not self.sel_mood: messagebox.showinfo("Oops!","Please select a mood first 😊"); return
        today = datetime.now().strftime("%Y-%m-%d"); note = self.mood_note.get().strip()
        if self.mood_history and self.mood_history[-1]["date"] == today:
            self.mood_history[-1] = {"date":today,"mood":self.sel_mood,"note":note}
        else:
            self.mood_history.append({"date":today,"mood":self.sel_mood,"note":note})
        if len(self.mood_history) > 30: self.mood_history = self.mood_history[-30:]
        self.mood_note.delete(0,"end"); self.sel_mood = None
        for n,l in self.mood_btns.items(): l.configure(relief="flat", bd=0)
        self.mood_st.configure(text="Saved! ✅", fg=C.MINT); self._draw_chart()
        messagebox.showinfo("Saved! 🎉", "Your mood has been logged! Keep tracking! 💪")

    def _draw_chart(self):
        c = self.mood_cv; c.delete("all"); data = self.mood_history[-7:]
        if not data: return
        c.update_idletasks(); w = max(c.winfo_width(),400); h = 200
        ml,mr,mt,mb = 50,30,25,40; cw=w-ml-mr; ch=h-mt-mb
        for i in range(1,7):
            y=mt+ch-(i/6)*ch; c.create_line(ml,y,w-mr,y,fill="#F0E8E0",dash=(2,4))
        for i,name in enumerate(MOODS.keys()):
            y=mt+ch-((i+1)/6)*ch; c.create_text(ml-8,y,text=MOODS[name]["emoji"],font=("Segoe UI",9),anchor="e")
        gap=cw/len(data); bw=gap*0.6; pts=[]
        for i,entry in enumerate(data):
            val=MOODS[entry["mood"]]["v"]; col=MOODS[entry["mood"]]["color"]
            x=ml+i*gap+(gap-bw)/2; bh=(val/6)*ch; yb=mt+ch; yt=yb-bh
            c.create_rectangle(x,yt,x+bw,yb,fill=col,outline="")
            c.create_text(x+bw/2,yt-10,text=MOODS[entry["mood"]]["emoji"],font=("Segoe UI",10))
            c.create_text(x+bw/2,yb+14,text=entry["date"][-5:],font=("Segoe UI",7),fill=C.TEXT_LT)
            pts.append((ml+i*gap+gap/2, yt))
        for i in range(len(pts)-1):
            c.create_line(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],fill=C.PINK,width=2,dash=(4,2))
        for x,y in pts: c.create_oval(x-3,y-3,x+3,y+3,fill=C.PINK,outline="")

    # ═══════════════════ CAREER GUIDE ═══════════════════
    def _pg_career(self):
        self._clear(); self.career_step=0; self.career_scores={k:0 for k in CAREERS}
        pad=self.content
        hdr=tk.Frame(pad,bg=C.YELLOW,padx=20,pady=12);hdr.pack(fill="x")
        tk.Label(hdr,text="🎯 Career Guide",bg=C.YELLOW,fg=C.TEXT_DK,font=("Segoe UI",14,"bold")).pack(side="left")
        wrapper=tk.Frame(pad,bg=C.BG);wrapper.pack(fill="both",expand=True)
        cv,self.career_area=self._scrwrap(wrapper); self._career_intro()

    def _career_intro(self):
        a=self.career_area
        for w in a.winfo_children(): w.destroy()
        cd=make_card(a,c_pad=30)
        tk.Label(cd,text="Discover Your Path! 🌟",bg=C.CARD,fg=C.TEXT_DK,font=("Segoe UI",18,"bold")).pack(pady=(0,8))
        tk.Label(cd,text="Answer 3 quick questions and we'll suggest\ncareer paths that match your interests!",
                 bg=C.CARD,fg=C.TEXT_LT,font=("Segoe UI",11),justify="center").pack(pady=(0,6))
        icons=tk.Frame(cd,bg=C.CARD);icons.pack(pady=(8,16))
        for name,info in CAREERS.items():
            f=tk.Frame(icons,bg=info["color"],padx=10,pady=6);f.pack(side="left",padx=4)
            tk.Label(f,text=f"{info['icon']}\n{name}",bg=info["color"],fg=C.WHITE,font=("Segoe UI",8,"bold"),justify="center").pack()
        hover_btn(cd,"Start Quiz 🚀",C.PINK,self._career_q)

    def _career_q(self):
        a=self.career_area
        for w in a.winfo_children(): w.destroy()
        if self.career_step>=len(CAREER_Q): self._career_res(); return
        qd=CAREER_Q[self.career_step]
        pf=tk.Frame(a,bg=C.BG);pf.pack(fill="x",pady=(0,12))
        for i in range(len(CAREER_Q)):
            col=C.PINK if i<self.career_step else C.TEAL if i==self.career_step else C.SHADOW
            tk.Label(pf,text="●",bg=C.BG,fg=col,font=("Segoe UI",16)).pack(side="left",padx=8)
        tk.Label(pf,text=f"  Question {self.career_step+1} of {len(CAREER_Q)}",bg=C.BG,fg=C.TEXT_LT,font=("Segoe UI",10)).pack(side="left")
        cd=make_card(a,c_pad=30)
        tk.Label(cd,text=qd["q"],bg=C.CARD,fg=C.TEXT_DK,font=("Segoe UI",16,"bold")).pack(pady=(0,16))
        self.career_opts=[]; colors=[C.TEAL_LT,C.YELLOW_LT,C.LAV_LT,C.MINT_LT,C.PEACH_LT]
        for i,(text,cat) in enumerate(qd["opts"]):
            of=tk.Frame(cd,bg=colors[i%len(colors)],padx=16,pady=10,cursor="hand2");of.pack(fill="x",pady=3)
            ol=tk.Label(of,text=f"  {text}",bg=colors[i%len(colors)],fg=C.TEXT,font=("Segoe UI",11),anchor="w",cursor="hand2")
            ol.pack(fill="x")
            for w in (of,ol):
                w.bind("<Enter>",lambda e,l=ol:l.configure(fg=C.PINK_DK))
                w.bind("<Leave>",lambda e,l=ol:l.configure(fg=C.TEXT))
                w.bind("<Button-1>",lambda e,c=cat,f=of:self._career_ans(c,f))
            self.career_opts.append(of)

    def _career_ans(self,cat,frame):
        self.career_scores[cat]+=1
        for f in self.career_opts: f.configure(relief="flat",bd=0)
        frame.configure(relief="solid",bd=2); self.career_step+=1
        self.root.after(500,self._career_q)

    def _career_res(self):
        a=self.career_area
        for w in a.winfo_children(): w.destroy()
        top3=sorted(self.career_scores.items(),key=lambda x:x[1],reverse=True)[:3]
        tk.Label(a,text="🎉 Your Career Matches!",bg=C.BG,fg=C.TEXT_DK,font=("Segoe UI",18,"bold")).pack(pady=(0,12))
        for rank,(name,score) in enumerate(top3):
            info=CAREERS[name]; cd=make_card(a,c_pad=20)
            hf=tk.Frame(cd,bg=info["color"],padx=14,pady=8);hf.pack(fill="x",pady=(0,12))
            tk.Label(hf,text=f"#{rank+1}  {info['icon']}  {name}  ({score}/{len(CAREER_Q)})",
                     bg=info["color"],fg=C.WHITE,font=("Segoe UI",13,"bold")).pack(anchor="w")
            rf=tk.Frame(cd,bg=C.CARD);rf.pack(fill="x",pady=2)
            tk.Label(rf,text="Career Roles:",bg=C.CARD,fg=C.TEXT_DK,font=("Segoe UI",9,"bold")).pack(anchor="w")
            tk.Label(rf,text="  •  "+"  •  ".join(info["roles"][:3]),bg=C.CARD,fg=C.TEXT,font=("Segoe UI",9),wraplength=480,justify="left").pack(anchor="w")
            sf=tk.Frame(cd,bg=C.CARD);sf.pack(fill="x",pady=2)
            tk.Label(sf,text="Key Skills:",bg=C.CARD,fg=C.TEXT_DK,font=("Segoe UI",9,"bold")).pack(anchor="w")
            sr=tk.Frame(sf,bg=C.CARD);sr.pack(anchor="w",pady=2)
            for skill in info["skills"][:4]:
                tk.Label(sr,text=f" {skill} ",bg=info["color"],fg=C.WHITE,font=("Segoe UI",8,"bold"),padx=6,pady=2).pack(side="left",padx=2)
            cf=tk.Frame(cd,bg=C.CARD);cf.pack(fill="x",pady=2)
            tk.Label(cf,text="📚 Suggested Courses:",bg=C.CARD,fg=C.TEXT_DK,font=("Segoe UI",9,"bold")).pack(anchor="w")
            tk.Label(cf,text="  •  "+"  •  ".join(info["courses"]),bg=C.CARD,fg=C.TEXT,font=("Segoe UI",9),wraplength=480,justify="left").pack(anchor="w")
        hover_btn(a,"Retake Quiz 🔄",C.TEAL,self._pg_career)

    # ═══════════════════ PROGRAMS ═══════════════════
    def _pg_prog(self):
        self._clear(); self.selected_cat="All"; pad=self.content
        hdr=tk.Frame(pad,bg=C.MINT,padx=20,pady=12);hdr.pack(fill="x")
        tk.Label(hdr,text="📋 Programs & Events",bg=C.MINT,fg=C.TEXT_DK,font=("Segoe UI",14,"bold")).pack(side="left")
        ff=tk.Frame(pad,bg=C.BG,padx=20,pady=10);ff.pack(fill="x")
        sf=tk.Frame(ff,bg=C.CARD,padx=10,pady=6);sf.pack(side="left",fill="x",expand=True,padx=(0,8))
        tk.Label(sf,text="🔍",bg=C.CARD,font=("Segoe UI",12)).pack(side="left")
        self.prog_se=tk.Entry(sf,bg=C.CARD,fg=C.TEXT,font=("Segoe UI",10),relief="flat",insertbackground=C.TEXT)
        self.prog_se.pack(side="left",fill="x",expand=True,padx=(6,0)); self.prog_se.insert(0,"Search programs...")
        self.prog_se.bind("<FocusIn>",lambda e:self.prog_se.delete(0,"end") if self.prog_se.get()=="Search programs..." else None)
        self.prog_se.bind("<KeyRelease>",lambda e:self._filt_prog())
        cats=["All"]+list(set(p["cat"] for p in PROGRAMS))
        self.cat_btns={}; cr=tk.Frame(ff,bg=C.BG); cr.pack(side="right")
        for cat in cats:
            col=C.PINK if cat=="All" else CAT_COL.get(cat,C.TEAL)
            f=tk.Frame(cr,bg=col,cursor="hand2",padx=8,pady=4);f.pack(side="left",padx=2)
            l=tk.Label(f,text=cat,bg=col,fg=C.WHITE,font=("Segoe UI",8,"bold"),cursor="hand2");l.pack()
            for w in (f,l): w.bind("<Button-1>",lambda e,c=cat:self._sel_cat(c))
            self.cat_btns[cat]=l
        wrapper=tk.Frame(pad,bg=C.BG);wrapper.pack(fill="both",expand=True,padx=20,pady=(0,20))
        self.prog_cv,self.prog_list=self._scrwrap(wrapper); self._render_prog(PROGRAMS)

    def _sel_cat(self,cat):
        self.selected_cat=cat
        for n,l in self.cat_btns.items(): l.configure(relief="solid" if n==cat else "flat",bd=2 if n==cat else 0)
        self._filt_prog()

    def _filt_prog(self):
        s=self.prog_se.get().lower()
        fl=[p for p in PROGRAMS
            if(self.selected_cat=="All" or p["cat"]==self.selected_cat)
            and(not s or s=="search programs..." or s in p["title"].lower() or s in p["desc"].lower())]
        self._render_prog(fl)

    def _render_prog(self,progs):
        for w in self.prog_list.winfo_children(): w.destroy()
        if not progs:
            tk.Label(self.prog_list,text="No programs found 😅",bg=C.BG,fg=C.TEXT_LT,font=("Segoe UI",12)).pack(pady=40); return
        for p in progs:
            cc=CAT_COL.get(p["cat"],C.TEAL); regged=p["id"] in self.registered; full=p["reg"]>=p["slots"]
            cd=tk.Frame(self.prog_list,bg=C.CARD,padx=14,pady=12); cd.pack(fill="x",pady=4)
            tk.Frame(cd,bg=cc,width=4).pack(side="left",fill="y",padx=(0,12))
            inf=tk.Frame(cd,bg=C.CARD); inf.pack(side="left",fill="both",expand=True)
            tk.Label(inf,text=p["title"],bg=C.CARD,fg=C.TEXT_DK,font=("Segoe UI",11,"bold"),anchor="w").pack(anchor="w")
            tk.Label(inf,text=p["desc"],bg=C.CARD,fg=C.TEXT_LT,font=("Segoe UI",9),wraplength=420,justify="left",anchor="w").pack(anchor="w")
            tk.Label(inf,text=f"📅 {p['date']}  •  ⏰ {p['time']}  •  📍 {p['loc']}",bg=C.CARD,fg=C.TEXT_LT,font=("Segoe UI",8),anchor="w").pack(anchor="w",pady=(2,0))
            bb=tk.Frame(inf,bg=C.SHADOW,height=6);bb.pack(fill="x",pady=(4,0)); bb.update_idletasks()
            tk.Frame(bb,bg=cc,height=6).place(relwidth=min(p["reg"]/p["slots"],1.0),relheight=1.0)
            tk.Label(inf,text=f"{p['reg']}/{p['slots']} slots",bg=C.CARD,fg=C.TEXT_LT,font=("Segoe UI",7)).pack(anchor="e")
            rt=tk.Frame(cd,bg=C.CARD);rt.pack(side="right",padx=(10,0))
            tk.Label(rt,text=p["cat"],bg=cc,fg=C.WHITE,font=("Segoe UI",8,"bold"),padx=8,pady=3).pack(pady=(0,6))
            if regged:
                tk.Label(rt,text="✅ Joined",bg=C.MINT_LT,fg=C.TEAL_DK,font=("Segoe UI",9,"bold"),padx=10,pady=4).pack()
            elif full:
                tk.Label(rt,text="Full",bg=C.SHADOW,fg=C.TEXT_LT,font=("Segoe UI",9,"bold"),padx=10,pady=4).pack()
            else:
                rf=tk.Frame(rt,bg=C.PINK,cursor="hand2");rf.pack()
                rl=tk.Label(rf,text="Join 🎉",bg=C.PINK,fg=C.WHITE,font=("Segoe UI",9,"bold"),padx=10,pady=4,cursor="hand2");rl.pack()
                for w in (rf,rl):
                    w.bind("<Enter>",lambda e:rl.configure(bg=C.PINK_DK))
                    w.bind("<Leave>",lambda e:rl.configure(bg=C.PINK))
                    w.bind("<Button-1>",lambda e,pid=p["id"]:self._join(pid))

    def _join(self,pid):
        self.registered.add(pid)
        messagebox.showinfo("Joined! 🎉","You've successfully registered!\nSee you there! 💖")
        self._filt_prog()

    # ═══════════════════ PROFILE + API SETTINGS ═══════════════════
    def _pg_profile(self):
        self._clear(); pad=self.content
        hdr=tk.Frame(pad,bg=C.PEACH,padx=20,pady=12);hdr.pack(fill="x")
        tk.Label(hdr,text="👤 My Profile",bg=C.PEACH,fg=C.TEXT_DK,font=("Segoe UI",14,"bold")).pack(side="left")
        wrapper=tk.Frame(pad,bg=C.BG);wrapper.pack(fill="both",expand=True)
        cv,inner=self._scrwrap(wrapper)

        # Avatar
        ac=make_card(inner,c_pad=30)
        af=tk.Frame(ac,bg=C.PINK_LT,padx=16,pady=8);af.pack(pady=(0,12))
        tk.Label(af,text="🧑‍🎓",bg=C.PINK_LT,font=("Segoe UI",40)).pack()
        tk.Label(ac,text=self.username,bg=C.CARD,fg=C.TEXT_DK,font=("Segoe UI",18,"bold")).pack()
        tk.Label(ac,text="UKM Student  •  FSKTM",bg=C.CARD,fg=C.TEXT_LT,font=("Segoe UI",11)).pack(pady=(0,8))

        # Stats row
        sr=tk.Frame(ac,bg=C.CARD);sr.pack(fill="x",pady=8)
        for label,val,col in [("Mood Logs",len(self.mood_history),C.PINK_LT),
                               ("Programs",len(self.registered),C.TEAL_LT),
                               ("AI Messages",len(self.chat_msgs),C.LAV_LT)]:
            sf=tk.Frame(sr,bg=col,padx=14,pady=8);sf.pack(side="left",fill="both",expand=True,padx=(0,6))
            tk.Label(sf,text=str(val),bg=col,fg=C.TEXT_DK,font=("Segoe UI",18,"bold")).pack()
            tk.Label(sf,text=label,bg=col,fg=C.TEXT_LT,font=("Segoe UI",9)).pack()

        # ── API Settings Card ──
        api_card = make_card(inner, c_pad=20)
        tk.Label(api_card, text="🔑 API Settings (Gemini)", bg=C.CARD, fg=C.TEXT_DK,
                 font=("Segoe UI",13,"bold")).pack(anchor="w", pady=(0,6))
        tk.Label(api_card, text="Enter your Google Gemini API key to enable full AI chat.",
                 bg=C.CARD, fg=C.TEXT_LT, font=("Segoe UI",9)).pack(anchor="w", pady=(0,8))

        kf = tk.Frame(api_card, bg=C.LAV_LT, padx=14, pady=8); kf.pack(fill="x", pady=(0,6))
        tk.Label(kf, text="🔑", bg=C.LAV_LT, font=("Segoe UI",14)).pack(side="left")
        self.api_ent = tk.Entry(kf, bg=C.LAV_LT, fg=C.TEXT, font=("Segoe UI",11),
                                relief="flat", insertbackground=C.TEXT, show="•")
        self.api_ent.pack(side="left", fill="x", expand=True, padx=(8,0))
        if self.chat_engine.api_key != "YOUR_GEMINI_API_KEY_HERE":
            self.api_ent.insert(0, self.chat_engine.api_key)

        hover_btn(api_card, "Save API Key 💾", C.LAV, self._save_api_key)

        # Status
        if self.chat_engine.is_api_ready():
            tk.Label(api_card, text="✅ Gemini API is connected and ready!",
                     bg=C.CARD, fg=C.MINT, font=("Segoe UI",10,"bold")).pack(anchor="w", pady=(8,0))
        elif HAS_GEMINI:
            tk.Label(api_card, text="⚠️ Gemini package installed but no API key set.",
                     bg=C.CARD, fg=C.YELLOW, font=("Segoe UI",10)).pack(anchor="w", pady=(8,0))
        else:
            tk.Label(api_card, text="❌ Gemini package not installed.\nRun: pip install google-generativeai",
                     bg=C.CARD, fg=C.M1, font=("Segoe UI",10)).pack(anchor="w", pady=(8,0))

        # About
        ab = make_card(inner, c_pad=20)
        tk.Label(ab, text="About YouthAI 🌈", bg=C.CARD, fg=C.TEXT_DK,
                 font=("Segoe UI",13,"bold")).pack(anchor="w", pady=(0,6))
        tk.Label(ab, text="YouthAI is your AI-powered wellbeing buddy designed\n"
                          "for UKM students. Track your mood, explore careers,\n"
                          "join campus programs, and chat with AI for support.\n\n"
                          "Powered by Google Gemini AI ✨",
                 bg=C.CARD, fg=C.TEXT_LT, font=("Segoe UI",10), justify="left").pack(anchor="w")

        hover_btn(inner, "Log Out 👋", C.PEACH, self._logout)

    def _save_api_key(self):
        key = self.api_ent.get().strip()
        if not key:
            messagebox.showwarning("Oops!", "Please enter an API key 🔑")
            return
        self.chat_engine.api_key = key
        messagebox.showinfo("Saved! ✅", "Gemini API key saved!\nGo to AI Chat to try it out! 💬")

    def _logout(self):
        if messagebox.askyesno("Log Out", "Are you sure you want to log out? 😊"):
            self.root.destroy()


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    root.title("YouthAI — Growth & Wellbeing Platform")
    root.geometry("1100x700")
    root.minsize(900, 600)

    app_ref = [None]
    def start_app(name):
        app_ref[0] = YouthAIApp(root, name)

    LoginScreen(root, start_app)
    root.mainloop()
