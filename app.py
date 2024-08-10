from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import io
import base64
from PIL import Image
import pdf2image
import google.generativeai as genai

genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))


def get_gemini_response(input, pdf_content, prompt):
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([input,pdf_content[0],prompt])
        return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]

        img_bytes_arr = io.BytesIO()
        first_page.save(img_bytes_arr, format = 'JPEG')
        img_bytes_arr = img_bytes_arr.getvalue()

        pdf_parts = [
            {
                "mime_type" : "image/jpeg",
                "data" : base64.b64encode(img_bytes_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

st.set_page_config(page_title= "ATS Resume Expert")
st.header("ATS Tracking System")
input_text = st.text_area("Job Description",key="input")
uploaded_file = st.file_uploader("Upload your resume(PDF)...",type = ["pdf"])

if uploaded_file is not None:
     st.write("PDF Uploaded Successfully")

submit1 = st.button("Tell me about resume")
submit2 = st.button("How can I improvise my skills")
submit3 = st.button("What are the keywords that are missing?")
submit4 = st.button("Percentage match")


input_prompt1 = """
As an experienced Human Resource Manager with extensive technical expertise in Data Science, Full Stack Development, Web Development, Big Data Engineering, DevOps, and Data Analysis:

1. Conduct a thorough review of the provided resume against the job description.
2. Evaluate the alignment between the candidate's profile and the role requirements.
3. Highlight specific strengths of the applicant, citing relevant experiences and skills that match the job.
4. Identify any weaknesses or gaps in the candidate's profile relative to the job requirements.
5. Assess the candidate's potential cultural fit based on any relevant information in the resume.
6. Provide an overall recommendation: Strongly Recommend, Recommend, Consider, or Do Not Recommend.
7. Suggest 2-3 specific questions for the interviewer to ask the candidate to better assess their fit for the role.

Your evaluation should be detailed, impartial, and focused on how well the candidate meets the specific needs outlined in the job description.
"""

input_prompt2 = """
As a Technical Human Resource Manager specializing in Data Science, Full Stack Development, Web Development, Big Data Engineering, DevOps, and Data Analysis:

1. Scrutinize the resume in light of the provided job description, focusing on technical qualifications.
2. Assess the candidate's technical skill set, experience, and projects against the job requirements.
3. Identify any missing critical skills or experiences that are essential for the role.
4. Suggest specific areas where the candidate could enhance their skills to better align with the job requirements.
5. Recommend relevant courses, certifications, or projects that could address any skill gaps.
6. Provide advice on how the candidate could better present their technical skills and experiences in their resume.
7. Suggest potential career paths or specializations within their field that the candidate might consider based on their current skill set.

Your analysis should be technically focused, providing actionable insights for skill improvement and career development.
"""
input_prompt4 = """
You are an skilled ATS(Applicant Tracking System) scanner with a deep understanding of Data Science, Full Stack, Web Development, Big Data Engineering, DEVOPS, Data Analysis and deep ATS functionality.
Your task is to evaluate the resume against the job description.Give me the percentage of match if resume matches with the job description.
First, the output should come as percentage and then keywords missing and last final thoughts

"""
input_prompt3 = """
You are an advanced Applicant Tracking System (ATS) with expertise in analyzing resumes for roles in Data Science, Full Stack Development, Web Development, Big Data Engineering, DevOps, and Data Analysis.

Your task is to meticulously scan the provided resume and compare it against the given job description. Focus on identifying the following:

1. Key technical skills mentioned in the job description that are missing from the resume.
2. Important soft skills or qualifications stated in the job description but not reflected in the resume.
3. Industry-specific keywords or buzzwords that are present in the job description but absent in the resume.
4. Any certifications, tools, or technologies mentioned in the job description that the candidate's resume lacks.

Please provide a comprehensive list of these missing keywords and phrases. This information will be crucial for the candidate to understand how to optimize their resume for better ATS performance.

Additionally, suggest how the candidate might incorporate these missing elements into their resume, if they possess the relevant skills or experiences.

Your analysis should be thorough and specific, helping the candidate to align their resume more closely with the job requirements and increase their chances of passing through ATS filters.
"""

if submit1:
    if uploaded_file is not None:
          pdf_content = input_pdf_setup(uploaded_file)
          response = get_gemini_response(input_prompt1, pdf_content, input_text)
          st.subheader("The Response is")
          st.write(response)
    else:
         st.write("Please upload the resume")
elif submit2:
    if uploaded_file is not None:
          pdf_content = input_pdf_setup(uploaded_file)
          response = get_gemini_response(input_prompt2, pdf_content, input_text)
          st.subheader("The Response is")
          st.write(response)
    else:
         st.write("Please upload the resume")
elif submit3:
    if uploaded_file is not None:
          pdf_content = input_pdf_setup(uploaded_file)
          response = get_gemini_response(input_prompt3, pdf_content, input_text)
          st.subheader("The Response is")
          st.write(response)
    else:
         st.write("Please upload the resume")
elif submit4:
    if uploaded_file is not None:
          pdf_content = input_pdf_setup(uploaded_file)
          response = get_gemini_response(input_prompt4, pdf_content, input_text)
          st.subheader("The Response is")
          st.write(response)
    else:
         st.write("Please upload the resume")

