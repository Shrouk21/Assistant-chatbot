import gradio as gr
import sys
import os
import json
from datetime import datetime
from typing import List, Tuple, Dict, Any

# Add the current directory to the path to import the agent
sys.path.insert(0, os.path.abspath('.'))

try:
    from agent.agent_runner import create_context_aware_agent, run_agent_with_query
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed and the agent module is available.")

# Global variables
agent_executor = None
chat_history = []
thinking_enabled = False

def initialize_agent():
    """Initialize the agent executor"""
    global agent_executor
    try:
        agent_executor = create_context_aware_agent()
        return "✅ Agent initialized successfully!"
    except Exception as e:
        return f"❌ Error initializing agent: {str(e)}"

def toggle_thinking_process(enabled):
    """Toggle the thinking process display"""
    global thinking_enabled
    thinking_enabled = enabled
    status = "enabled" if enabled else "disabled"
    return f"🧠 Thinking process {status}"

def format_thinking_steps(intermediate_steps):
    """Format the agent's thinking steps for display"""
    if not intermediate_steps:
        return ""
    
    thinking_text = "\n🧠 **Agent Thinking Process:**\n\n"
    for i, (action, observation) in enumerate(intermediate_steps, 1):
        thinking_text += f"**Step {i}:**\n"
        thinking_text += f"🔧 **Tool:** {action.tool}\n"
        thinking_text += f"📝 **Input:** {action.tool_input}\n"
        thinking_text += f"📊 **Output:** {observation}\n\n"
    
    return thinking_text

def process_query_with_thinking(query, history, show_thinking):
    """Process a user query and return the response with optional thinking process"""
    global chat_history, thinking_enabled
    
    if not query.strip():
        return history, "", ""
    
    if agent_executor is None:
        error_msg = "❌ Agent not initialized. Please click 'Initialize Agent' first."
        history.append([query, error_msg])
        chat_history.append({"user": query, "assistant": error_msg, "timestamp": datetime.now().isoformat()})
        return history, "", ""
    
    try:
        # Add user message to history immediately
        history.append([query, "🤔 Processing..."])
        
        # Get response from agent with intermediate steps
        response = agent_executor.invoke({"input": query}, return_only_outputs=False)
        agent_response = response.get("output", "No response generated")
        intermediate_steps = response.get("intermediate_steps", [])
        
        # Format thinking process if enabled
        thinking_text = ""
        if show_thinking and intermediate_steps:
            thinking_text = format_thinking_steps(intermediate_steps)
        
        # Combine response with thinking process if enabled
        full_response = agent_response
        if thinking_text:
            full_response = f"{agent_response}\n\n---\n{thinking_text}"
        
        # Update the last message with the actual response
        history[-1][1] = full_response
        
        # Save to persistent chat history
        chat_history.append({
            "user": query,
            "assistant": agent_response,
            "thinking": thinking_text if show_thinking else "",
            "timestamp": datetime.now().isoformat()
        })
        
        return history, "", thinking_text if show_thinking else ""
        
    except Exception as e:
        error_msg = f"❌ Error processing query: {str(e)}"
        history[-1][1] = error_msg
        chat_history.append({"user": query, "assistant": error_msg, "timestamp": datetime.now().isoformat()})
        return history, "", ""

def clear_chat():
    """Clear the chat history"""
    global chat_history
    chat_history = []
    return [], "", ""

