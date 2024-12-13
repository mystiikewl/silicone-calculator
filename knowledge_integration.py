from knowledge_framework import KnowledgeFramework
from pathlib import Path
import streamlit as st
import yaml
import datetime

class CalculatorKnowledge:
    def __init__(self):
        """Initialize the Calculator Knowledge system."""
        self.knowledge_base_path = Path("knowledge_base")
        self.framework = KnowledgeFramework(str(self.knowledge_base_path))
        self._initialize()
    
    def _initialize(self):
        """Initialize knowledge base structure."""
        self.knowledge_base_path.mkdir(exist_ok=True)
        
    def log_calculation(self, inputs: dict, result: dict):
        """Log a calculation session.
        
        Args:
            inputs (dict): Calculator inputs
            result (dict): Calculation results
        """
        session_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'inputs': inputs,
            'results': result,
            'type': 'calculation'
        }
        
        self.framework.document_session(session_data)
    
    def get_insights(self) -> list:
        """Get insights from accumulated calculations.
        
        Returns:
            list: List of insights
        """
        knowledge = self.framework.extract_knowledge()
        return knowledge.get('recommendations', [])
    
    def update_learning(self):
        """Update learning based on accumulated knowledge."""
        knowledge = self.framework.extract_knowledge()
        self.framework.refine_strategy(knowledge)

def initialize_knowledge_system():
    """Initialize or get the knowledge system."""
    if 'knowledge_system' not in st.session_state:
        st.session_state.knowledge_system = CalculatorKnowledge()
    return st.session_state.knowledge_system
