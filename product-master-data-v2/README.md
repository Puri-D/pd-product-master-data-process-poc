# UOM Extraction + Department View Generation POC 
Extract packaging hierarchy and transform to departmental views using AI-powered extraction.

## What You Need to Install

### 1. Python 3.9+
Download from: https://www.python.org/downloads/

**Important:** Check "Add Python to PATH" during installation

### 2. Ollama
Download from: https://ollama.com/download

### 3. Python Packages
Open terminal in project folder and run:
```bash
pip install -r requirements.txt
```

### 4. Ollama Models
Pull required models:
```bash
ollama pull llama3.1:8b
ollama pull qwen3-vl:8b
```

## 🚀 How to Run

### Step 1: Start Ollama (Or just open Ollama desktop app)
Open a terminal and run:
```bash
ollama serve
```
Keep this terminal open.

### Step 2: Run the App
Open another terminal in project folder and run:
```bash
streamlit run streamlit_uom.py
```

The app will open in your browser at `http://localhost:8501`

## Sharing to Another PC

Copy the entire project folder to the new PC, then follow the installation steps above.
