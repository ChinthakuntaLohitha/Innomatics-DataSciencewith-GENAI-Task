import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from config import Config
from utils.logger import logger
from prompts.prompt_templates import SYSTEM_PROMPT, get_mode_prompt

class GeminiService:
    def __init__(self):
        self.is_configured = False
        if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == "your_api_key_here":
            logger.warning("Gemini API Key is not set or is using the default template. Please set GEMINI_API_KEY in .env")
        else:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.is_configured = True
            
        self.model = genai.GenerativeModel(
            model_name=Config.MODEL_NAME,
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.types.GenerationConfig(
                temperature=Config.TEMPERATURE,
            )
        )
        logger.info(f"Gemini Service initialized with model {Config.MODEL_NAME}")

    def generate_response(self, chat_session, user_message: str, current_mode: str) -> str:
        if not self.is_configured:
             return "I cannot respond because the Gemini API Key is not configured in the `.env` file."
        try:
            logger.info(f"Generating response for mode: {current_mode}")
            mode_instruction = get_mode_prompt(current_mode)
            
            context_message = f"[System Context: User is currently in mode '{current_mode}'. Follow the instructions: {mode_instruction}]\n\nUser: {user_message}"
            
            response = chat_session.send_message(
                context_message,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH
                }
            )
            logger.info("Successfully received response from Gemini API")
            return response.text
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            return "I apologize, but I encountered an error connecting to my AI service. Please check your API key and connection."

    def generate_streaming_response(self, chat_session, user_message: str, current_mode: str):
        if not self.is_configured:
             yield "I cannot respond because the Gemini API Key is not configured in the `.env` file."
             return
        try:
            logger.info(f"Generating streaming response for mode: {current_mode}")
            mode_instruction = get_mode_prompt(current_mode)
            context_message = f"[System Context: User is currently in mode '{current_mode}'. Follow the instructions: {mode_instruction}]\n\nUser: {user_message}"
            
            response = chat_session.send_message(
                context_message,
                stream=True,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH
                }
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Error calling Gemini API (streaming): {str(e)}")
            yield "I apologize, but I encountered an error connecting to my AI service."
            
    def start_chat(self, history=None):
        if not self.is_configured:
            return None
        if history is None:
            history = []
        try:
            formatted_history = []
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                # Strip out the system contexts previously injected to save tokens if needed, 
                # but for simplicity we'll just pass the raw content
                formatted_history.append({"role": role, "parts": [msg["content"]]})
                
            return self.model.start_chat(history=formatted_history)
        except Exception as e:
            logger.error(f"Error starting chat: {str(e)}")
            return None
