# K-pop Creator Aptitude Test (Streamlit)

An interactive quiz that maps your creative tendencies to K‑pop creator roles, with a playful **aespa‑inspired cyber UI**.  
**Note:** The test UI and all question text are in **Japanese (日本語)**.

---

## Quick Start

```bash
# 1) Install (no external APIs required)
pip install streamlit plotly pandas

# 2) Run
streamlit run kpop_app_fixed.py
```

**Folder structure**
```
.
├─ kpop_app_fixed.py        # Streamlit app
├─ aespa_cyber_css.css      # Custom CSS (must be in the same folder)
└─ demo/                    # Put demo screenshots here
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

## Example Questions (JP prompts, English summaries)

- **「もし飼い犬が突然アイドル並みに歌い出したら、まずどうする？」**  
  *Your dog suddenly sings like an idol—what’s your first move?*

- **「無人島に1ヶ月、片道チケット。持っていくのは？」**  
  *A one‑month, one‑way ticket to a deserted island—what single item do you bring?*

- **「タイムトラベルして音楽の時代を1つ見学できるなら？」**  
  *You can time‑travel to observe one music era; which do you pick and why?*

- **（任意のサンプル）「スマホが電池切れの電車内で、つい何をする？」**  
  *Bonus example: your phone dies on the train—what do you naturally do?*

> These imaginative prompts are designed to surface **creative style, problem‑solving bias, and role fit** rather than “right answers.”

---


## Demo Screenshots (from the ./demo folder)

These are sample screens of the Japanese UI. The images below should exist in the `demo/` folder with the exact names shown.

<p align="center">
  <img src="./demo/welcome page.jpg" alt="Demo — Welcome page (Japanese UI)" width="45%">
  <img src="./demo/test question 1.jpg" alt="Demo — Test question 1" width="45%"><br>
  <img src="./demo/test question 2.jpg" alt="Demo — Test question 2" width="45%">
  <img src="./demo/diagnosis result.jpg" alt="Demo — Diagnosis result with radar chart" width="45%">
</p>


---

## Troubleshooting

- **CSS not applied** → Ensure `aespa_cyber_css.css` sits next to `kpop_app_fixed.py` and the file name matches exactly.  
- **Japanese text garbled** → Confirm your terminal/browser uses UTF‑8 and the file encoding is UTF‑8.  
- **Chart looks squashed** → Widen the browser window or use an up‑to‑date Chrome/Edge.  

---

## Notes

- All UI strings and questions are currently **Japanese-only** for a native feel.  
- You can localize the strings by editing the question list and labels inside `kpop_app_fixed.py`.

---

## Notes

- All UI strings and questions are currently **Japanese-only** for a native feel.  
- You’re welcome to localize the strings by editing the question list and labels inside `kpop_app_fixed.py`.
