"""
Week 10: AI Integration with Google Gemini API
Domain-specific AI Assistants with isolated data access.

Each domain has its own API key and can only access its specific database tables.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

# Try to import google.generativeai
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

# Try to load dotenv
try:
    from dotenv import load_dotenv
    # Try multiple possible locations for .env file
    env_paths = [
        Path(__file__).parent / '.env',
        Path.cwd() / '.env',
        Path(__file__).parent.parent / '.env',
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
    else:
        load_dotenv()  # Try default location
except ImportError:
    pass  # dotenv not installed, rely on system environment variables


class DomainAIAssistant:
    """
    Domain-specific AI Assistant powered by Google Gemini.
    Each domain has its own API key and restricted data access.
    """
    
    # Domain configurations
    DOMAIN_CONFIG = {
        'cybersecurity': {
            'env_key': 'GEMINI_API_KEY_CYBER',
            'name': 'Cybersecurity Analyst AI',
            'blocked_topics': [
                'dataset catalog', 'data governance', 'data quality score', 'archiving policy',
                'IT ticket', 'service desk', 'help desk', 'ticket resolution', 'SLA compliance',
                'staff performance', 'customer satisfaction rating'
            ],
            'restricted_message': """I am the Cybersecurity AI Assistant. I specialize in:
- Security incident analysis and response
- Threat detection and cybersecurity concepts
- Phishing, malware, and vulnerability analysis
- Security best practices and compliance
- General cybersecurity knowledge

I cannot answer questions about data science/datasets or IT support tickets.
Please ask a cybersecurity-related question.""",
            'system_prompt': """You are a Senior Cybersecurity Analyst AI Assistant.

You can answer ANY question related to cybersecurity, including:
- Security incidents and threat analysis from the provided data
- General cybersecurity concepts, terminology, and best practices
- Phishing attacks, malware, ransomware, and how to prevent them
- Vulnerability management and penetration testing
- Incident response procedures and frameworks (NIST, ISO 27001, etc.)
- Network security, encryption, authentication
- Security compliance and risk assessment
- Career advice in cybersecurity
- Explanations of security tools and technologies

RESTRICTIONS (only these topics are blocked):
- You CANNOT discuss data science topics, dataset catalogs, or data governance
- You CANNOT discuss IT support tickets, service desk metrics, or IT operations
- If asked about these blocked topics, politely decline and explain you only handle cybersecurity

You have access to security incident data which you should use when relevant to the question."""
        },
        'datascience': {
            'env_key': 'GEMINI_API_KEY_DATA',
            'name': 'Data Science AI',
            'blocked_topics': [
                'security incident', 'phishing', 'malware', 'ransomware', 'cyber attack',
                'threat detection', 'vulnerability', 'IT ticket', 'service desk', 'help desk',
                'ticket resolution', 'SLA compliance', 'staff performance'
            ],
            'restricted_message': """I am the Data Science AI Assistant. I specialize in:
- Dataset management and data governance
- Data quality and metadata management
- Data analysis and statistics
- General data science concepts and best practices

I cannot answer questions about security incidents or IT support tickets.
Please ask a data science-related question.""",
            'system_prompt': """You are a Senior Data Scientist AI Assistant.

You can answer ANY question related to data science, including:
- Dataset management and governance from the provided catalog data
- General data science concepts, terminology, and methodologies
- Data quality assessment and improvement strategies
- Data formats (CSV, JSON, Parquet, etc.) and their use cases
- Database design and data modeling
- ETL pipelines and data engineering
- Statistics and data analysis techniques
- Machine learning concepts and applications
- Data visualization best practices
- Career advice in data science
- Python, SQL, and data tools

RESTRICTIONS (only these topics are blocked):
- You CANNOT discuss security incidents, threats, or cybersecurity topics
- You CANNOT discuss IT support tickets, service desk, or IT operations
- If asked about these blocked topics, politely decline and explain you only handle data science

You have access to dataset catalog metadata which you should use when relevant to the question."""
        },
        'it_operations': {
            'env_key': 'GEMINI_API_KEY_IT',
            'name': 'IT Operations AI',
            'blocked_topics': [
                'security incident', 'phishing', 'malware', 'ransomware', 'cyber attack',
                'threat detection', 'vulnerability', 'dataset catalog', 'data governance',
                'data quality score', 'archiving policy', 'data science'
            ],
            'restricted_message': """I am the IT Operations AI Assistant. I specialize in:
- IT ticket management and service desk operations
- IT support processes and best practices
- SLA management and performance metrics
- General IT operations knowledge

I cannot answer questions about security incidents or data science/datasets.
Please ask an IT operations-related question.""",
            'system_prompt': """You are a Senior IT Operations Manager AI Assistant.

You can answer ANY question related to IT operations, including:
- IT ticket management and analysis from the provided data
- General IT support concepts and best practices
- Service desk optimization and ITIL frameworks
- SLA management and compliance strategies
- Hardware and software troubleshooting concepts
- Network administration basics
- User account and access management
- IT asset management
- Customer service in IT support
- Career advice in IT operations
- IT tools and ticketing systems