def export_chat_history():
    """Export chat history as JSON"""
    if not chat_history:
        return None
    
    filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(os.getcwd(), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(chat_history, f, indent=2, ensure_ascii=False)
    
    return filepath

def load_chat_history(file):
    """Load chat history from uploaded JSON file"""
    global chat_history
    
    if file is None:
        return [], "No file uploaded"
    
    try:
        with open(file.name, 'r', encoding='utf-8') as f:
            loaded_history = json.load(f)
        
        # Validate the structure
        if not isinstance(loaded_history, list):
            return [], "Invalid file format"
        
        # Convert to Gradio chat format
        gradio_history = []
        for item in loaded_history:
            if isinstance(item, dict) and "user" in item and "assistant" in item:
                user_msg = item["user"]
                assistant_msg = item["assistant"]
                if item.get("thinking"):
                    assistant_msg += f"\n\n---\n{item['thinking']}"
                gradio_history.append([user_msg, assistant_msg])
        
        chat_history = loaded_history
        return gradio_history, f"✅ Loaded {len(loaded_history)} messages from chat history"
        
    except Exception as e:
        return [], f"❌ Error loading file: {str(e)}"

def get_sample_queries():
    """Return sample queries for testing"""
    return [
        "What is LangChain used for?",
        "In the context of neural networks for computer vision, how do convolutional layers work?",
        "Tell me about attention mechanisms",
        "Explain the difference between supervised and unsupervised learning",
        "What are the main components of a transformer architecture?"
    ]

def load_sample_query(query):
    """Load a sample query into the input box"""
    return query

def get_chat_stats():
    """Get statistics about the current chat session"""
    if not chat_history:
        return "📊 No messages in current session"
    
    total_messages = len(chat_history)
    user_messages = sum(1 for msg in chat_history if "user" in msg)
    
    if chat_history:
        first_msg_time = datetime.fromisoformat(chat_history[0]["timestamp"])
        last_msg_time = datetime.fromisoformat(chat_history[-1]["timestamp"])
        duration = last_msg_time - first_msg_time
        
        return f"📊 Session Stats: {total_messages} messages | Duration: {str(duration).split('.')[0]} | Started: {first_msg_time.strftime('%H:%M:%S')}"
    
    return "📊 No messages in current session"

# Custom CSS for better styling
custom_css = """
.gradio-container {
    max-width: 1400px !important;
    margin: auto !important;
}

.chat-message {
    padding: 10px;
    margin: 5px 0;
    border-radius: 10px;
}

.user-message {
    background-color: #e3f2fd;
    margin-left: 20%;
}

.bot-message {
    background-color: #f5f5f5;
    margin-right: 20%;
}

.title-container {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    margin-bottom: 20px;
}

.status-box {
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
}

.sample-queries {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}

.thinking-box {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    font-family: monospace;
    font-size: 12px;
    max-height: 300px;
    overflow-y: auto;
}

.stats-box {
    background-color: #e8f5e8;
    border-radius: 5px;
    padding: 10px;
    margin: 5px 0;
    font-size: 12px;
}
"""

# Create the enhanced Gradio interface
with gr.Blocks(css=custom_css, title="Context-Aware Agent UI - Enhanced") as demo:
    # Title and description
    with gr.Row():
        gr.HTML("""
        <div class="title-container">
            <h1>🤖 Context-Aware Agent Interface - Enhanced</h1>
            <p>An intelligent agent powered by LangChain with context-aware capabilities, thinking process display, and chat history management</p>
        </div>
        """)
    
    # Status and controls section
    with gr.Row():
        with gr.Column(scale=2):
            status_display = gr.Textbox(
                label="🔧 Agent Status",
                value="❌ Agent not initialized",
                interactive=False,
                elem_classes=["status-box"]
            )
        with gr.Column(scale=1):
            init_btn = gr.Button(
                "🚀 Initialize Agent",
                variant="primary",
                size="lg"
            )
    
    # Thinking process controls
    with gr.Row():
        with gr.Column(scale=2):
            thinking_toggle = gr.Checkbox(
                label="🧠 Show Thinking Process",
                value=False,
                info="Display the agent's reasoning steps and tool usage"
            )
        with gr.Column(scale=2):
            thinking_status = gr.Textbox(
                label="Thinking Status",
                value="🧠 Thinking process disabled",
                interactive=False
            )
    
    # Chat history management
    with gr.Row():
        with gr.Column(scale=1):
            export_btn = gr.Button("💾 Export Chat", variant="secondary")
            download_file = gr.File(label="Download Chat History", visible=False)
        with gr.Column(scale=1):
            upload_file = gr.File(label="📁 Upload Chat History", file_types=[".json"])
        with gr.Column(scale=2):
            stats_display = gr.Textbox(
                label="📊 Session Statistics",
                value="📊 No messages in current session",
                interactive=False,
                elem_classes=["stats-box"]
            )
    
    # Main chat interface
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="💬 Chat with Agent",
                height=500,
                show_label=True,
                elem_id="chatbot"
            )
            
            with gr.Row():
                query_input = gr.Textbox(
                    label="Your Query",
                    placeholder="Ask me anything about AI, machine learning, or any topic...",
                    lines=2,
                    scale=4
                )
                submit_btn = gr.Button("📤 Send", variant="primary", scale=1)
            
            with gr.Row():
                clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
        
        # Sample queries and thinking display sidebar
        with gr.Column(scale=1):
            gr.HTML("""
            <div class="sample-queries">
                <h3>💡 Sample Queries</h3>
                <p>Click on any query below to try it out:</p>
            </div>
            """)
            
            sample_queries = get_sample_queries()
            for i, query in enumerate(sample_queries):
                sample_btn = gr.Button(
                    f"📝 {query[:50]}{'...' if len(query) > 50 else ''}",
                    variant="secondary",
                    size="sm"
                )
                sample_btn.click(
                    fn=lambda q=query: q,
                    outputs=query_input
                )
    
    # Thinking process display (when enabled)
    with gr.Row():
        thinking_display = gr.Textbox(
            label="🧠 Agent Thinking Process",
            lines=10,
            max_lines=15,
            visible=False,
            elem_classes=["thinking-box"]
        )
    
    # Footer
    with gr.Row():
        gr.HTML("""
        <div style="text-align: center; padding: 20px; color: #666;">
            <p>🔧 Built with Gradio | 🤖 Powered by LangChain | ⚡ Context-Aware Intelligence | 🧠 Enhanced with Thinking Process</p>
            <p><small>Timestamp: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</small></p>
        </div>
        """)
    
    # Event handlers
    init_btn.click(
        fn=initialize_agent,
        outputs=status_display
    )
    
    thinking_toggle.change(
        fn=toggle_thinking_process,
        inputs=thinking_toggle,
        outputs=thinking_status
    )
    
    thinking_toggle.change(
        fn=lambda x: gr.update(visible=x),
        inputs=thinking_toggle,
        outputs=thinking_display
    )
    
    submit_btn.click(
        fn=process_query_with_thinking,
        inputs=[query_input, chatbot, thinking_toggle],
        outputs=[chatbot, query_input, thinking_display]
    ).then(
        fn=get_chat_stats,
        outputs=stats_display
    )
    
    query_input.submit(
        fn=process_query_with_thinking,
        inputs=[query_input, chatbot, thinking_toggle],
        outputs=[chatbot, query_input, thinking_display]
    ).then(
        fn=get_chat_stats,
        outputs=stats_display
    )
    
    clear_btn.click(
        fn=clear_chat,
        outputs=[chatbot, query_input, thinking_display]
    ).then(
        fn=get_chat_stats,
        outputs=stats_display
    )
    
    export_btn.click(
        fn=export_chat_history,
        outputs=download_file
    ).then(
        fn=lambda x: gr.update(visible=True) if x else gr.update(visible=False),
        inputs=download_file,
        outputs=download_file
    )
    
    upload_file.upload(
        fn=load_chat_history,
        inputs=upload_file,
        outputs=[chatbot, status_display]
    ).then(
        fn=get_chat_stats,
        outputs=stats_display
    )

# Launch the interface
if __name__ == "__main__":
    print("🚀 Starting Enhanced Context-Aware Agent UI...")
    print("📝 New Features:")
    print("   - 🧠 Thinking process display")
    print("   - 💾 Chat history export/import")
    print("   - 📊 Session statistics")
    print("   - 🔄 Persistent chat management")
    print("\n📝 Make sure you have:")
    print("   - Ollama installed and running")
    print("   - Required environment variables set in .env file")
    print("   - All dependencies installed")
    print("\n🌐 The interface will be available at the URL shown below:")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=True,
        show_error=True,
        debug=True
    )

