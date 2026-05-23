# 🔍 DevScan CLI

> A modular, strictly-typed Command Line Interface for static code analysis with AI-powered refactoring suggestions.

**DevScan** is a powerful code analysis tool that performs static code analysis on Python (`.py`) and JavaScript (`.js`) codebases. It calculates health metrics, generates color-coded terminal reports, exports findings to JSON, and launches an interactive chat session with a local Ollama AI model for customized refactoring advice.

---

## 📋 Requirements

Before running DevScan, ensure you have the following installed:

| Requirement | Version | Purpose |
|---|---|---|
| **Python** | 3.10+ | Core runtime |
| **Ollama** | Latest | Local AI model runtime |
| **rich** | Latest | Terminal UI & formatting |
| **requests** | Latest | API communication |

---

## 🚀 Installation & Setup

### Step 1: Navigate to Project Directory
```powershell
cd C:\Users\koushik\OneDrive\Desktop\Dev_Scan
```

### Step 2: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Download the Base AI Model
Ensure Ollama is running, then pull the foundational model:
```bash
ollama pull phi3
```

### Step 4: Create the Custom DevScan AI Agent
Build a specialized AI model using the provided configuration:
```bash
ollama create devscan-ai -f Modelfile
```

---

## 💻 How to Use

### Option 1: Windows Launcher (Recommended)
The easiest way to run DevScan:

```powershell
.\scanit.bat
```

Simply enter your folder path when prompted (e.g., `C:\Users\koushik\OneDrive\Desktop\Dev_Scan`), and the scan will execute automatically.

### Option 2: Command Line Interface

#### Basic Usage - Scan Python Files
```bash
python cli.py <folder_path>
```

#### Scan All Languages (Python + JavaScript)
```bash
python cli.py <folder_path> --lang all
```

#### Export Analysis to JSON (Skip AI Assistant)
```bash
python cli.py <folder_path> --format json --output report.json --no-ai
```

#### Enable Verbose Logging
```bash
python cli.py <folder_path> --verbose
```
Logs are saved to `devscan.log`

---

## 📊 Health Metrics Explained

DevScan evaluates codebase health through three key metrics:

### 1️⃣ Cyclomatic Complexity

**Definition:** A quantitative measure of the number of linearly independent paths through your code. High complexity indicates code with excessive nested conditions, loops, or branches—making it difficult to read, maintain, and test.

**Calculation Method:**
- Base complexity: **1**
- Add **+1** for each branching construct:
  - `if` / `elif` statements
  - `for` loops
  - `while` loops
  - `catch` / `except` blocks
  - `case` / `match` statements
- Python uses Abstract Syntax Tree (AST) analysis
- JavaScript uses regex-based keyword scanning

**Health Thresholds:**
```
🟢 Green:  Max Complexity < 6
🟡 Yellow: Max Complexity ≥ 6
🔴 Red:    Max Complexity ≥ 10
```

---

### 2️⃣ Dead Code Detection

**Definition:** Functions that are defined in your codebase but never called or invoked anywhere.

**Calculation Method:**
1. Accumulate all defined functions across scanned files
2. Accumulate all function call signatures (Python magic methods `__*__` are excluded)
3. Identify functions whose names never appear in the calls list

**Health Thresholds:**
```
🟢 Green:  Dead Functions = 0
🟡 Yellow: Dead Functions ≥ 1
🔴 Red:    Dead Functions ≥ 3
```

---

### 3️⃣ TODO Comments

**Definition:** Comment lines indicating unfinished tasks, quick hacks, or known bugs left by developers.

**Calculation Method:**
- Scans all comments (`#` in Python, `//`, `/*`, `*` in JavaScript)
- Case-insensitive regex detection for keywords:
  - `TODO`
  - `FIXME`
  - `HACK`

**Health Thresholds:**
```
🟢 Green:  TODO Count = 0–2
🟡 Yellow: TODO Count ≥ 3
🔴 Red:    TODO Count ≥ 6
```

---

## 🎯 File Health Status

DevScan assigns a health status to each file based on threshold violations:

| Status | Symbol | Meaning | Condition |
|--------|--------|---------|-----------|
| **Green** | 🟢 | Healthy | No thresholds exceeded |
| **Yellow** | 🟡 | Needs Attention | Some thresholds exceeded (e.g., complexity ≥ 6, dead functions ≥ 1, TODO ≥ 3) |
| **Red** | 🔴 | Critical / High-Risk | Major thresholds exceeded (e.g., complexity ≥ 10, dead functions ≥ 3, TODO ≥ 6) |

---

## 📁 Project Structure

```
Dev_Scan/
├── cli.py                  # Main CLI application
├── scanit.bat             # Windows launcher script
├── Modelfile              # Custom Ollama model configuration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## 🤖 AI-Powered Refactoring

After code analysis, DevScan launches an interactive chat session with your custom AI agent. This allows you to:

- Ask for refactoring suggestions
- Get insights on complexity reduction
- Discuss code improvements in real-time
- Request specific optimization strategies

The AI agent uses the analysis results to provide contextual, actionable advice.

---

## 🔧 Troubleshooting

**Ollama not found in PATH:**
- Ensure Ollama is properly installed and added to your system PATH
- Restart your terminal after installing Ollama

**Model not found:**
- Verify the `devscan-ai` model was created: `ollama list`
- Rebuild if necessary: `ollama create devscan-ai -f Modelfile`

**Python version mismatch:**
- Check your Python version: `python --version`
- Ensure you're using Python 3.10 or higher

---

## 📝 License

This project is provided as-is for development and analysis purposes.

---

## 🤝 Contributing

Found an issue or have a suggestion? Feel free to improve the codebase!