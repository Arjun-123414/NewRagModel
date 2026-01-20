# 🏗️ AI‑Powered Construction Bid Comparison Platform

> **"From messy PDFs to clear winners — automatically."**

This repository contains a **production‑ready, LLM‑driven bid analysis system** built for the construction domain. It extracts plans and prices from **PDF / Excel bid files**, compares them intelligently, identifies **per‑plan and overall winners**, and even lets you **chat with your bid data** using AI.

This is not a demo. This is a **real decision‑support system**.

---

## 🚀 What This Project Solves

Construction bids are:
- Large (80+ pages)
- Unstructured (PDFs, scanned docs, Excel sheets)
- Hard to compare manually

This system:

✔ Extracts **every plan** from every file using LLMs  
✔ Normalizes prices & structures data  
✔ Compares **same plans across vendors**  
✔ Finds **lowest price per plan**  
✔ Declares an **overall winning bid**  
✔ Shows **exact savings**  
✔ Provides a **Streamlit UI**  
✔ Allows **natural‑language Q&A** over bid data

---

## 🧠 High‑Level Architecture

```
PDF / Excel Bids
      ↓
LLM‑based Extraction (LangChain)
      ↓
Structured JSON (plan‑wise)
      ↓
Plan‑to‑Plan Comparison Engine
      ↓
Winner + Savings Analysis
      ↓
Streamlit UI / Chat Interface
```

---

## 📂 Project Structure

```
.
├── data/                     # Place all bid PDFs / Excel files here
│
├── bid_extractor.py           # LLM‑based bid & plan extraction
├── bid_comparator.py          # Core comparison + winner logic
├── loader.py                  # PDF / Excel document loaders
│
├── app_comparison.py          # Streamlit UI (comparison only)
├── llm_chat.py                # Streamlit UI + AI chat mode
│
├── trial.py                   # Experimental: plan + location extraction
│
├── extracted_bids.json        # Auto‑generated structured output
├── bid_comparison_report.txt  # Auto‑generated comparison report
├── bid_comparison_table.csv   # Auto‑generated comparison table
│
├── .env                       # OpenAI API key
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Install Dependencies

```bash
pip install streamlit langchain langchain-openai python-dotenv pandas unstructured
pip install "unstructured[all-docs]"
```

### 2️⃣ Add Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_key_here
```

### 3️⃣ Add Bid Files

Place **all PDFs / Excel bid files** inside:

```
./data
```

---

## ▶️ How to Run (IMPORTANT)

You have **multiple valid ways** to use this system 👇

---

## 🟢 OPTION 1: Full UI (Recommended)

### Run Streamlit App (Comparison Only)

```bash
streamlit run app_comparison.py
```

### OR Run Streamlit App (Comparison + Chat)

```bash
streamlit run llm_chat.py
```

✅ Both apps:
- Extract bids
- Compare plans
- Show winners
- Calculate savings

🧠 `llm_chat.py` **adds AI chat** on top of everything.

---

## 🟡 OPTION 2: Script‑Only (Backend / Automation)

If you want **pure processing without UI** 👇

### Step 1: Extract bids

```bash
python bid_extractor.py
```

This will:
- Read all files in `./data`
- Extract **ALL plans** using LLM
- Save output to `extracted_bids.json`

---

### Step 2: Compare bids

```bash
python bid_comparator.py
```

This will:
- Compare same plans across files
- Find lowest price per plan
- Decide overall winner
- Generate:
  - `bid_comparison_report.txt`
  - `bid_comparison_table.csv`

---

## 🔁 Important Execution Logic (READ THIS)

You can:

✔ Run **Streamlit directly** (it internally calls extraction + comparison)  
✔ OR run `bid_extractor.py` → `bid_comparator.py` manually  
✔ OR do both (Streamlit can reuse extracted JSON)

👉 **Order matters only when running scripts manually**:

```
bid_extractor.py  →  bid_comparator.py
```

Streamlit handles this automatically.

---

## 🧪 Fair Comparison Mode (Very Important Feature)

Sometimes:
- Plan exists in only **one bid**
- Comparing it is unfair

🎯 **Fair Comparison Mode**:
- Only compares plans where **2+ files have data**
- Eliminates false winners

Available in both Streamlit apps.

---

## 💬 AI Chat Mode (llm_chat.py)

Ask **business‑style questions**, not technical ones:

Examples:
- `Plan 4101 is best for which bid and why?`
- `Compare plan 4102 across all vendors`
- `Which bid saves the most money overall?`
- `What is the price difference for plan 4104?`

🧠 AI answers are:
- Data‑grounded
- Numeric
- Explain **WHY**, not just WHAT

---

## 📍 Location‑Aware Extraction (trial.py)

`trial.py` is an **experimental extension** that extracts:
- City
- State
- ZIP
- Metro Area (e.g. DFW)
```text
python trial.py
```
Useful for:
- Regional bid analysis
- Location‑based pricing
- Market segmentation

---

## 🏆 Why This Project Is Powerful

✔ No hardcoding of plans  
✔ Handles 50+ plans per file  
✔ Works on messy PDFs  
✔ LLM‑driven intelligence  
✔ UI + API‑style scripts  
✔ Extendable to vendors, locations, HVAC types

This is **enterprise‑grade logic** packaged simply.

---

## 🔮 Future Extensions

- Vendor‑level scoring
- Weight‑based evaluation (price + quality)
- Snowflake / DB integration
- Authentication & multi‑user support
- Cloud deployment

---

