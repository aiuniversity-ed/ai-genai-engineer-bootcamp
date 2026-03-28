
# Run: python gradio_demo.py

import gradio as gr
from PIL import Image

# DEMO 1 — Simple Interface (text in → text out)

def greet(name: str, intensity: int) -> str:
    """Simple function: takes name + intensity, returns greeting."""
    return "Hello, " + name + "!" * intensity

demo_simple = gr.Interface(
    fn=greet,
    inputs=[
        gr.Textbox(label="Your Name", placeholder="e.g. Priya"),
        gr.Slider(1, 10, value=3, step=1, label="Exclamation Intensity"),
    ],
    outputs=gr.Textbox(label="Greeting"),
    title="🙋 Simple Greeter",
    description="Type a name and choose intensity — your first Gradio app!",
    examples=[["Alice", 5], ["Bob", 1], ["Priya", 8]],   # clickable examples
)


# DEMO 2 — Image Input / Output

def grayscale(img):
    """Convert uploaded image to grayscale."""
    return img.convert("L")

demo_image = gr.Interface(
    fn=grayscale,
    inputs=gr.Image(type="pil", label="Upload Image"),
    outputs=gr.Image(label="Grayscale Output"),
    title="🖼️ Image Grayscaler",
    description="Upload any image and get a grayscale version instantly.",
)

# DEMO 3 — Gradio Blocks (flexible layout like Streamlit)

def analyse_text(text: str) -> tuple:
    """Return word count and character count."""
    word_count = len(text.split())
    char_count = len(text)
    unique_words = len(set(text.lower().split()))
    summary = (
        f"📝 Word Count   : {word_count}\n"
        f"🔤 Characters   : {char_count}\n"
        f"🔑 Unique Words : {unique_words}"
    )
    return summary, word_count

with gr.Blocks(title="AI Bootcamp — Blocks Demo") as demo_blocks:
    gr.Markdown("## 🤖 AI Bootcamp — Gradio Blocks Demo")
    gr.Markdown("A flexible layout using `gr.Blocks` — similar to Streamlit columns.")

    with gr.Row():
        with gr.Column():
            text_in = gr.Textbox(label="Input Text", lines=5,
                                  placeholder="Paste any text here…")
            btn     = gr.Button("Analyse", variant="primary")
        with gr.Column():
            text_out    = gr.Textbox(label="Analysis Result", lines=5)
            word_count  = gr.Number(label="Word Count")

    btn.click(fn=analyse_text, inputs=text_in, outputs=[text_out, word_count])

    gr.Markdown("---")
    gr.Markdown("### 💡 Key Gradio Blocks Components")
    gr.Markdown("""
    | Component | Purpose |
    |-----------|---------|
    | `gr.Row()` | Horizontal layout |
    | `gr.Column()` | Vertical layout inside a row |
    | `gr.Markdown()` | Text / headings |
    | `btn.click()` | Wire button to function |
    """)


# DEMO 4 — ChatInterface (easiest chatbot UI)

def echo_bot(message: str, history: list) -> str:
    """
    history = list of [user_msg, bot_msg] pairs — Gradio manages it automatically.
    Replace this function body with a real LLM call in Section 17 Part 2.
    """
    word_count = len(message.split())
    return f"You said ({word_count} words): {message}"

demo_chat = gr.ChatInterface(
    fn=echo_bot,
    title="💬 Echo Chatbot",
    description="A simple echo bot. Replace `echo_bot()` with an LLM call in the next lecture.",
    examples=["Tell me a joke", "What is RAG?", "Explain transformers simply"],
)


# LAUNCH — uncomment the demo you want to run

if __name__ == "__main__":

    print("""
    ╔══════════════════════════════════════╗
    ║   Gradio Demo — Section 17           ║
    ║   Choose which demo to launch:       ║
    ║   1 → Simple Interface               ║
    ║   2 → Image Grayscaler               ║
    ║   3 → Blocks Layout                  ║
    ║   4 → ChatInterface  (default)       ║
    ╚══════════════════════════════════════╝
    """)

    choice = input("Enter demo number (1/2/3/4) [default=4]: ").strip() or "4"

    demos = {
        "1": demo_simple,
        "2": demo_image,
        "3": demo_blocks,
        "4": demo_chat,
    }

    selected = demos.get(choice, demo_chat)

    selected.launch(
        share=False,     # set share=True to get a public URL (useful for HuggingFace Spaces)
        show_error=True,
    )
