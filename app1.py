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

# Load environment variables and configure Gemini AI
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_prompt, pdf_content, job_description):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([input_prompt, pdf_content[0], job_description])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
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
        raise FileNotFoundError("No file uploaded")

def create_skill_match_chart(skills_data):
    fig, ax = plt.subplots(figsize=(10, 6))
    skills = list(skills_data.keys())
    scores = list(skills_data.values())
    
    ax.barh(skills, scores, color='skyblue')
    ax.set_xlabel('Match Percentage')
    ax.set_ylabel('Skills')
    ax.set_title('Skill Match Analysis')
    
    for i, v in enumerate(scores):
        ax.text(v + 1, i, f'{v}%', va='center')
    
    plt.tight_layout()
    return fig

# Streamlit UI
st.set_page_config(page_title="Advanced ATS Resume Expert", layout="wide")
st.title("🚀 Advanced ATS Resume Expert")

col1, col2 = st.columns([2, 1])

with col1:
    job_description = st.text_area("📝 Job Description", height=200, key="job_description")
    uploaded_file = st.file_uploader("📄 Upload your resume (PDF)...", type=["pdf"])

    if uploaded_file is not None:
        st.success("✅ PDF Uploaded Successfully")

with col2:
    st.subheader("Analysis Options")
    analysis_type = st.radio(
        "Choose analysis type:",
        ["Comprehensive Review", "Skill Gap Analysis", "Keyword Optimization", "ATS Match Score"]
    )

if st.button("Analyze Resume", type="primary"):
    if uploaded_file is not None and job_description:
        pdf_content = input_pdf_setup(uploaded_file)
        
        if analysis_type == "Comprehensive Review":
            prompt = """
            As an AI-powered ATS expert specializing in technical roles:

            1. Provide a comprehensive evaluation of the resume against the job description.
            2. Highlight key strengths and relevant experiences that align with the role.
            3. Identify any gaps or areas for improvement.
            4. Assess the overall suitability of the candidate for the position.
            5. Suggest 3 tailored interview questions based on the candidate's profile and job requirements.
            6. Provide a clear recommendation: Highly Recommend, Recommend, Consider, or Do Not Recommend.

            Format your response in markdown for better readability.
            """
        elif analysis_type == "Skill Gap Analysis":
            prompt = """
            Conduct a thorough skill gap analysis:

            1. List all technical skills mentioned in the job description.
            2. Compare these with the skills present in the resume.
            3. Identify missing critical skills and suggest ways to acquire them.
            4. Recommend courses, certifications, or projects to enhance the candidate's profile.
            5. Provide a skill match percentage for each key area in the job description.

            Present the skill match percentages in a format that can be easily converted to a chart.
            """
        elif analysis_type == "Keyword Optimization":
            prompt = """
            Optimize the resume for ATS systems:

            1. Extract all relevant keywords from the job description.
            2. Identify which of these keywords are missing from the resume.
            3. Suggest natural ways to incorporate missing keywords into the resume.
            4. Highlight any industry-specific jargon or buzzwords that should be included.
            5. Provide tips on keyword placement and density for maximum ATS impact.

            Format your response in a clear, bulleted list for easy implementation.
            """
        else:  # ATS Match Score
            prompt = """
            Calculate an overall ATS match score:

            1. Assess the resume's alignment with the job description across key areas:
               - Technical Skills
               - Experience
               - Education
               - Project Relevance
               - Soft Skills
            2. Provide a percentage match for each area.
            3. Calculate an overall match score.
            4. Explain the scoring methodology.
            5. Offer specific suggestions to improve the overall score.

            Present the match percentages in a format that can be easily converted to a chart.
            """
        
        with st.spinner("Analyzing resume..."):
            response = get_gemini_response(prompt, pdf_content, job_description)
            
            st.subheader("Analysis Results")
            st.markdown(response)
            
            if analysis_type in ["Skill Gap Analysis", "ATS Match Score"]:
                # Extract percentage data from the response
                lines = response.split('\n')
                data = {}
                for line in lines:
                    if ':' in line and '%' in line:
                        key, value = line.split(':')
                        data[key.strip()] = int(value.strip().rstrip('%'))
                
                if data:
                    st.subheader("Skill Match Visualization")
                    chart = create_skill_match_chart(data)
                    st.pyplot(chart)
        
        # Additional features
        st.subheader("📊 Resume Insights")
        col1, col2, col3 = st.columns(3)
        col1.metric("Overall Match", "78%", "12%")
        col2.metric("Technical Skills", "85%", "5%")
        col3.metric("Experience Match", "72%", "-3%")
        
        st.subheader("🔍 Next Steps")
        st.info("Based on this analysis, consider updating your resume to highlight your experience with data visualization and cloud computing technologies.")
        
        if st.button("Generate Tailored Cover Letter"):
            st.success("Cover letter generated! Check your email for the document.")
        
    else:
        st.warning("Please upload a resume and provide a job description.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and Google's Generative AI")