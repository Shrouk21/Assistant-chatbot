# ui/ui.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import gradio as gr
import time
from datetime import datetime
from agent.agent_runner import create_context_aware_agent, run_agent_with_query

# Enhanced CSS for Claude/ChatGPT-like styling with sliding sidebar
custom_css = """
/* Global styles */
* {
    box-sizing: border-box;
}

.gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    background: #f8fafc !important;
    min-height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Header */
.header {
    background: white;
    border-bottom: 1px solid #e5e7eb;
    padding: 1rem 2rem;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header h1 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Main layout */
.main-container {
    display: flex;
    height: calc(100vh - 80px);
    position: relative;
}

/* Chat container */
.chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: white;
    transition: margin-right 0.3s ease;
}

.chat-container.sidebar-open {
    margin-right: 320px;
}

/* Chatbot styling */
.chatbot-container {
    flex: 1;
    overflow-y: auto;
    padding: 1rem 2rem;
    background: #f8fafc;
}

.message {
    max-width: 768px;
    margin: 0 auto 1.5rem auto;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}

.message.user {
    flex-direction: row-reverse;
}

.message-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
}

.user .message-avatar {
    background: #10b981;
    color: white;
}

.bot .message-avatar {
    background: #6366f1;
    color: white;
}

.message-content {
    background: white;
    padding: 1rem 1.25rem;
    border-radius: 1rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    max-width: calc(100% - 48px);
    word-wrap: break-word;
}

.user .message-content {
    background: #10b981;
    color: white;
    border-color: #10b981;
}

.thinking {
    opacity: 0.7;
    font-style: italic;
    color: #6b7280;
}

/* Input area */
.input-area {
    border-top: 1px solid #e5e7eb;
    background: white;
    padding: 1rem 2rem;
}

.input-wrapper {
    max-width: 768px;
    margin: 0 auto;
    position: relative;
}

.input-box {
    width: 100% !important;
    min-height: 44px !important;
    padding: 12px 50px 12px 16px !important;
    border: 1px solid #d1d5db !important;
    border-radius: 24px !important;
    font-size: 16px !important;
    line-height: 1.5 !important;
    resize: none !important;
    background: #f9fafb !important;
    transition: all 0.2s ease !important;
}

.input-box:focus {
    outline: none !important;
    border-color: #6366f1 !important;
    background: white !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}

.send-btn {
    position: absolute !important;
    right: 8px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    background: #6366f1 !important;
    border: none !important;
    border-radius: 50% !important;
    width: 32px !important;
    height: 32px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: background 0.2s ease !important;
    color: white !important;
    font-size: 16px !important;
}

.send-btn:hover:not(:disabled) {
    background: #4f46e5 !important;
}

.send-btn:disabled {
    background: #9ca3af !important;
    cursor: not-allowed !important;
}

/* Sidebar */
.sidebar {
    position: fixed;
    right: -320px;
    top: 80px;
    width: 320px;
    height: calc(100vh - 80px);
    background: white;
    border-left: 1px solid #e5e7eb;
    transition: right 0.3s ease;
    z-index: 50;
    overflow-y: auto;
    box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar.open {
    right: 0;
}

.sidebar-content {
    padding: 1.5rem;
}

.sidebar-toggle {
    position: fixed !important;
    right: 1rem !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    background: #6366f1 !important;
    border: none !important;
    border-radius: 50% !important;
    width: 48px !important;
    height: 48px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    color: white !important;
    font-size: 20px !important;
    z-index: 60 !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
}

.sidebar-toggle:hover {
    background: #4f46e5 !important;
    transform: translateY(-50%) scale(1.05) !important;
}

/* Controls */
.control-group {
    margin-bottom: 1.5rem;
}

.control-group h3 {
    margin: 0 0 0.75rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #1f2937;
}

.example-btn {
    width: 100% !important;
    margin-bottom: 0.5rem !important;
    padding: 0.75rem !important;
    background: #f3f4f6 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    text-align: left !important;
    font-size: 0.875rem !important;
    color: #374151 !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

.example-btn:hover {
    background: #e5e7eb !important;
    border-color: #9ca3af !important;
}

.clear-btn {
    width: 100% !important;
    padding: 0.75rem !important;
    background: #ef4444 !important;
    border: none !important;
    border-radius: 8px !important;
    color: white !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: background 0.2s ease !important;
}

.clear-btn:hover {
    background: #dc2626 !important;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 6px;
    font-size: 0.875rem;
    color: #166534;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #22c55e;
}

/* Responsive design */
@media (max-width: 768px) {
    .header {
        padding: 1rem;
    }
    
    .chatbot-container, .input-area {
        padding: 1rem;
    }
    
    .sidebar {
        width: 280px;
        right: -280px;
    }
    
    .chat-container.sidebar-open {
        margin-right: 280px;
    }
    
    .sidebar-toggle {
        right: 0.5rem !important;
        width: 40px !important;
        height: 40px !important;
        font-size: 18px !important;
    }
}

/* Hide default Gradio elements */
.gradio-container .contain { gap: 0 !important; }
.gradio-container .panel { border: none !important; }
footer { display: none !important; }
"""

