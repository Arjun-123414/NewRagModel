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

## 🔍 How It Works (End‑to‑End Explanation)

This section explains **how the system actually handles very large bid documents (80+ pages), multiple vendors, and dozens of plans** in a reliable and scalable way.

The key idea is simple but powerful:
> **The full document is never blindly sent to the LLM.**

Instead, the system breaks the problem into controlled, verifiable steps.

---

### 1️⃣ Document Ingestion & Chunking

- Each PDF or Excel file is first loaded using document loaders.
- Large PDFs are **split into smaller text chunks**.

Why chunking is important:
- Prevents token‑limit issues
- Reduces hallucination
- Improves extraction accuracy

You can think of this as:
> Breaking a large book into smart, readable sections.

---

### 2️⃣ Targeted LLM Analysis (Chunk‑Level)

Each chunk is analyzed independently by the LLM with **very focused prompts**, such as:
- Does this chunk contain a *plan number*?
- Is there a *price or total* mentioned?
- Is this describing *scope or line items*?

Important behavior:
- Chunks without plan‑related information are **ignored**
- Cover pages, legal text, and indexes are automatically filtered out

The LLM is used for **understanding text**, not guessing.

---

### 3️⃣ Plan‑Level Data Extraction

Relevant chunks are converted into structured data.

Information like:
- Plan number
- Plan name
- Price
- Vendor
- Source file

Multiple chunks referring to the same plan are **merged into a single structured record**.

There is **no hardcoding of plan numbers**, so plans can appear anywhere in the document.

---

### 4️⃣ Cross‑File Normalization

Once extraction is complete:
- Plans from all vendors are collected
- Prices are normalized
- The same plan number is matched across different files

This creates a clean, comparable structure such as:
- Plan 4101 → Vendor A vs Vendor B vs Vendor C

This ensures a true **apples‑to‑apples comparison**.

---

### 5️⃣ Fair Comparison Logic

To avoid misleading results:
- Plans that appear in **only one bid are excluded**
- At least **two vendors must have the same plan** for comparison

This prevents false winners and ensures business‑grade accuracy.

---

### 6️⃣ Separation of Intelligence and Calculation

The system clearly separates responsibilities:

- **LLM** is used for:
  - Understanding messy, unstructured text
  - Identifying plans and prices
  - Explaining results in plain language

- **Python logic** is used for:
  - Price comparison
  - Winner selection
  - Savings calculation

This makes results deterministic, auditable, and trustworthy.

---

### 7️⃣ AI Chat Layer (Optional)

In chat mode (`llm_chat.py`):
- The LLM does **not re‑read PDFs**
- It only sees already extracted structured data (JSON / tables)

This makes the chat:
- Fast
- Cost‑efficient
- Grounded in real data

---

### 🧠 Simple Mental Model

- Documents are read **piece by piece**, not blindly
- LLM acts like a **junior analyst**
- Python acts like a **senior auditor**

The result is a system that can handle complex bid documents and still produce **reliable, decision‑ready outputs**.

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
- `Plan 4101 kis file ka best hai aur kyun?`
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
Because **this is how AI should be used — to decide better, faster, cheaper.**

