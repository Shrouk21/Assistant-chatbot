# ui/ui.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import gradio as gr
import time
from datetime import datetime
from agent.agent_runner import create_context_aware_agent, run_agent_with_query

# Custom CSS for modern styling
custom_css = """
/* Main container styling */
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    min-height: 100vh;
}

/* Header styling */
.header-container {
    text-align: center;
    padding: 2rem 0;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    margin: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* Chat interface styling */
.chat-container {
    background: rgba(255, 255, 255, 0.95) !important;
    border-radius: 20px !important;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    backdrop-filter: blur(20px) !important;
}

/* Message styling */
.message {
    border-radius: 15px !important;
    padding: 1rem !important;
    margin: 0.5rem 0 !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
}

.user-message {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
    color: white !important;
    margin-left: 2rem !important;
}

.bot-message {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
    color: #2d3748 !important;
    margin-right: 2rem !important;
}

/* Input styling */
.input-container {
    background: rgba(255, 255, 255, 0.9) !important;
    border-radius: 25px !important;
    border: 2px solid transparent !important;
    background-clip: padding-box !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1) !important;
}

.input-container:focus-within {
    border: 2px solid #4facfe !important;
    transform: translateY(-2px) !important;
    transition: all 0.3s ease !important;
}

/* Button styling */
.send-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    border-radius: 20px !important;
    padding: 0.8rem 2rem !important;
    color: white !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4) !important;
}

.send-button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
}

/* Sidebar styling */
.sidebar {
    background: rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 15px !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

/* Status indicators */
.status-indicator {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 8px;
}

.status-online { background-color: #10b981; }
.status-thinking { background-color: #f59e0b; animation: pulse 2s infinite; }
.status-error { background-color: #ef4444; }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Responsive design */
@media (max-width: 768px) {
    .user-message { margin-left: 0.5rem !important; }
    .bot-message { margin-right: 0.5rem !important; }
    .header-container { margin: 0.5rem; padding: 1rem; }
}
"""

# Global agent instance
agent_executor = None

def initialize_agent():
    """Initialize the agent on startup"""
    global agent_executor
    try:
        agent_executor = create_context_aware_agent()
        return "🟢 Agent initialized successfully"
    except Exception as e:
        return f"🔴 Failed to initialize agent: {str(e)}"

def get_agent_response(message, history, show_thinking=False):
    """Get response from the context-aware agent"""
    global agent_executor
    
    if not agent_executor:
        return "❌ Agent not initialized. Please restart the interface.", history
    
    if not message.strip():
        return "", history
    
    # Add user message to history
    history.append([message, None])
    
    try:
        # Show thinking indicator
        if show_thinking:
            history[-1][1] = "🤔 Thinking and analyzing context..."
            yield "", history
            time.sleep(1)
        
        # Get agent response
        start_time = time.time()
        response = agent_executor.invoke({"input": message})
        end_time = time.time()
        
        # Format the response
        bot_response = response["output"]
        response_time = f"\n\n*Response time: {end_time - start_time:.2f}s*"
        
        # Update history with final response
        history[-1][1] = bot_response + response_time
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        history[-1][1] = error_msg
    
    yield "", history

def clear_chat():
    """Clear the chat history"""
    return [], ""

def get_example_questions():
    """Return a list of example questions"""
    return [
        "What is machine learning?",
        "In the context of neural networks, how do transformers work?",
        "Explain attention mechanisms in deep learning",
        "What is LangChain used for?",
        "How do convolutional layers work in computer vision?",
        "Tell me about reinforcement learning",
        "What are the differences between supervised and unsupervised learning?"
    ]

def load_example(example_text):
    """Load an example question into the input"""
    return example_text