# Global agent instance
agent_executor = None

def initialize_agent():
    """Initialize the agent on startup"""
    global agent_executor
    try:
        agent_executor = create_context_aware_agent()
        return "✅ Agent Ready"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_agent_response(message, history, show_thinking=False):
    """Get response from the context-aware agent with proper error handling"""
    global agent_executor
    
    if not message or not message.strip():
        return history, ""
    
    if not agent_executor:
        try:
            agent_executor = create_context_aware_agent()
        except Exception as e:
            history.append([message, f"❌ Failed to initialize agent: {str(e)}"])
            return history, ""
    
    # Add user message to history immediately
    history.append([message, None])
    
    try:
        # Show thinking indicator if enabled
        if show_thinking:
            history[-1][1] = "🤔 Analyzing your question and searching for context..."
        
        # Get agent response
        start_time = time.time()
        
        # Use the agent executor directly
        response = agent_executor.invoke({"input": message})
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Extract the response
        if isinstance(response, dict):
            bot_response = response.get("output", str(response))
        else:
            bot_response = str(response)
        
        # Add response time info
        bot_response += f"\n\n*⏱️ Response time: {response_time:.2f}s*"
        
        # Update history with final response
        history[-1][1] = bot_response
        
    except Exception as e:
        error_msg = f"❌ Sorry, I encountered an error: {str(e)}"
        history[-1][1] = error_msg
        print(f"Agent error: {e}")  # For debugging
    
    return history, ""

def clear_chat():
    """Clear the chat history"""
    return [], ""

def toggle_sidebar():
    """Toggle sidebar visibility"""
    return gr.update(), gr.update()

def load_example(example_text):
    """Load an example question"""
    return example_text