RESTRICTIONS (only these topics are blocked):
- You CANNOT discuss security incidents, threats, or cybersecurity topics
- You CANNOT discuss dataset catalogs, data governance, or data science
- If asked about these blocked topics, politely decline and explain you only handle IT operations

You have access to IT ticket data which you should use when relevant to the question."""
        }
    }
    
    def __init__(self, domain: str):
        """
        Initialize domain-specific AI Assistant.
        
        Args:
            domain: One of 'cybersecurity', 'datascience', 'it_operations'
        """
        if domain not in self.DOMAIN_CONFIG:
            raise ValueError(f"Invalid domain. Must be one of: {list(self.DOMAIN_CONFIG.keys())}")
        
        self.domain = domain
        self.config = self.DOMAIN_CONFIG[domain]
        self.api_key = os.getenv(self.config['env_key'])
        self.model = None
        self._configure_api()
    
    def _configure_api(self) -> bool:
        """Configure the Gemini API with the domain-specific key."""
        if not GENAI_AVAILABLE:
            print("google-generativeai package not installed")
            return False
            
        if not self.api_key:
            print(f"No API key found for {self.domain} (env var: {self.config['env_key']})")
            return False
        
        try:
            genai.configure(api_key=self.api_key)
            
            # Try to find an available model
            available_model = None
            try:
                # List available models and find a suitable one
                models = genai.list_models()
                for model in models:
                    if 'generateContent' in model.supported_generation_methods:
                        # Prefer flash models, then pro models
                        model_name = model.name
                        if 'flash' in model_name.lower():
                            available_model = model_name
                            break
                        elif 'pro' in model_name.lower() and available_model is None:
                            available_model = model_name
            except Exception as list_error:
                print(f"Could not list models: {list_error}")
            
            # If we found a model from listing, use it; otherwise try common names
            if available_model:
                self.model = genai.GenerativeModel(available_model)
            else:
                # Fallback to trying common model names
                model_options = ['gemini-pro', 'gemini-1.0-pro', 'gemini-1.0-pro-latest']
                for model_name in model_options:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        break
                    except Exception:
                        continue
            
            return self.model is not None
        except Exception as e:
            print(f"Error configuring Gemini API for {self.domain}: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if the API is properly configured."""
        return self.model is not None and self.api_key is not None
    
    def _is_on_topic(self, message: str) -> bool:
        """
        Check if the user's message is NOT about a blocked topic.
        
        The AI can answer general questions - we only block specific cross-domain topics.
        
        Args:
            message: User's question or request
            
        Returns:
            True if the message is allowed (not about blocked topics)
        """
        message_lower = message.lower()
        
        # Check if message contains any blocked topics for this domain
        blocked_topics = self.config.get('blocked_topics', [])
        
        for blocked in blocked_topics:
            if blocked.lower() in message_lower:
                return False
        
        # Allow all other questions (general questions are fine within domain)
        return True
    
    def get_domain_data_context(self, db_manager) -> str:
        """
        Get only the data context relevant to this domain.
        
        Args:
            db_manager: DatabaseManager instance
            
        Returns:
            String containing domain-specific data context
        """
        if self.domain == 'cybersecurity':
            stats = db_manager.get_incident_stats()
            return f"""CYBERSECURITY INCIDENT DATA (Your ONLY data source):
- Total incidents: {stats['total']}
- By status: {stats['by_status']}
- By severity: {stats['by_severity']}
- By threat type: {stats['by_threat_type']}
- Average resolution time: {stats['avg_resolution_hours']} hours

You can ONLY analyze and discuss this security incident data."""

        elif self.domain == 'datascience':
            stats = db_manager.get_dataset_stats()
            return f"""DATASET CATALOG DATA (Your ONLY data source):
- Total datasets: {stats['total']}
- Total storage: {stats['total_size_gb']} GB
- By department: {stats['by_department']}
- By status: {stats['by_status']}
- Average quality score: {stats['avg_quality_score']}

You can ONLY analyze and discuss this dataset catalog data."""

        elif self.domain == 'it_operations':
            stats = db_manager.get_ticket_stats()
            return f"""IT TICKET DATA (Your ONLY data source):
- Total tickets: {stats['total']}
- By status: {stats['by_status']}
- By category: {stats['by_category']}
- By assigned staff: {stats['by_assignee']}
- SLA compliance: {stats['sla_compliance']}%
- Average resolution time: {stats['avg_resolution_hours']} hours

You can ONLY analyze and discuss this IT ticket data."""
        
        return ""
    
    def chat(self, message: str, db_manager=None) -> str:
        """
        Send a message to the domain-specific AI assistant.
        
        Args:
            message: User's question or request
            db_manager: Optional DatabaseManager for data context
            
        Returns:
            AI response as string
        """
        if not self.is_configured():
            env_key = self.config['env_key']
            return f"""⚠️ **{self.config['name']} Not Configured**

To enable this AI assistant, please:
1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Add to your `.env` file: `{env_key}=your_api_key_here`
3. Restart the application

Each domain requires its own separate API key."""

        # Check if question is on-topic
        if not self._is_on_topic(message):
            return self.config['restricted_message']
        
        try:
            # Build the prompt with domain restrictions
            data_context = ""
            if db_manager:
                data_context = self.get_domain_data_context(db_manager)
            
            prompt = f"""{self.config['system_prompt']}

{data_context}

User question: {message}

Remember: You can ONLY answer questions related to {self.domain.replace('_', ' ')}. 
If this question is outside your domain, politely decline and explain your restrictions."""

            response = self.model.generate_content(prompt)
            
            # Handle response safely
            if response and hasattr(response, 'text') and response.text:
                return response.text
            elif response and hasattr(response, 'candidates') and response.candidates:
                # Try to extract text from candidates
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    return ''.join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
            
            return "⚠️ The AI could not generate a response. Please try rephrasing your question."
        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
                return f"❌ Invalid API key for {self.config['name']}. Please check your `.env` file."
            elif "quota" in error_msg.lower():
                return f"❌ API quota exceeded for {self.config['name']}. Please try again later."
            elif "blocked" in error_msg.lower():
                return "⚠️ The response was blocked by safety filters. Please try a different question."
            return f"❌ Error communicating with {self.config['name']}: {error_msg}"
    
    def analyze_domain_data(self, db_manager) -> str:
        """
        Perform automated analysis of domain-specific data.
        
        Args:
            db_manager: DatabaseManager instance
            
        Returns:
            AI analysis and recommendations
        """
        if not self.is_configured():
            env_key = self.config['env_key']
            return f"⚠️ {self.config['name']} is not configured. Set {env_key} in your .env file."
        
        data_context = self.get_domain_data_context(db_manager)
        
        analysis_prompts = {
            'cybersecurity': f"""As a cybersecurity expert, analyze this security incident data and provide:
1. Key observations about the threat landscape
2. Identification of the most critical issues (especially any Phishing surge)
3. Recommendations for improving incident response
4. Specific actions to reduce the incident backlog

{data_context}

Provide actionable, security-focused recommendations.""",

            'datascience': f"""As a data governance expert, analyze this dataset catalog and provide:
1. Assessment of current data governance state
2. Identification of storage optimization opportunities
3. Recommendations for data archiving policies
4. Data quality improvement suggestions
5. Resource consumption analysis by department

{data_context}

Provide actionable data governance recommendations.""",

            'it_operations': f"""As an IT operations expert, analyze this service desk data and provide:
1. Identification of any staff performance anomalies
2. Analysis of which processes or statuses cause the greatest delays
3. Assessment of SLA compliance issues
4. Specific recommendations for improving ticket resolution times
5. Training needs or resource allocation improvements

{data_context}

Focus on identifying bottlenecks and performance issues."""
        }
        
        try:
            prompt = analysis_prompts[self.domain]
            response = self.model.generate_content(prompt)
            
            # Handle response safely
            if response and hasattr(response, 'text') and response.text:
                return response.text
            elif response and hasattr(response, 'candidates') and response.candidates:
                # Try to extract text from candidates
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    return ''.join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
            
            return "⚠️ The AI could not generate an analysis. Please try again."
        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
                return f"❌ Invalid API key. Please check your `.env` file."
            elif "quota" in error_msg.lower():
                return f"❌ API quota exceeded. Please try again later."
            elif "blocked" in error_msg.lower():
                return "⚠️ The response was blocked by safety filters. Please try again."
            return f"❌ Error analyzing data: {error_msg}"


