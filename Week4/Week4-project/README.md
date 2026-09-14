# Week 4 Project – Secured Library App + AI Service

## How to Run the AI Service

### 1. Go to the AI service folder

```bash
cd ai-services
```

### 2. Activate the virtual environment

Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the FastAPI server

```bash
uvicorn main:app --reload
```

### 5. Open Swagger UI

http://127.0.0.1:8000/docs

### Example Request

POST `/summarize`

```json
{
  "title": "Atomic Habits",
  "description": "A practical guide to building good habits and breaking bad ones."
}
```

### Note

During Week 4, the ASP.NET Core Library API and the FastAPI AI Service are independent applications. The .NET API does not call the AI service yet. Their integration will be completed in Week 6.