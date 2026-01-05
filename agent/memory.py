import json
import os
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger

class Memory:
    """
    The Notebook: Tracks everything the agent does.
    """
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.start_time = datetime.now()

    def add_step(self, step_data: Dict[str, Any]):
        self.history.append(step_data)

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history

    def save_session(self, log_dir: str = "logs"):
        """Save history to JSON."""
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"{log_dir}/session_{timestamp}.json"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            logger.info(f"Session saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return None
