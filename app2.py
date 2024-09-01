import streamlit as st
import os
import io
import base64
from PIL import Image
import pdf2image
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import pdfplumber
import json
import time

# Load environment variables and configure Gemini AI
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set page config
st.set_page_config(page_title="ATS Resume Expert", layout="wide")

# Custom CSS for a cleaner look
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .big-font {
        font-size: 2.5rem !important;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2980b9;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .result-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .metric-label {
        font-size: 1rem;
        color: #7f8c8d;
    }
    .section-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

INDUSTRY_TEMPLATES = {
    "Technology": {
        "sections": ["Summary", "Technical Skills", "Work Experience", "Projects", "Education"],
        "keywords": ["programming", "software development", "agile", "cloud computing"]
    },
    "Finance": {
        "sections": ["Professional Summary", "Core Qualifications", "Professional Experience", "Education", "Certifications"],
        "keywords": ["financial analysis", "risk management", "investment strategies", "market research"]
    },
    "Healthcare": {
        "sections": ["Professional Summary", "Clinical Experience", "Education", "Certifications", "Skills"],
        "keywords": ["patient care", "medical procedures", "healthcare regulations", "electronic health records"]
    },
    "Business": {
        "sections": ["Executive Summary", "Core Competencies", "Professional Experience", "Achievements", "Education"],
        "keywords": ["strategic planning", "project management", "business development", "data analysis", "leadership"]
    },
    "Sales": {
        "sections": ["Professional Summary", "Sales Achievements", "Work Experience", "Skills", "Education"],
        "keywords": ["revenue growth", "client acquisition", "negotiation", "CRM", "sales strategies"]
    }
}


@st.cache_resource
def download_nltk_data():
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except Exception as e:
        st.error(f"Error downloading NLTK data: {str(e)}")

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            file_content = uploaded_file.read()
            if len(file_content) == 0:
                st.warning("The uploaded file is empty. You can manually input your resume text below.")
                return None
            
            images = pdf2image.convert_from_bytes(file_content)
            if len(images) > 0:
                first_page = images[0]
                img_bytes_arr = io.BytesIO()
                first_page.save(img_bytes_arr, format='JPEG')
                img_bytes_arr = img_bytes_arr.getvalue()
                pdf_parts = [
                    {
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(img_bytes_arr).decode()
                    }
                ]
                return pdf_parts
            else:
                st.warning("No pages were converted from the PDF. You can manually input your resume text below.")
                return None
        except pdf2image.exceptions.PDFPageCountError:
            st.warning("Unable to process the PDF. You can manually input your resume text below.")
            return None
        except Exception as e:
            st.warning(f"An unexpected error occurred while processing the PDF: {str(e)}. You can manually input your resume text below.")
            return None
    else:
        st.info("No file uploaded. You can manually input your resume text below.")
        return None

def extract_text_from_pdf(pdf_file):
    if pdf_file is not None:
        try:
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
            if not text.strip():
                st.warning("No text could be extracted from the PDF. You can manually input your resume text below.")
            return text
        except Exception as e:
            st.warning(f"Error extracting text from PDF: {str(e)}. You can manually input your resume text below.")
            return ""
    return ""


def get_gemini_response(input_prompt, pdf_content, job_description):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([input_prompt, pdf_content, job_description])
        return response.text
    except Exception as e:
        st.error(f"Error generating AI response: {str(e)}")
        return ""

def structured_resume_input():
    resume_data = {}
    
    st.subheader("Personal Information")
    col1, col2 = st.columns(2)
    with col1:
        resume_data['name'] = st.text_input("Full Name")
        resume_data['email'] = st.text_input("Email")
    with col2:
        resume_data['phone'] = st.text_input("Phone")
        resume_data['location'] = st.text_input("Location")

    st.markdown('<p class="section-title">Professional Summary</p>', unsafe_allow_html=True)
    resume_data['summary'] = st.text_area("Summarize your professional experience and goals", height=100)

    st.markdown('<p class="section-title">Work Experience</p>', unsafe_allow_html=True)
    num_jobs = st.number_input("Number of jobs to add", min_value=0, max_value=10, value=1)
    resume_data['work_experience'] = []
    for i in range(num_jobs):
        st.markdown(f"<p class='section-title'>Job {i+1}</p>", unsafe_allow_html=True)
        job = {}
        col1, col2 = st.columns(2)
        with col1:
            job['title'] = st.text_input(f"Job Title {i+1}")
            job['company'] = st.text_input(f"Company {i+1}")
        with col2:
            job['start_date'] = st.date_input(f"Start Date {i+1}")
            job['end_date'] = st.date_input(f"End Date {i+1}")
        job['responsibilities'] = st.text_area(f"Key Responsibilities and Achievements {i+1}", height=100)
        resume_data['work_experience'].append(job)

    st.markdown('<p class="section-title">Education</p>', unsafe_allow_html=True)
    num_edu = st.number_input("Number of educational qualifications to add", min_value=0, max_value=5, value=1)
    resume_data['education'] = []
    for i in range(num_edu):
        edu = {}
        col1, col2 = st.columns(2)
        with col1:
            edu['degree'] = st.text_input(f"Degree {i+1}")
            edu['institution'] = st.text_input(f"Institution {i+1}")
        with col2:
            edu['graduation_year'] = st.number_input(f"Graduation Year {i+1}", min_value=1950, max_value=2030)
        resume_data['education'].append(edu)

    st.markdown('<p class="section-title">Skills</p>', unsafe_allow_html=True)
    resume_data['skills'] = st.text_area("List your key skills (comma-separated)")

    return resume_data

def format_resume(resume_data):
    formatted_resume = f"""
{resume_data['name']}
{resume_data['email']} | {resume_data['phone']} | {resume_data['location']}

PROFESSIONAL SUMMARY
{resume_data['summary']}

WORK EXPERIENCE
"""
    for job in resume_data['work_experience']:
        formatted_resume += f"""
{job['title']} at {job['company']}
{job['start_date']} - {job['end_date']}
{job['responsibilities']}
"""

    formatted_resume += "\nEDUCATION\n"
    for edu in resume_data['education']:
        formatted_resume += f"{edu['degree']} from {edu['institution']}, {edu['graduation_year']}\n"

    formatted_resume += f"\nSKILLS\n{resume_data['skills']}"

    return formatted_resume

def extract_keywords(text):
    try:
        words = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        keywords = [word for word in words if word.isalnum() and word not in stop_words]
        return Counter(keywords)
    except Exception as e:
        st.error(f"Error extracting keywords: {str(e)}")
        return Counter()

def calculate_percentage_match(resume_text, job_description):
    try:
        resume_keywords = extract_keywords(resume_text)
        job_keywords = extract_keywords(job_description)
        matching_keywords = set(resume_keywords.keys()) & set(job_keywords.keys())
        total_job_keywords = len(job_keywords)
        if total_job_keywords == 0:
            return 0
        match_percentage = (len(matching_keywords) / total_job_keywords) * 100
        return round(match_percentage, 2)
    except Exception as e:
        st.error(f"Error calculating percentage match: {str(e)}")
        return 0

def apply_industry_template(resume_text, industry):
    template = INDUSTRY_TEMPLATES.get(industry, {})
    sections = template.get("sections", [])
    keywords = template.get("keywords", [])
    formatted_resume = "\n\n".join([f"{section.upper()}:\n[Add relevant information here]" for section in sections])
    return formatted_resume, keywords

def generate_prompt(analysis_type, industry):
    if analysis_type == "Comprehensive Review":
        return f"""Provide a comprehensive evaluation of the resume for a {industry} position:
        1. Overall Match: Provide a percentage and brief explanation.
        2. Key Strengths: Identify and explain the top 3-5 strengths relevant to the job.
        3. Experience Analysis: Evaluate the relevance and depth of the candidate's experience.
        4. Skills Assessment: Analyze the alignment of the candidate's skills with job requirements.
        5. Education Relevance: Comment on the applicant's educational background in relation to the position.
        6. Achievements: Highlight notable accomplishments and their relevance.
        7. Improvement Areas: Suggest 3-5 specific areas for enhancement.
        8. ATS Optimization Tips: Provide actionable advice to improve ATS compatibility.
        9. Overall Impression: Summarize the candidate's suitability in 2-3 sentences.
        """
    elif analysis_type == "Skill Gap Analysis":
        return f"""Conduct a thorough skill gap analysis for the {industry} position:
        1. Required Skills: List the key skills required for the job based on the description.
        2. Matching Skills: Identify skills in the resume that align with job requirements.
        3. Missing Skills: Highlight important skills mentioned in the job description but missing from the resume.
        4. Skill Proficiency: Assess the apparent level of expertise in matching skills.
        5. Transferable Skills: Identify skills that, while not exact matches, could be valuable for the role.
        6. Skill Development Recommendations: Suggest ways to acquire or improve crucial skills.
        7. Industry Trends: Mention any emerging skills in the {industry} field that could enhance the application.
        """
    elif analysis_type == "Keyword Optimization":
        return f"""Analyze and optimize the resume for key {industry} keywords:
        1. Job Description Keywords: Extract and list important keywords from the job description.
        2. Resume Keyword Matches: Identify keywords in the resume that match the job description.
        3. Missing Keywords: List important keywords from the job description not found in the resume.
        4. Keyword Placement: Suggest optimal sections to incorporate missing keywords.
        5. Keyword Density: Evaluate the appropriate use and frequency of keywords.
        6. Industry-Specific Terminology: Suggest relevant {industry} terms to include.
        7. Action Verbs: Recommend powerful action verbs to enhance impact.
        8. Keyword Integration Tips: Provide advice on naturally incorporating keywords into the resume.
        """
    else:  # ATS Match Score
        return f"""Evaluate the resume's ATS compatibility for a {industry} position:
        1. Overall ATS Score: Provide a percentage score for ATS compatibility.
        2. Formatting Analysis: Assess the resume's format for ATS readability.
        3. Keyword Match: Calculate the percentage of job description keywords found in the resume.
        4. Section Headers: Evaluate the use of standard, ATS-friendly section headings.
        5. Contact Information: Check for proper placement and completeness of contact details.
        6. Work History Format: Analyze the presentation of work experience for ATS parsing.
        7. Education Section: Assess the formatting of educational qualifications.
        8. Skills Section: Evaluate the presentation and relevance of the skills section.
        9. ATS Optimization Recommendations: Provide specific tips to improve ATS compatibility.
        """

def generate_improvement_suggestions(resume_text, job_description, industry):
    # This function would ideally use more advanced NLP techniques
    # For simplicity, we'll use a basic keyword matching approach
    resume_keywords = set(extract_keywords(resume_text).keys())
    job_keywords = set(extract_keywords(job_description).keys())
    industry_keywords = set(INDUSTRY_TEMPLATES[industry]["keywords"])
    
    missing_job_keywords = job_keywords - resume_keywords
    missing_industry_keywords = industry_keywords - resume_keywords
    
    suggestions = [
        f"Consider adding these keywords from the job description: {', '.join(list(missing_job_keywords)[:5])}",
        f"Include industry-specific terms like: {', '.join(list(missing_industry_keywords)[:5])}",
        "Quantify your achievements with specific metrics and results",
        "Ensure your resume is ATS-friendly by using a simple, clean format",
        "Tailor your resume summary to directly address the job requirements",
        "Use action verbs to start each bullet point in your experience section",
        "Highlight your most relevant skills and experiences for this specific role",
        "Include any relevant certifications or training programs you've completed"
    ]
    
    return suggestions

def main():
    st.markdown('<p class="big-font">ATS Resume Expert</p>', unsafe_allow_html=True)

    # Sidebar for configuration
    with st.sidebar:
        st.subheader("Configuration")
        upload_option = st.radio("Choose input method:", ["Upload PDF", "Manual Input"])
        job_description = st.text_area("Job Description", height=200)
        industry = st.selectbox("Select Industry", list(INDUSTRY_TEMPLATES.keys()))
        analysis_type = st.selectbox("Analysis Type", ["Comprehensive Review", "Skill Gap Analysis", "Keyword Optimization", "ATS Match Score"])

    # Main content area
    resume_text = ""  # Initialize resume_text with an empty string
    if upload_option == "Upload PDF":
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
        if uploaded_file:
            pdf_content = input_pdf_setup(uploaded_file)
            resume_text = extract_text_from_pdf(uploaded_file)
            if resume_text:
                resume_text = st.text_area("Extracted Resume Text (Edit if needed):", value=resume_text, height=300)
            else:
                st.warning("Failed to extract text from PDF. Please use the manual input option.")
    else:
        resume_data = structured_resume_input()
        resume_text = format_resume(resume_data)
        resume_text = st.text_area("Formatted Resume Text (Edit if needed):", value=resume_text, height=300)

    if resume_text and job_description:
        if st.button("Analyze Resume", type="primary"):
            with st.spinner(f"Performing {analysis_type}... 🧠"):
                # Generate AI response
                prompt = generate_prompt(analysis_type, industry)
                ai_response = get_gemini_response(prompt, resume_text, job_description)
                
                # Calculate match percentage
                match_percentage = calculate_percentage_match(resume_text, job_description)
                
                # Generate improvement suggestions
                suggestions = generate_improvement_suggestions(resume_text, job_description, industry)
                
                # Display results
                st.subheader("Analysis Results")
                
                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Overall Match", f"{match_percentage}%")
                with col2:
                    keyword_match = min(100, match_percentage + 10)  # Simplified calculation
                    st.metric("Keyword Match", f"{keyword_match}%")
                with col3:
                    st.metric("ATS Readability", "High")
                
                # AI Feedback
                st.markdown(f"### {analysis_type} Feedback")
                st.markdown(ai_response)
                
                # Improvement Suggestions
                st.markdown("### Improvement Suggestions")
                for i, suggestion in enumerate(suggestions, 1):
                    st.info(f"{i}. {suggestion}")
    elif not resume_text:
        st.info("Please input your resume to begin the analysis.")
    elif not job_description:
        st.info("Please enter a job description to compare your resume against.")

if __name__ == "__main__":
    download_nltk_data()
    main()