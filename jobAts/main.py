import requests
from bs4 import BeautifulSoup
import gradio as gr
import fitz
from openai import OpenAI
from markdown_pdf import MarkdownPdf, Section
import os
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

def extract_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def get_id_description(job_url):
    try:
        response = requests.get(job_url)
        soup = BeautifulSoup(response.content,'html.parser')

        for script in soup(["script","style","nav","footer"]):
            script.decompose()
        text = soup.get_text(separator=" ")
        return " ".join(text.split())
    except Exception as e:
        return f"Exception occured: {str(e)}"

def taylor_resume(jd_text):
    jd_text_refine = get_id_description(jd_text)
    cv_text = extract_from_pdf("CV.pdf")

    prompt= f"""
    You are an expert Resume Writer and Applicant Tracking System Optimization Specialist.
    JOB DESCRIPTION (JD):
    {jd_text_refine}
    MY MASTER RESUME:
    {cv_text}
    TASK:
    Rewrite my resume to perfectly match the Job Description.
    RULES:
    1. Use the EXACT keywords from the JD in skills and summary sections.
    2. Rephrase bullet points to match the responsibilities and metrics they care about.
    3. Do NOT lie or invent new experience.
    4. Only use real experience from my resume.
    5. Output in clean, well-formatted MARKDOWN.
    """
    response = client.responses.create(
            model = "gpt-4.1-nano",
        input = prompt
    )
    markdown_text = response.output_text
    output_file = "tailored_cv.pdf"
    pdf = MarkdownPdf(toc_level=0)

    css_style = """
    body { font-family: 'Helvetica', sans-serif; font-size: 12px; line-height: 1.4; color: #333; }
    h1 { font-size: 24px; border-bottom: 2px solid #333; margin-bottom: 10px; text-transform: uppercase; }
    h2 { font-size: 16px; border-bottom: 1px solid #ccc; margin-top: 20px; text-transform: uppercase; color: #555; }
    ul { padding-left: 20px; }
    li { margin-bottom: 5px; }
    strong { color: #000; }
    """

    pdf.add_section(Section(markdown_text), user_css=css_style)
    pdf.save(output_file)

def rate_match(job_description, resume_text):
    prompt = f"""
    You are an expert resume writer and Applicant  Tracking System specialist.
    You re given a job description and a resume below.
    Job Description:
    {job_description}
    Resume: 
    {resume_text}
    TASK:
    Compare the key words in job description to the key words in the resume.
    Come up with a matching score between 1 and 100. 1 is the least match and 100 is the most match.
    RULES:
    1. Do NOT come up with a score below 1 or above 100.
    2. Do NOT give any other output other than just a single score.
    """
    response = client.responses.create(
        model = "gpt-5-nano",
        input = prompt
    )
    return response

gr.close_all()

# demo = gr.Interface(fn=summary, inputs="text",outputs="text")
demo = gr.Interface(fn=taylor_resume,
                    inputs=[gr.Textbox(label="ATS Supported Resume",lines=1)],
                    outputs=[gr.Textbox(label="Get text",lines=4)],
                    title="Input Job Url",
                    description="")
demo.launch()