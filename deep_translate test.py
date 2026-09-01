# Import necessary libraries
from deep_translator import GoogleTranslator, MyMemoryTranslator
import gradio as gr
import pandas as pd
import string
import html
#from openpyxl import load_workbook as ld_book

# save excel path so its easier to call
csv_sw_path = r"C:\Users\abe\Documents\GitHub\KiswahiliTranslator\kamusi\words.csv"
csv_en_path = r"C:\Users\abe\Documents\GitHub\KiswahiliTranslator\kamusi\english.csv"

# big thanks to all the wonderful people on github this is super fun, I'll have to find an english dictionary but this is a good start!
# Open and read the excel file
dsw = pd.read_csv(csv_sw_path, header=None)  # for swahili dictionary
den = pd.read_csv(csv_en_path, header=None)  # for english

# Convert to Python dictionary and force keys to lowercase for safe matching
dict_sw = dict(zip(dsw[0].astype(str).str.lower(), dsw[1]))
dict_en = dict(zip(den[0].astype(str).str.lower(), den[1]))


def clean_word(text):
    """Standardise a word: strip punctuation, lowercase."""
    return text.strip(string.punctuation).lower()


def translate(text):
    # big ups to google AI for this helpful bit
    clean_text = clean_word(text)

    if not clean_text:
        return ""

    # Look up in Swahili dictionary first
    definition = dict_sw.get(clean_text)

    if definition is None:
        # Try the English dictionary next
        definition = dict_en.get(clean_text)

        if definition is None:
            try:
                # Use translation fallback
                definition = GoogleTranslator(source='swahili', target='english').translate(clean_text)

                # Update local dictionary variable
                dict_en[clean_text] = definition

                # FIX: Correctly structure dictionary to save as a 2-column CSV
                df = pd.DataFrame(list(dict_en.items()))
                df.to_csv(csv_en_path, index=False, header=False)
                print(f"Saved new translation for: {clean_text}")
            except Exception as e:
                print(f"Error during API translation/saving: {e}")
                definition = "No Definition Found"

    return definition


def generate_hoverable_text(input_text):
    """Parses text and wraps matched words in a hover-tooltip span. Each
    span carries data-word so the click-handling JS (see js_on_load below)
    knows which word to look up when clicked."""
    words = input_text.split(" ")
    html_output = []

    for word in words:
        definition = translate(word)
        word_key = clean_word(word)

        # Escape values so quotes/special chars in words or definitions
        # don't break the HTML attributes.
        safe_definition = html.escape(str(definition), quote=True)
        safe_word_key = html.escape(word_key, quote=True)

        hover_html = (
            f'<span class="tooltip-target" '
            f'data-tooltip="{safe_definition}" '
            f'data-word="{safe_word_key}">{word}</span>'
        )
        html_output.append(hover_html)

    return " ".join(html_output)


# ---------------------------------------------------------------------
# server_functions: plain Python functions that the JS inside the HTML
# widget (see js_on_load below) can call directly via `await server.xxx()`.
# This is what actually lets a click inside the rendered HTML reach back
# into Python — no hidden textboxes or global click listeners required.
# ---------------------------------------------------------------------

def get_word_definition(word):
    """Called when a word is clicked. Returns its definition as a string."""
    return str(translate(word))


def save_word_definition(word, new_definition):
    """Called when 'Save to Dictionary' is clicked in the panel. Writes the
    edited definition back to whichever CSV the word already belongs to
    (defaults to the English dictionary for brand-new words)."""
    if not word:
        return "No word selected."

    key = clean_word(word)

    if key in dict_sw:
        dict_sw[key] = new_definition
        df = pd.DataFrame(list(dict_sw.items()))
        df.to_csv(csv_sw_path, index=False, header=False)
    else:
        dict_en[key] = new_definition
        df = pd.DataFrame(list(dict_en.items()))
        df.to_csv(csv_en_path, index=False, header=False)

    return f"Saved definition for '{key}'"


