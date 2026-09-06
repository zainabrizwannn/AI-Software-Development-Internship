# Week 3 Library Management System

## Project Overview
This project is a Library Management System developed during Week 3 of the AI Software Development Internship. The application consists of:
- ASP.NET Core Web API
- SQL Server with Entity Framework Core
- Angular Frontend
- Standalone Python AI Script using the Gemini API

## Tech Stack
### Backend
- ASP.NET Core Web API
- Entity Framework Core
- SQL Server

### Frontend
- Angular
- TypeScript
- Reactive Forms
- HttpClient

### AI
- Python
- Google Gemini API
- python-dotenv


## Project Structure
Week3-Project/
│
├── Backend/
├── Frontend/
├── ai-scripts/
└── README.md

## Running the Backend
cd Backend
dotnet restore
dotnet ef database update
dotnet run
Swagger:
https://localhost:5194/swagger

## Running the Frontend
cd Frontend
npm install
ng serve
Angular:
http://localhost:4200

## Running the AI Script
cd ai-scripts
python -m venv .venv
.venv\Scripts\Activate
pip install google-genai python-dotenv
python main.py


## API Endpoints
| Method | Endpoint | Description |
| GET | /api/Books | Get all books |
| GET | /api/Books/{id} | Get book by ID |
| POST | /api/Books | Add a book |
| PUT | /api/Books/{id} | Update a book |
| DELETE | /api/Books/{id} | Delete a book |
| POST | /api/Auth/login | Login endpoint |

## Data Flow
Angular
    ↓
ASP.NET Core API
    ↓
Service Layer
    ↓
Repository Layer
    ↓
Entity Framework Core
    ↓
SQL Server

## AI Track
The standalone Python script accepts a book title and description, sends them to the Google Gemini API, and generates a one paragraph summary along with a suggested genre. This script runs independently from the ASP.NET Core API and demonstrates basic LLM integration.

## Features
- CRUD operations for books
- Author and Category relationships
- SQL Server persistence
- Angular frontend connected to the API
- Loading and error handling
- Login endpoint foundation
- AI-powered book summary and genre suggestion