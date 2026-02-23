from config import Config
from utils.logger import logger

class ConversationManager:
    def __init__(self, session_state):
        self.session_state = session_state
        if "mode_messages" not in self.session_state:
            self.session_state.mode_messages = {}
            logger.info("Initialized multi-mode conversation history in session state.")

    def add_message(self, mode: str, role: str, content: str):
        if mode not in self.session_state.mode_messages:
            self.session_state.mode_messages[mode] = []
        
        self.session_state.mode_messages[mode].append({"role": role, "content": content})
        self._trim_history(mode)
        
    def get_history(self, mode: str):
        return self.session_state.mode_messages.get(mode, [])

    def clear_history(self, mode: str):
        self.session_state.mode_messages[mode] = []
        logger.info(f"Conversation history cleared for mode: {mode}")

    def _trim_history(self, mode: str):
        max_msgs = Config.MAX_HISTORY_MESSAGES * 2 
        if len(self.session_state.mode_messages[mode]) > max_msgs:
            logger.info(f"Trimming history for {mode}. Max pairs: {Config.MAX_HISTORY_MESSAGES}")
            self.session_state.mode_messages[mode] = self.session_state.mode_messages[mode][-max_msgs:]
