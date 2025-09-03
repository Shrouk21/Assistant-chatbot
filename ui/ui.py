import gradio as gr
import sys
import os
from datetime import datetime

# Add the current directory to the path to import the agent
sys.path.insert(0, os.path.abspath('.'))

try:
    from agent.agent_runner import create_context_aware_agent, run_agent_with_query
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed and the agent module is available.")

# Global variable to store the agent executor
agent_executor = None

def initialize_agent():
    """Initialize the agent executor"""
    global agent_executor
    try:
        agent_executor = create_context_aware_agent()
        return "✅ Agent initialized successfully!"
    except Exception as e:
        return f"❌ Error initializing agent: {str(e)}"

def process_query(query, history):
    """Process a user query and return the response"""
    if not query.strip():
        return history, ""
    
    if agent_executor is None:
        error_msg = "❌ Agent not initialized. Please click 'Initialize Agent' first."
        history.append([query, error_msg])
        return history, ""
    
    try:
        # Add user message to history
        history.append([query, "🤔 Processing..."])
        
        # Get response from agent
        response = agent_executor.invoke({"input": query})
        agent_response = response.get("output", "No response generated")
        
        # Update the last message with the actual response
        history[-1][1] = agent_response
        
    except Exception as e:
        error_msg = f"❌ Error processing query: {str(e)}"
        history[-1][1] = error_msg
    
    return history, ""

def clear_chat():
    """Clear the chat history"""
    return [], ""

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

# Custom CSS for better styling
custom_css = """
.gradio-container {
    max-width: 1200px !important;
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
"""

# Create the Gradio interface
with gr.Blocks(css=custom_css, title="Context-Aware Agent UI") as demo:
    # Title and description
    with gr.Row():
        gr.HTML("""
        <div class="title-container">
            <h1>🤖 Context-Aware Agent Interface</h1>
            <p>An intelligent agent powered by LangChain with context-aware capabilities</p>
        </div>
        """)
    
    # Status section
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
        
        # Sample queries sidebar
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
    
    # Footer
    with gr.Row():
        gr.HTML("""
        <div style="text-align: center; padding: 20px; color: #666;">
            <p>🔧 Built with Gradio | 🤖 Powered by LangChain | ⚡ Context-Aware Intelligence</p>
            <p><small>Timestamp: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</small></p>
        </div>
        """)
    
    # Event handlers
    init_btn.click(
        fn=initialize_agent,
        outputs=status_display
    )
    
    submit_btn.click(
        fn=process_query,
        inputs=[query_input, chatbot],
        outputs=[chatbot, query_input]
    )
    
    query_input.submit(
        fn=process_query,
        inputs=[query_input, chatbot],
        outputs=[chatbot, query_input]
    )
    
    clear_btn.click(
        fn=clear_chat,
        outputs=[chatbot, query_input]
    )

# Launch the interface
if __name__ == "__main__":
    print("🚀 Starting Context-Aware Agent UI...")
    print("📝 Make sure you have:")
    print("   - Ollama installed and running")
    print("   - Required environment variables set in .env file")
    print("   - All dependencies installed")
    print("\n🌐 The interface will be available at the URL shown below:")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True,
        debug=True
    )

