import streamlit as st
import re
import openai
import PyPDF2

# OpenAI API Key Setup
openai.api_key = "YOUR_OPENAI_API_KEY"

# Function to Extract Text from PDF
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() if page.extract_text() else ""
    return text

# JD Parsing Logic
def extract_key_points(jd_text):
    skills_pattern = r"experience in ([\w\s,]+)"
    role_pattern = r"The role involves ([\w\s,]+)"
    tools_pattern = r"Experience in ([\w\s,]+) is required"

    skills = re.findall(skills_pattern, jd_text)
    roles = re.findall(role_pattern, jd_text)
    tools = re.findall(tools_pattern, jd_text)

    parsed_data = {
        "Skills": skills[0].split(", ") if skills else [],
        "Roles": roles[0].split(", ") if roles else [],
        "Tools": tools[0].split(", ") if tools else []
    }

    return parsed_data

# GPT Prompt for Resume Point Generation
def generate_resume_points(parsed_data, experience_summary):
    prompt = (
        f"Based on my experience: {experience_summary}\n\n"
        f"Generate 3 impactful resume points emphasizing leadership in business strategy, P&L ownership, and stakeholder management."
        f" Focus on measurable outcomes such as revenue growth, cost optimization, and operational efficiency."
        f" Highlight expertise in {', '.join(parsed_data['Skills'])} skills, my role as {', '.join(parsed_data['Roles'])}, and the tools {', '.join(parsed_data['Tools'])}."
        f" Include industry-relevant language that resonates with decision-makers in mid-senior management roles."
    )

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a professional resume expert."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=300
)

    return response['choices'][0]['text'].strip()

# GPT Prompt for Cover Letter Generation
def generate_cover_letter(parsed_data, experience_summary):
    prompt = (
        f"Based on my experience: {experience_summary}\n\n"
        f"Generate a professional cover letter highlighting my expertise in {', '.join(parsed_data['Skills'])}."
        f" Emphasize leadership, business strategy, and measurable outcomes for a mid-senior management role."
    )

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300
    )

    return response['choices'][0]['text'].strip()

# GPT Prompt for Skills Gap Analysis
def generate_skills_gap_analysis(parsed_data, user_skills):
    missing_skills = set(parsed_data['Skills']) - set(user_skills)
    if missing_skills:
        return f"Consider improving these key skills to align better with the JD: {', '.join(missing_skills)}"
    return "You match the required skills well."

# Streamlit UI Design
st.title("AI Resume Assistant")

# PDF Upload Inputs
jd_file = st.file_uploader("Upload JD PDF Here", type="pdf")
exp_file = st.file_uploader("Upload Experience Summary PDF Here", type="pdf")
user_skills = st.text_input("List Your Current Skills (comma separated)").split(", ")

if st.button("Generate Insights"):
    if jd_file and exp_file:
        jd_text = extract_text_from_pdf(jd_file)
        experience_summary = extract_text_from_pdf(exp_file)
        
        jd_parsed = extract_key_points(jd_text)
        resume_points = generate_resume_points(jd_parsed, experience_summary)
        cover_letter = generate_cover_letter(jd_parsed, experience_summary)
        skills_gap = generate_skills_gap_analysis(jd_parsed, user_skills)

        st.subheader("Extracted JD Insights")
        st.json(jd_parsed)

        st.subheader("Generated Resume Points")
        st.write(resume_points)

        st.subheader("Generated Cover Letter")
        st.write(cover_letter)

        st.subheader("Skills Gap Analysis")
        st.write(skills_gap)
    else:
        st.warning("Please upload both the Job Description and Experience Summary PDFs.")
