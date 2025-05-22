import gradio as gr
from chatbot_logic import handle_user_message, set_tts

def chat_interface(user_input, chat_history, voice_enabled):
    set_tts(voice_enabled)
    bot_response, updated_history = handle_user_message(user_input, chat_history)
    return updated_history, updated_history

with gr.Blocks() as demo:
    gr.Markdown("## 🧠 Smart Medical Chatbot with Voice")
    chatbot = gr.Chatbot(label="Virtual Health Assistant")
    msg = gr.Textbox(placeholder="Type here and press Enter...", label="Your input")
    state = gr.State([])
    tts_toggle = gr.Checkbox(label="🔈 Enable Voice", value=True)

    msg.submit(chat_interface, [msg, state, tts_toggle], [chatbot, state])
    msg.submit(lambda: "", None, msg)  # Clear input after submission

demo.launch()