def create_modern_ui():
    """Create the modern Gradio interface"""
    
    # Initialize agent status
    init_status = initialize_agent()
    
    with gr.Blocks(
        css=custom_css,
        title="🤖 Context-Aware AI Assistant",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="purple",
            neutral_hue="slate"
        )
    ) as interface:
        
        # Header
        with gr.Row():
            gr.HTML("""
                <div class="header-container">
                    <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
                        🤖 Context-Aware AI Assistant
                    </h1>
                    <p style="color: rgba(255, 255, 255, 0.8); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
                        Intelligent conversational agent that searches for context when needed
                    </p>
                </div>
            """)
        
        with gr.Row():
            # Main chat interface
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    [],
                    elem_id="chatbot",
                    height=500,
                    show_label=False,
                    avatar_images=["👤", "🤖"],
                    bubble_full_width=False,
                    show_share_button=False,
                    show_copy_button=True
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Ask me anything! I'll search for context if needed...",
                        show_label=False,
                        scale=4,
                        container=False,
                        elem_classes=["input-container"]
                    )
                    
                    send_btn = gr.Button(
                        "Send 🚀",
                        scale=1,
                        variant="primary",
                        elem_classes=["send-button"]
                    )
                
                with gr.Row():
                    clear_btn = gr.Button("Clear Chat 🗑️", variant="secondary")
                    thinking_toggle = gr.Checkbox(
                        label="Show thinking process",
                        value=True,
                        scale=1
                    )
            
            # Sidebar with examples and info
            with gr.Column(scale=1, elem_classes=["sidebar"]):
                gr.HTML("""
                    <div style="padding: 1rem; text-align: center;">
                        <h3 style="color: white; margin-bottom: 1rem;">🎯 How it works</h3>
                        <div style="color: rgba(255, 255, 255, 0.8); font-size: 0.9rem; line-height: 1.6;">
                            <p>1. 🕵️ Analyzes your question</p>
                            <p>2. 🌐 Searches web if context is missing</p>
                            <p>3. ✅ Checks information relevance</p>
                            <p>4. 💡 Provides comprehensive answer</p>
                        </div>
                    </div>
                """)
                
                # Status indicator
                status_display = gr.HTML(f"""
                    <div style="padding: 1rem; text-align: center; color: white;">
                        <h4>Agent Status</h4>
                        <p>{init_status}</p>
                    </div>
                """)
                
                # Example questions
                gr.HTML("""
                    <div style="padding: 1rem 0; color: white;">
                        <h4 style="text-align: center; margin-bottom: 1rem;">💡 Example Questions</h4>
                    </div>
                """)
                
                examples = get_example_questions()
                for i, example in enumerate(examples[:5]):  # Show first 5 examples
                    example_btn = gr.Button(
                        example,
                        variant="secondary",
                        size="sm",
                        elem_id=f"example_{i}"
                    )
                    example_btn.click(
                        fn=load_example,
                        inputs=[gr.State(example)],
                        outputs=[msg]
                    )
        
        # Statistics footer
        gr.HTML("""
            <div style="text-align: center; padding: 1rem; color: rgba(255, 255, 255, 0.6); font-size: 0.8rem;">
                <p>🔧 Built with LangChain & Gradio | 🧠 Powered by Ollama Llama3 | ⚡ Context-aware search capabilities</p>
            </div>
        """)
        
        # Event handlers
        msg.submit(
            fn=get_agent_response,
            inputs=[msg, chatbot, thinking_toggle],
            outputs=[msg, chatbot]
        )
        
        send_btn.click(
            fn=get_agent_response,
            inputs=[msg, chatbot, thinking_toggle],
            outputs=[msg, chatbot]
        )
        
        clear_btn.click(
            fn=clear_chat,
            outputs=[chatbot, msg]
        )
    
    return interface

def launch_ui(share=False, server_name="127.0.0.1", server_port=7860):
    """Launch the Gradio interface"""
    print("🚀 Starting Context-Aware AI Assistant...")
    print("📋 Features:")
    print("   • Context analysis and judgment")
    print("   • Automatic web search when needed")
    print("   • Relevance checking")
    print("   • Modern, responsive UI")
    print("   • Example questions and status indicators")
    
    interface = create_modern_ui()
    
    interface.launch(
        share=share,
        server_name=server_name,
        server_port=server_port,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    # Install gradio if not present
    try:
        import gradio as gr
    except ImportError:
        print("Installing Gradio...")
        os.system("pip install gradio")
        import gradio as gr
    
    # Launch the interface
    launch_ui(
        share=False,  # Set to True if you want a public link
        server_name="127.0.0.1",
        server_port=7860
    )