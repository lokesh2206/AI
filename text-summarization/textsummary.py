import torch
import gradio as gr

from transformers import pipeline
model_path = "../Models/models--sshleifer--distilbart-cnn-12-6/snapshots/a4f8f3ea906ed274767e9906dbaede7531d660ff"
text_summary = pipeline("summarization",model="sshleifer/distilbart-cnn-12-6")

def summary(input):
    output = text_summary(input)
    return output[0]['summary_text']

gr.close_all()
demo =gr.Interface(fn=summary,inputs="text",outputs="text", title="Text Summarizer")
demo.launch()