# Factory function to get domain-specific assistants
_assistant_instances: Dict[str, DomainAIAssistant] = {}


def get_domain_assistant(domain: str) -> Optional[DomainAIAssistant]:
    """
    Get or create a domain-specific AI Assistant instance.
    
    Args:
        domain: One of 'cybersecurity', 'datascience', 'it_operations'
        
    Returns:
        DomainAIAssistant instance for the specified domain, or None if creation fails
    """
    global _assistant_instances
    
    try:
        if domain not in _assistant_instances:
            _assistant_instances[domain] = DomainAIAssistant(domain)
        
        return _assistant_instances[domain]
    except Exception as e:
        print(f"Error creating assistant for {domain}: {e}")
        return None


# Legacy function for backward compatibility
def get_ai_assistant():
    """Legacy function - returns None. Use get_domain_assistant() instead."""
    return None


if __name__ == "__main__":
    # Test the domain-specific AI Assistants
    print("=" * 60)
    print("  Domain-Specific AI Assistant Test")
    print("=" * 60)
    
    for domain in ['cybersecurity', 'datascience', 'it_operations']:
        assistant = get_domain_assistant(domain)
        config = assistant.config
        
        print(f"\n{config['name']}:")
        print(f"  API Key Env: {config['env_key']}")
        print(f"  Configured: {'Yes ✓' if assistant.is_configured() else 'No ✗'}")
    
    print("\n" + "=" * 60)
    print("Environment Variables Required:")
    print("  GEMINI_API_KEY_CYBER  - For Cybersecurity AI")
    print("  GEMINI_API_KEY_DATA   - For Data Science AI")
    print("  GEMINI_API_KEY_IT     - For IT Operations AI")
    print("=" * 60)
