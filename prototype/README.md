# ⚙️ Prototype Setup Guide

> **Goal:** anyone — a judge, a mentor, a teammate — can clone your project and run it in under 5 minutes.
> Replace the placeholders below with YOUR project's real steps, then delete anything that doesn't apply.

---

## 📋 Prerequisites

Tell people exactly what they need installed before starting:

| Tool | Version | Check with | Install |
|------|---------|-----------|---------|
| Node.js | 18+ | `node -v` | https://nodejs.org |
| Python | 3.10+ | `python --version` | https://python.org |
| Git | any | `git -v` | https://git-scm.com |

*(Keep only the rows your project actually needs.)*

---

## 1️⃣ Clone the repository

```bash
git clone <repository-link>
cd <project-folder>
```

## 2️⃣ Install dependencies

**Node projects:**

```bash
npm install
```

**Python projects:**

```bash
pip install -r requirements.txt
```

## 3️⃣ Configure environment variables

If your project uses API keys, NEVER commit them. Instead:

1. Create a file named `.env.example` listing the keys WITHOUT values:

```
OPENAI_API_KEY=
DATABASE_URL=
```

2. Tell users to copy it and fill in their own values:

```bash
cp .env.example .env
```

3. Add `.env` to your `.gitignore`.

## 4️⃣ Run the project

**Node:**

```bash
npm run dev
```

**Python:**

```bash
python main.py
```

Then open: http://localhost:3000 *(replace with your port)*

## 5️⃣ Try it out

Give a 30-second test path so people see the magic immediately:

1. Open the app
2. Upload the sample file in `/examples` *(include one!)*
3. Click "Generate"
4. See the output

---

## 🌐 Can't run it locally? Provide a fallback

Judges may not have time to install things. Always include at least ONE of:

- **Live deployment** — Vercel / Render / Google Cloud link
- **Screenshots or GIF** — put them in this folder and embed them here
- **The demo video** — link to it

---

## 🆘 Troubleshooting

Add the 2–3 errors your own team hit, e.g.:

- **`command not found: npm`** → Node isn't installed (see Prerequisites)
- **Port already in use** → stop other apps or change the port in config
- **Missing API key error** → you skipped step 3 (.env setup)

---

## 🧠 Implementation Notes (optional but impressive)

Briefly explain how the pieces fit — judges love a simple architecture story:

```
[ Frontend (React) ] → [ API (Node/Express) ] → [ OpenAI API ]
                                ↓
                        [ Database (Firestore) ]
```

One or two sentences per box is plenty.
