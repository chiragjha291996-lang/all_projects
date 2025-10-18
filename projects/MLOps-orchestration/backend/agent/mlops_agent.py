"""
LangGraph agent for conversational MLOps.
"""
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
import operator

from backend.tools.prefect_tools import PrefectTools
from backend.tools.mlflow_tools import MLflowTools
from backend.tools.google_api_tools import GoogleAPITools
from backend.config import settings


class AgentState(TypedDict):
    """State for the MLOps agent."""
    messages: Annotated[List[BaseMessage], operator.add]
    current_task: Optional[str]
    pipeline_name: Optional[str]
    file_path: Optional[str]


class ConversationalMLOpsAgent:
    """LangGraph-based conversational MLOps agent."""
    
    def __init__(self):
        """Initialize the agent with tools and LLM."""
        # Initialize LLM with error handling
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.1,
                google_api_key=settings.google_api_key,
                convert_system_message_to_human=True,
                model_kwargs={
                    "generation_config": {
                        "thinking_config": {
                            "thinking_budget": 0  # Disable thinking for faster responses
                        }
                    }
                }
            )
        except Exception as e:
            # Fallback for testing or when credentials are not available
            print(f"Warning: Could not initialize Google Generative AI: {e}")
            self.llm = None
        
        # Initialize tools
        self.prefect_tools = PrefectTools(settings.prefect_api_url)
        self.mlflow_tools = MLflowTools(settings.mlflow_tracking_uri, settings.mlflow_experiment_name)
        self.google_api_tools = GoogleAPITools(settings.google_cloud_project)
        
        # Create tool functions
        self.tools = self._create_tools()
        self.tool_node = ToolNode(self.tools)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _create_tools(self) -> List:
        """Create tool functions for the agent."""
        
        @tool
        def register_pipeline(file_path: str, pipeline_name: str) -> str:
            """Register a pipeline from a Python file with Prefect."""
            result = self.prefect_tools.register_pipeline_from_file(file_path, pipeline_name)
            if result["success"]:
                return f"✅ {result['message']}"
            else:
                return f"❌ Error: {result['error']}"
        
        @tool
        def trigger_pipeline_run(pipeline_name: str, parameters: Optional[Dict[str, Any]] = None) -> str:
            """Trigger a run of an existing pipeline."""
            result = self.prefect_tools.trigger_pipeline_run(pipeline_name, parameters)
            if result["success"]:
                return f"✅ {result['message']}"
            else:
                return f"❌ Error: {result['error']}"
        
        @tool
        def get_pipeline_status(flow_run_id: str) -> str:
            """Get the status of a pipeline run."""
            result = self.prefect_tools.get_pipeline_status(flow_run_id)
            if result["success"]:
                return f"📊 Pipeline status: {result['status']}"
            else:
                return f"❌ Error: {result['error']}"
        
        @tool
        def list_pipelines() -> str:
            """List all registered pipelines."""
            result = self.prefect_tools.list_pipelines()
            if result["success"]:
                pipelines = result["pipelines"]
                if pipelines:
                    pipeline_list = "\n".join([f"- {p['name']} ({p['flow_name']})" for p in pipelines])
                    return f"📋 Registered pipelines:\n{pipeline_list}"
                else:
                    return "📋 No pipelines registered yet."
            else:
                return f"❌ Error: {result['error']}"
        
        @tool
        def get_latest_run_metrics(experiment_name: Optional[str] = None) -> str:
            """Get metrics from the latest MLflow run."""
            result = self.mlflow_tools.get_latest_run_metrics(experiment_name)
            if result["success"]:
                metrics = result["metrics"]
                if metrics:
                    metrics_str = "\n".join([f"- {k}: {v}" for k, v in metrics.items()])
                    return f"📈 Latest run metrics:\n{metrics_str}"
                else:
                    return "📈 No metrics found in the latest run."
            else:
                return f"❌ Error: {result['error']}"
        
        @tool
        def promote_model(model_name: str, version: Optional[str] = None, stage: str = "Staging") -> str:
            """Promote a model to a specific stage."""
            result = self.mlflow_tools.promote_model(model_name, version, stage)
            if result["success"]:
                return f"✅ {result['message']}"
            else:
                return f"❌ Error: {result['error']}"
        
        @tool
        def list_models() -> str:
            """List all registered models."""
            result = self.mlflow_tools.list_models()
            if result["success"]:
                models = result["models"]
                if models:
                    model_list = "\n".join([f"- {m['name']}" for m in models])
                    return f"🤖 Registered models:\n{model_list}"
                else:
                    return "🤖 No models registered yet."
            else:
                return f"❌ Error: {result['error']}"
        
        @tool
        def upload_to_gcs(bucket_name: str, file_path: str, destination_name: str) -> str:
            """Upload a file to Google Cloud Storage."""
            result = self.google_api_tools.upload_to_gcs(bucket_name, file_path, destination_name)
            if result["success"]:
                return f"☁️ {result['message']}"
            else:
                return f"❌ Error: {result['error']}"
        
        @tool
        def get_project_info() -> str:
            """Get information about the Google Cloud project."""
            result = self.google_api_tools.get_project_info()
            if result["success"]:
                return f"🔧 Project: {result['project_id']} ({result['credentials_type']})"
            else:
                return f"❌ Error: {result['error']}"
        
        return [
            register_pipeline,
            trigger_pipeline_run,
            get_pipeline_status,
            list_pipelines,
            get_latest_run_metrics,
            promote_model,
            list_models,
            upload_to_gcs,
            get_project_info
        ]
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        def should_continue(state: AgentState) -> str:
            """Determine whether to continue or end."""
            messages = state["messages"]
            last_message = messages[-1]
            
            # If the last message is from the human, continue to agent
            if isinstance(last_message, HumanMessage):
                return "agent"
            # If the last message is from the agent, continue to tools
            elif isinstance(last_message, AIMessage):
                if last_message.tool_calls:
                    return "tools"
                else:
                    return END
            # If the last message is from tools, continue to agent
            elif isinstance(last_message, ToolMessage):
                return "agent"
            else:
                return END
        
        def call_agent(state: AgentState) -> Dict[str, Any]:
            """Call the LLM agent."""
            messages = state["messages"]
            if self.llm is None:
                # Fallback response for testing
                response = AIMessage(content="I'm a test agent. Please set up your Google API credentials to use the full functionality.")
            else:
                response = self.llm.bind_tools(self.tools).invoke(messages)
            return {"messages": [response]}
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", call_agent)
        workflow.add_node("tools", self.tool_node)
        
        # Add edges
        workflow.add_edge("tools", "agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "agent": "agent",
                "tools": "tools",
                END: END
            }
        )
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        return workflow.compile()
    
    def process_message(self, message: str, file_path: Optional[str] = None) -> str:
        """
        Process a user message and return the agent's response.
        
        Args:
            message: User's message
            file_path: Optional path to uploaded file
            
        Returns:
            Agent's response
        """
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "current_task": None,
            "pipeline_name": None,
            "file_path": file_path
        }
        
        # Run the graph
        try:
            final_state = self.graph.invoke(initial_state)
            
            # Extract the final response
            messages = final_state["messages"]
            last_message = messages[-1]
            
            if isinstance(last_message, AIMessage):
                return last_message.content
            else:
                return "I'm processing your request..."
        except Exception as e:
            return f"I encountered an error: {str(e)}"
    
    def get_available_commands(self) -> List[str]:
        """Get a list of available commands for the user."""
        return [
            "set up a new [model_name] pipeline",
            "upload my pipeline script",
            "register my pipeline",
            "run my pipeline",
            "retrain the [model_name] model",
            "what was the accuracy?",
            "show me the latest metrics",
            "promote this model to staging",
            "list all pipelines",
            "list all models",
            "upload to Google Cloud Storage",
            "get project information"
        ]
