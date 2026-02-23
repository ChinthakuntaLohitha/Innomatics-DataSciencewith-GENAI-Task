# Deployment Guide: AWS EC2

This guide outlines the steps to deploy the Career Advisor AI on an AWS EC2 instance.

## 1. AWS EC2 Instance Setup
1. **Login to AWS Console** and navigate to EC2.
2. **Launch Instance**:
   - **AMI**: Ubuntu 22.04 LTS.
   - **Instance Type**: t3.small (Recommended for responsive AI response streaming) or t2.micro (Free Tier).
   - **Key Pair**: Create or use an existing one (.pem).
3. **Configure Security Group**:
   - Add **Inbound Rule**: Custom TCP, Port `8501`, Source `0.0.0.0/0`.
   - Add **Inbound Rule**: SSH, Port `22`, Source `Your IP`.

---

## 2. Server Configuration
Connect to your instance via SSH:
```bash
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
```

### Install Dependencies:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git -y
```

### Clone Project:
```bash
git clone <your-repo-url>
cd "Career Advisor"
```

### Setup Environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Environment Variables
Create the `.env` file on the server:
```bash
nano .env
```
Paste your Gemini API key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```
Press `Ctrl+O`, `Enter`, `Ctrl+X` to save.

---

## 4. Background Execution
To keep the application running after you disconnect from SSH, use `tmux`:

1. **Start a tmux session**:
   ```bash
   tmux new -s career_chatbot
   ```
2. **Run the app**:
   ```bash
   source .venv/bin/activate
   streamlit run app.py
   ```
3. **Detach from session**:
   Press `Ctrl+B`, then `D`.

The app will now be live at `http://your-ec2-public-ip:8501`.

---

## 5. Security Best Practices (Production Note)
- **HTTPS**: In a true production environment, use a Reverse Proxy (Nginx) and SSL (Let's Encrypt).
- **Environment Variables**: Use AWS Secrets Manager for sensitive keys if deploying at scale.
- **Auto-Scaling**: Consider Elastic Beanstalk or ECS for multi-user redundancy.
