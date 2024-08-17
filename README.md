# 🚀 Advanced ATS Resume Expert

Advanced ATS Resume Expert is a powerful Streamlit-based web application that leverages Google's Generative AI to provide comprehensive resume analysis and optimization. This tool helps job seekers align their resumes with job descriptions, identify skill gaps, and improve their chances of passing Applicant Tracking Systems (ATS).

## 🌟 Features

- **Comprehensive Resume Review**: Evaluate resumes against job descriptions with detailed insights.
- **Skill Gap Analysis**: Identify missing skills and get suggestions for improvement.
- **Keyword Optimization**: Optimize resumes for ATS systems with relevant keywords.
- **ATS Match Score**: Calculate and visualize how well a resume matches a job description.
- **Interactive UI**: User-friendly interface with options for different types of analysis.
- **Data Visualization**: Visual representation of skill matches and resume insights.
- **Cover Letter Generation**: Option to generate tailored cover letters based on the analysis.

## 🛠️ Prerequisites

- Python 3.7+
- Google API key for Generative AI

## 📦 Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/advanced-ats-resume-expert.git
   cd advanced-ats-resume-expert
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   Create a `.env` file in the project root and add your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## 🚀 Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Enter the job description in the text area provided.

4. Upload a resume in PDF format.

5. Choose an analysis type:
   - Comprehensive Review
   - Skill Gap Analysis
   - Keyword Optimization
   - ATS Match Score

6. Click "Analyze Resume" to start the analysis.

7. Review the results, including:
   - Detailed analysis based on the chosen type
   - Skill match visualizations (for applicable analysis types)
   - Resume insights and metrics
   - Suggestions for next steps

8. Optionally, generate a tailored cover letter based on the analysis.

## 📁 Project Structure

```
advanced-ats-resume-expert/
│
├── app.py              # Main Streamlit application
├── .env                # Environment variables (API keys)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 📚 Dependencies

- streamlit
- python-dotenv
- Pillow
- pdf2image
- google-generativeai
- pandas
- matplotlib

## 🤝 Contributing

Contributions to improve the project are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgments

- Google for the Generative AI model
- Streamlit for the web application framework
- The open-source community for various libraries used in this project

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact

For any queries or suggestions, please open an issue in the GitHub repository.

---

Built with ❤️ using Streamlit and Google's Generative AI
