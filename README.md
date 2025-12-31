# 12labs

## Flask Web Application

A simple web application for analyzing videos using 12 Labs API and generating YouTube-ready descriptions.

### Prerequisites

1. Python 3.10 or higher
2. TwelveLabs API key

### Setup

1. **Install dependencies:**

   If using `uv`:
   ```bash
   uv sync
   ```

   Or using `pip`:
   ```bash
   pip install -e .
   ```

2. **Set up environment variables:**

   Create a `.env` file in the project root with your TwelveLabs API key:
   ```
   TL_API_KEY=your_api_key_here
   ```

### Running the Application

1. **Start the Flask server:**

   **Option 1 - Direct Python (Recommended):**
   ```bash
   python app.py
   ```

   **Option 2 - Using uv with virtual environment:**
   ```bash
   uv venv
   .venv\Scripts\activate  # On Windows
   # or: source .venv/bin/activate  # On Linux/Mac
   python app.py
   ```

   **Option 3 - Using uv sync and then run:**
   ```bash
   uv sync
   .venv\Scripts\python app.py  # On Windows
   # or: .venv/bin/python app.py  # On Linux/Mac
   ```

2. **Open your browser:**
   Navigate to `http://localhost:5000`

### Usage

1. Select a video index from the dropdown
2. Select a video from the second dropdown (populated based on selected index)
3. View the video thumbnail and name
4. Click "Generate YouTube Description" to analyze the video
5. Copy the generated description using the "Copy to Clipboard" button