# The whole reading area + side panel lives in ONE html_template so the
# click handling never has to cross a component boundary.
reading_html_template = """
<div class="tooltip-container">
    <div class="reading-text">${value}</div>
    <div class="side-panel">
        <h4>Word Details</h4>
        <div class="panel-word"></div>
        <textarea class="panel-definition" rows="3"></textarea>
        <button class="save-btn">Save to Dictionary</button>
        <div class="save-status"></div>
    </div>
</div>
"""

# Scoped CSS for this component only (won't leak out, won't be blocked
# from reaching in — it's compiled specifically for this template).
reading_css_template = """
.tooltip-container {
    font-size: 16px;
    line-height: 1.6;
    display: flex;
    gap: 24px;
    align-items: flex-start;
}
.reading-text {
    flex: 3;
}
.tooltip-target {
    color: #00A3DD;
    cursor: pointer;
    position: relative;
    display: inline-block;
}
.tooltip-target::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    background-color: #333;
    color: #fff;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 14px;
    white-space: normal;
    width: 220px;
    z-index: 100;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s ease-in-out;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.25);
}
.tooltip-target:hover::after {
    opacity: 1;
}
.tooltip-target:hover {
    color: #ebf2ec;
}
.side-panel {
    flex: 1;
    display: none;
    border-left: 2px solid #eee;
    padding-left: 16px;
    min-width: 200px;
}
.side-panel.open {
    display: block;
}
.panel-word {
    font-weight: bold;
    margin-bottom: 8px;
}
.panel-definition {
    width: 100%;
    box-sizing: border-box;
    margin-bottom: 8px;
}
.save-btn {
    background-color: #1EB53A;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
}
.save-btn:hover {
    background-color: #1b9e33;
}
.save-status {
    margin-top: 8px;
    font-size: 13px;
    color: #1b9e33;
}
"""

# Runs once when this widget mounts. `element` is this component's own
# root node, so element.addEventListener + event delegation keeps working
# even after ${value} changes and the inner HTML gets re-rendered (the
# translate button reruns generate_hoverable_text and pushes it into
# `value`, which replaces the .reading-text / .side-panel markup, but
# `element` itself is never destroyed, so this listener survives it).
reading_js_on_load = """
element.addEventListener('click', async (e) => {
    const wordSpan = e.target.closest('.tooltip-target');
    if (wordSpan) {
        const word = wordSpan.getAttribute('data-word');
        const definition = await server.get_word_definition(word);

        const panel = element.querySelector('.side-panel');
        const panelWord = element.querySelector('.panel-word');
        const panelDef = element.querySelector('.panel-definition');
        const status = element.querySelector('.save-status');

        panel.dataset.currentWord = word;
        panelWord.textContent = word;
        panelDef.value = definition;
        status.textContent = '';
        panel.classList.add('open');
        return;
    }

    const saveBtn = e.target.closest('.save-btn');
    if (saveBtn) {
        const panel = element.querySelector('.side-panel');
        const panelDef = element.querySelector('.panel-definition');
        const status = element.querySelector('.save-status');
        const word = panel.dataset.currentWord;
        if (!word) return;
        const message = await server.save_word_definition(word, panelDef.value);
        status.textContent = message;
    }
});
"""

# CSS for the plain Gradio-level "Translate Text" button (this one lives
# outside the HTML widget, in normal Gradio Blocks layout, so the regular
# demo.launch(css=...) mechanism is fine for it).
custom_css = """
#green_btn {
    background-color: #1EB53A !important;
    color: white !important;
}
#green_btn:hover {
    background-color: #1b9e33 !important;
}
"""

# 3. Build the Gradio App
with gr.Blocks() as demo:
    gr.Markdown("### Kiswahili Reading Buddy")
    gr.Markdown("Write any Kiswahili text — hover a word for a quick translation, or click it to open details and edit the dictionary.")

    user_input = gr.Textbox(
        label="Enter Text",
        value="Andika Kiswahili hapa"
    )

    reading_widget = gr.HTML(
        value="",
        html_template=reading_html_template,
        css_template=reading_css_template,
        js_on_load=reading_js_on_load,
        server_functions=[get_word_definition, save_word_definition],
    )

    generate_button = gr.Button("Translate Text", elem_id="green_btn")
    generate_button.click(fn=generate_hoverable_text, inputs=user_input, outputs=reading_widget)

demo.launch(css=custom_css)