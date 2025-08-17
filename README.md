# K-pop Creator Aptitude Test (Streamlit)

An interactive quiz that maps your creative tendencies to K‑pop creator roles, with a playful **aespa‑inspired cyber UI**.  
**Note:** The test UI and all question text are in **Japanese (日本語)**.

---

## Quick Start

```bash
# 1) Install (OpenAI is optional)
pip install streamlit plotly pandas openai

# 2) Run
streamlit run kpop_app_fixed.py
```

**Folder structure**
```
.
├─ kpop_app_fixed.py        # Streamlit app
└─ aespa_cyber_css.css      # Custom CSS (must be in the same folder)
```

> The CSS is loaded via a relative path in `kpop_app_fixed.py`. Keep the two files in the **same directory**.

---

## What it Does

- 📋 **10 questions** (Japanese) about preferences and work style
- 🧮 Scores are normalized and aggregated into six capability axes
- 📈 **Radar chart** (Plotly) to visualize your profile
- 🧭 Suggested **creator role** among: `Concept / Producer / Lyric / Visual / Performance / Fan`
- 🎨 Custom **cyber / neon** look & feel via `aespa_cyber_css.css`

---

## Optional: AI Commentary

If you want a short AI-generated note for the result, enable the `generate_ai_analysis()` section in the code and set your API key:

```
# .env or environment variable
OPENAI_API_KEY=sk-xxxxxxxx
```

By default the app uses a simple fallback message—no API is required to run.

---

## Troubleshooting

- **CSS not applied** → Ensure `aespa_cyber_css.css` sits next to `kpop_app_fixed.py` and the file name matches exactly.  
- **ModuleNotFoundError: openai** → Either `pip install openai` or keep the AI section commented out.  
- **Chart looks squashed** → Widen the browser window or use an up-to-date Chrome/Edge.  
- **Japanese text garbled** → Confirm your terminal/browser uses UTF‑8 and the file encoding is UTF‑8.

---

## Notes

- All UI strings and questions are currently **Japanese-only** for a native feel.  
- You’re welcome to localize the strings by editing the question list and labels inside `kpop_app_fixed.py`.
