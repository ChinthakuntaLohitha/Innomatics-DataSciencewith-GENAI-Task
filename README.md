# Career Advisor AI - Production-Ready Chatbot

## 1. Project Title
**Building a Production-Ready Domain-Specific Chatbot using Gemini GenAI API**

## 2. Project Overview
This application is a professional **Career Advisor Chatbot** built with Streamlit and Google Gemini 1.5 Flash. It follows real-world AI engineering standards, featuring modular architecture, structured multi-turn memory, and advanced prompt engineering.

### Targeted Domain: Career & Professional Growth
The advisor provides structured guidance across four specialized modes:
- **Career Mode**: Mentoring and growth roadmaps.
- **Resume Review Mode**: ATS optimization and content feedback.
- **Skill Gap Mode**: Delta analysis between current skills and target roles.
- **Mock Interview Mode**: Realistic technical and behavioral simulations.

---

## 3. System Architecture
The project follows **Clean Architecture** principles to ensure scalability and maintainability.

### Architecture Flow:
`User` -> `UI (Streamlit)` -> `Backend Logic` -> `Prompt Engineering` -> `Gemini API` -> `Response Processing` -> `UI Rendering`

### Component Breakdown:
- **`app.py`**: User Interface layer (Streamlit). Handles rendering and event management.
- **`services/gemini_service.py`**: API Handling Layer. Manages streaming, error handling, and safety settings.
- **`memory/conversation_manager.py`**: Memory Layer. Manages session-based, mode-specific chat history.
- **`prompts/prompt_templates.py`**: Prompt Management. Stores role-based system instructions and configurable templates.
- **`config.py`**: Configuration Layer. Centralized environment variable and hyperparameter management.
- **`utils/logger.py`**: Logging Layer. Implements file-based and console logging for API tracking and error debugging.

---

## 4. Key Technical Features
- **Secure API Management**: Utilizes `.env` for key isolation.
- **Multi-Turn Context**: Preserves full conversation history per mode.
- **Token Optimization**: Auto-trims history to stay within context windows.
- **Keyboard Efficiency**: Custom JavaScript injection for `Ctrl+K` (Clear History) and native `Shift+Enter` (Multi-line).
- **Production Logging**: All API calls and errors are logged to `logs/app.log`.

---

## 5. Setup & Installation

### Prerequisites:
- Python 3.9+
- Google Gemini API Key

### Local Installation:
1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd "Career Advisor"
   ```
2. **Setup Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment**:
   Create a `.env` file:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
5. **Run Application**:
   ```bash
   streamlit run app.py
   ```

---

## 6. Cloud Deployment (AWS EC2)
For detailed instructions on deploying to an AWS EC2 instance, refer to [DEPLOYMENT.md](./DEPLOYMENT.md).

### Summary Deployment Checklist:
- [x] Launch EC2 (Ubuntu 22.04 LTS).
- [x] Configure Security Group (Open Port 8501).
- [x] Install Python and Git.
- [x] Clone and install dependencies.
- [x] Use `tmux` or `systemd` for background execution.
