# ui/ui.py
import sys, os, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import gradio as gr
from agent.agent_runner import create_context_aware_agent

# --- Neater CSS ---
custom_css = """
.gradio-container { font-family:'Inter',sans-serif !important;background:#f9fafb !important;min-height:100vh !important;}
.header {background:white;border-bottom:1px solid #e5e7eb;padding:0.75rem 1.5rem;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100;}
.header h1 {font-size:1.25rem;font-weight:600;color:#111827;margin:0;}
.sidebar-toggle {background:#6366f1 !important;border-radius:8px !important;width:40px !important;height:40px !important;font-size:18px !important;color:white !important;display:flex;align-items:center;justify-content:center;cursor:pointer;}
.sidebar-toggle:hover {background:#4f46e5 !important;}
.chatbot-container {padding:1rem 1.5rem;background:#f9fafb;}
.message {max-width:680px;margin:0 auto 1rem auto;display:flex;gap:0.75rem;}
.message-avatar {width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1rem;}
.user .message-avatar {background:#3b82f6;color:white;}
.bot .message-avatar {background:#6366f1;color:white;}
.message-content {padding:0.75rem 1rem;border-radius:12px;border:1px solid #e5e7eb;background:white;font-size:0.95rem;line-height:1.4;}
.user .message-content {background:#3b82f6;color:white;border:none;}
.input-area {border-top:1px solid #e5e7eb;background:white;padding:0.75rem 1.5rem;}
.input-wrapper {max-width:680px;margin:0 auto;display:flex;gap:0.5rem;width:100%;}
.input-box {flex:1;border:1px solid #d1d5db !important;border-radius:20px !important;padding:0.6rem 1rem !important;font-size:0.95rem !important;background:#f9fafb !important;}
.input-box:focus {border-color:#6366f1 !important;background:white !important;box-shadow:0 0 0 2px rgba(99,102,241,0.15) !important;}
.send-btn {background:#6366f1 !important;border-radius:50% !important;width:36px !important;height:36px !important;display:flex !important;align-items:center !important;justify-content:center !important;color:white !important;}
.send-btn:hover {background:#4f46e5 !important;}
.sidebar {position:fixed;right:-300px;top:60px;width:300px;height:calc(100vh - 60px);background:white;border-left:1px solid #e5e7eb;transition:right 0.3s ease;overflow-y:auto;box-shadow:-2px 0 6px rgba(0,0,0,0.05);z-index:200;}
.sidebar.open {right:0;}
.sidebar-content {padding:1rem;}
.example-btn {width:100% !important;margin-bottom:0.5rem !important;padding:0.5rem 0.75rem !important;background:#f3f4f6 !important;border:1px solid #d1d5db !important;border-radius:8px !important;font-size:0.9rem !important;text-align:left;}
.example-btn:hover {background:#e5e7eb !important;}
.clear-btn {background:#ef4444 !important;border-radius:8px !important;padding:0.5rem !important;color:white !important;font-weight:500 !important;width:100%;}
"""

# --- Agent setup ---
agent_executor = None
def initialize_agent():
    global agent_executor
    try:
        agent_executor = create_context_aware_agent()
        return "✅ Agent Ready"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_agent_response(message, history, show_thinking=False):
    global agent_executor
    if not message.strip(): return history, ""
    if not agent_executor:
        try: agent_executor = create_context_aware_agent()
        except Exception as e:
            history.append([message, f"❌ Failed to init agent: {str(e)}"]); return history, ""
    history.append([message, None])
    try:
        if show_thinking: history[-1][1] = "🤔 Thinking..."
        start = time.time()
        response = agent_executor.invoke({"input": message})
        elapsed = time.time()-start
        bot_response = response.get("output") if isinstance(response,dict) else str(response)
        bot_response += f"\n\n⏱️ {elapsed:.2f}s"
        history[-1][1] = bot_response
    except Exception as e:
        history[-1][1] = f"❌ Error: {e}"
    return history, ""

def clear_chat(): return [], ""

# --- UI ---
def create_enhanced_ui():
    init_status = initialize_agent()
    with gr.Blocks(css=custom_css, title="🤖 AI Assistant") as ui:
        sidebar_open = gr.State(False)

        # Header
        with gr.Row(elem_classes=["header"]):
            gr.HTML("<h1>🤖 AI Assistant</h1>")
            sidebar_toggle_btn = gr.Button("☰", elem_classes=["sidebar-toggle"])

        # Chat
        chatbot = gr.Chatbot([], height=600, bubble_full_width=False, avatar_images=["👤","🤖"])
        with gr.Row(elem_classes=["input-area"]):
            with gr.Column(elem_classes=["input-wrapper"]):
                msg_input = gr.Textbox(placeholder="Ask me anything...", lines=1, max_lines=5, container=False, elem_classes=["input-box"])
                send_btn = gr.Button("➤", elem_classes=["send-btn"], scale=0)

        # Sidebar overlay
        with gr.Column(elem_classes=["sidebar"], visible=False) as sidebar:
            with gr.Column(elem_classes=["sidebar-content"]):
                gr.HTML(f"<h3>Status</h3><div>{init_status}</div>")
                show_thinking = gr.Checkbox(label="Show thinking process", value=True)
                gr.HTML("<h3>Examples</h3>")
                for ex in ["What is machine learning?","How do neural networks work?","Explain transformers","Latest in AI research?"]:
                    gr.Button(ex, elem_classes=["example-btn"]).click(fn=lambda x=ex: x, outputs=msg_input)
                gr.Button("🗑️ Clear Chat", elem_classes=["clear-btn"]).click(fn=clear_chat, outputs=[chatbot,msg_input])

        # Events
        def submit(message,history,thinking): return get_agent_response(message,history,thinking)
        msg_input.submit(submit,[msg_input,chatbot,show_thinking],[chatbot,msg_input])
        send_btn.click(submit,[msg_input,chatbot,show_thinking],[chatbot,msg_input])

        def toggle(opened): return gr.update(visible=not opened), not opened
        sidebar_toggle_btn.click(toggle,[sidebar_open],[sidebar,sidebar_open])

    return ui

def launch_ui(share=False, server_name="127.0.0.1", server_port=7860):
    ui = create_enhanced_ui()
    ui.queue().launch(share=share, server_name=server_name, server_port=server_port)

if __name__=="__main__":
    launch_ui(share=True, server_name="127.0.0.1", server_port=7860)