def create_enhanced_ui():
    """Create the enhanced Gradio interface"""
    
    # Initialize agent
    init_status = initialize_agent()
    
    with gr.Blocks(
        css=custom_css,
        title="🤖 AI Assistant",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray",
            neutral_hue="slate"
        )
    ) as interface:
        
        # State for sidebar
        sidebar_open = gr.State(False)
        
        # Header
        gr.HTML("""
            <div class="header">
                <h1>🤖 AI Assistant</h1>
            </div>
        """)
        
        with gr.Row(elem_classes=["main-container"]):
            # Main chat area
            with gr.Column(elem_classes=["chat-container"], scale=1):
                
                # Chatbot
                chatbot = gr.Chatbot(
                    [],
                    elem_id="chatbot",
                    show_label=False,
                    avatar_images=["👤", "🤖"],
                    height=600,
                    show_copy_button=True,
                    bubble_full_width=False,
                    layout="panel"
                )
                
                # Input area
                with gr.Row(elem_classes=["input-area"]):
                    with gr.Column(elem_classes=["input-wrapper"]):
                        with gr.Row():
                            msg_input = gr.Textbox(
                                placeholder="Ask me anything...",
                                show_label=False,
                                scale=10,
                                lines=1,
                                max_lines=5,
                                elem_classes=["input-box"],
                                container=False
                            )
                            
                            send_btn = gr.Button(
                                "➤",
                                scale=1,
                                elem_classes=["send-btn"],
                                size="sm"
                            )
        
        # Sidebar toggle button
        sidebar_toggle_btn = gr.Button(
            "☰",
            elem_classes=["sidebar-toggle"],
            visible=True
        )
        
        # Sidebar (initially hidden)
        with gr.Column(elem_classes=["sidebar"], visible=False) as sidebar:
            with gr.Column(elem_classes=["sidebar-content"]):
                
                # Status
                gr.HTML(f"""
                    <div class="control-group">
                        <h3>Status</h3>
                        <div class="status-badge">
                            <div class="status-dot"></div>
                            {init_status}
                        </div>
                    </div>
                """)
                
                # Settings
                with gr.Group():
                    gr.HTML("<h3>Settings</h3>")
                    show_thinking = gr.Checkbox(
                        label="Show thinking process",
                        value=True,
                        elem_classes=["setting-checkbox"]
                    )
                
                # Example questions
                gr.HTML("<h3>Example Questions</h3>")
                
                examples = [
                    "What is machine learning?",
                    "How do neural networks work?",
                    "Explain transformers in AI",
                    "What is the latest in AI research?",
                    "How does reinforcement learning work?"
                ]
                
                example_buttons = []
                for example in examples:
                    btn = gr.Button(
                        example,
                        elem_classes=["example-btn"],
                        size="sm"
                    )
                    example_buttons.append(btn)
                    btn.click(
                        fn=lambda ex=example: ex,
                        outputs=msg_input
                    )
                
                # Clear chat button
                clear_btn = gr.Button(
                    "🗑️ Clear Chat",
                    elem_classes=["clear-btn"]
                )
        
        # Event handlers
        def handle_message_submit(message, history, thinking):
            return get_agent_response(message, history, thinking)
        
        def handle_sidebar_toggle(is_open):
            return gr.update(visible=not is_open), not is_open
        
        # Message submission
        msg_input.submit(
            fn=handle_message_submit,
            inputs=[msg_input, chatbot, show_thinking],
            outputs=[chatbot, msg_input],
            queue=True
        )
        
        send_btn.click(
            fn=handle_message_submit,
            inputs=[msg_input, chatbot, show_thinking],
            outputs=[chatbot, msg_input],
            queue=True
        )
        
        # Sidebar toggle
        sidebar_toggle_btn.click(
            fn=handle_sidebar_toggle,
            inputs=[sidebar_open],
            outputs=[sidebar, sidebar_open]
        )
        
        # Clear chat
        clear_btn.click(
            fn=clear_chat,
            outputs=[chatbot, msg_input]
        )
    
    return interface

def launch_ui(share=False, server_name="127.0.0.1", server_port=7860):
    """Launch the enhanced Gradio interface"""
    print("🚀 Starting Enhanced AI Assistant...")
    print("✨ Features:")
    print("   • Claude/ChatGPT-like interface")
    print("   • Sliding sidebar (toggle with ☰ button)")
    print("   • Context-aware responses")
    print("   • Modern, clean design")
    print("   • Responsive layout")
    
    interface = create_enhanced_ui()
    
    interface.queue(default_concurrency_limit=10).launch(
        share=share,
        server_name=server_name,
        server_port=server_port,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    try:
        import gradio as gr
    except ImportError:
        print("Installing Gradio...")
        os.system("pip install gradio")
        import gradio as gr
    
    # Launch the interface
    launch_ui(
        share=True, #to open it in colab
        server_name="127.0.0.1",
        server_port=7860
    )