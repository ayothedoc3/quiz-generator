import streamlit as st
import time
import random
import google.generativeai as genai
import os
import json

# Configure Gemini API
def setup_gemini_api():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
        if not api_key:
            st.warning("⚠️ Please enter a Gemini API key to enable real quiz generation!")
            return None
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="AI Quiz Generator MVP", layout="wide")

st.title("AI Quiz Generator Workflow Demo")
st.markdown("### A visual demonstration of the WordPress automation system with Gemini API")

# Sidebar for controls
with st.sidebar:
    st.header("Quiz Generation Controls")
    subject = st.selectbox(
        "Select Subject",
        ["History", "Science", "Literature", "Geography", "Mathematics"]
    )
    
    question_count = st.slider("Number of Questions", min_value=3, max_value=10, value=5)
    
    use_real_api = st.checkbox("Use actual Gemini API", value=False)
    
    generate_button = st.button("Generate Quiz & WordPress Page")

# Main content area
col1, col2 = st.columns([1, 1])

# Sample quiz data for fallback
sample_quiz_data = {
    "History": {
        "title": "History Knowledge Quiz",
        "questions": [
            {
                "question": "Who was the first President of the United States?",
                "options": ["George Washington", "Thomas Jefferson", "Abraham Lincoln", "John Adams"],
                "answer": 0
            },
            # more questions...
        ]
    },
    "Science": {
        "title": "Science Knowledge Quiz",
        "questions": [
            {
                "question": "What is the chemical symbol for gold?",
                "options": ["Go", "Gd", "Au", "Ag"],
                "answer": 2
            },
            # more questions...
        ]
    },
    # more subjects...
}

# Initialize session state
if 'generated' not in st.session_state:
    st.session_state.generated = False
    st.session_state.progress = 0
    st.session_state.quiz_data = None

# Function to generate quiz using Gemini API
def generate_quiz_with_gemini(subject, count):
    # Set up Gemini
    model = setup_gemini_api()
    if not model:
        return None
    
    # Create prompt for Gemini
    prompt = f"""
    Create a knowledge quiz about {subject} with {count} questions.
    
    Format your response as a JSON object with the following structure:
    {{
        "title": "Quiz title here",
        "questions": [
            {{
                "question": "Question text here?",
                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                "answer": 0  // Index of correct answer (0-3)
            }},
            // More questions...
        ]
    }}
    
    Make sure:
    1. Questions are challenging but fair
    2. Each question has exactly 4 options
    3. The answer index is correct (0-3)
    4. The JSON is valid and properly formatted
    5. Questions are interesting and educational
    """
    
    try:
        # Call Gemini API
        response = model.generate_content(prompt)
        
        # Extract and parse JSON from response
        content = response.text
        # Find JSON content (if embedded in markdown or other text)
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = content[json_start:json_end]
            return json.loads(json_str)
        else:
            st.error("Could not parse JSON from Gemini response")
            return None
    except Exception as e:
        st.error(f"Error calling Gemini API: {str(e)}")
        return None

# Process button click
if generate_button:
    st.session_state.generated = False
    st.session_state.progress = 0
    
    # Display the workflow with a progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Subject Selection
    status_text.text("Step 1: Subject selected - " + subject)
    progress_bar.progress(10)
    time.sleep(0.5)
    
    # Step 2: Quiz Generation
    status_text.text("Step 2: Generating quiz content with Gemini API...")
    progress_bar.progress(30)
    
    if use_real_api:
        # Call actual Gemini API
        quiz_data = generate_quiz_with_gemini(subject, question_count)
        if not quiz_data:
            quiz_data = sample_quiz_data.get(subject, sample_quiz_data["Science"])
            status_text.text("⚠️ Falling back to sample data (API issue)")
    else:
        # Use sample data
        time.sleep(1.0)  # Simulate API call delay
        quiz_data = sample_quiz_data.get(subject, sample_quiz_data["Science"])
    
    st.session_state.quiz_data = quiz_data
    
    # Step 3: WordPress Quiz Integration
    status_text.text("Step 3: Formatting quiz for WordPress plugin...")
    progress_bar.progress(50)
    time.sleep(0.7)
    
    # Step 4: Page Creation
    status_text.text("Step 4: Creating new WordPress page...")
    progress_bar.progress(70)
    time.sleep(0.7)
    
    # Step 5-6: Quiz Button Insertion & Attachment
    status_text.text("Step 5-6: Adding quiz buttons and linking quiz...")
    progress_bar.progress(85)
    time.sleep(0.7)
    
    # Step 7: Category Assignment
    status_text.text("Step 7: Assigning to category: " + subject + " Quizzes")
    progress_bar.progress(100)
    time.sleep(0.5)
    
    status_text.text("✅ Complete! Page created with " + str(question_count) + " questions")
    st.session_state.generated = True
    st.session_state.progress = 100

# Display the generated content
if st.session_state.generated and st.session_state.quiz_data:
    quiz_data = st.session_state.quiz_data
    
    with col1:
        st.markdown("### 📊 Generated Quiz")
        st.markdown(f"**{quiz_data['title']}**")
        
        # Show sample questions
        for i, q in enumerate(quiz_data['questions'][:question_count]):
            st.markdown(f"**Q{i+1}: {q['question']}**")
            for j, option in enumerate(q['options']):
                if j == q['answer']:
                    st.markdown(f"- ✅ {option}")
                else:
                    st.markdown(f"- {option}")
            st.markdown("---")
    
    with col2:
        st.markdown("### 📄 WordPress Page Preview")
        
        # Sample WordPress page
        st.markdown(f"## {quiz_data['title']}")
        st.markdown("Test your knowledge with this interactive quiz!")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.button("Start Quiz", type="primary")
        with col_btn2:
            st.button("View Past Results")
        
        st.markdown("---")
        st.markdown("### WordPress Details:")
        st.markdown(f"✅ **Page Title:** {quiz_data['title']}")
        st.markdown(f"✅ **Category:** {subject} Quizzes")
        st.markdown(f"✅ **URL:** example.com/{subject.lower()}-knowledge-quiz")
        st.markdown(f"✅ **Questions:** {question_count} questions created")
        st.markdown(f"✅ **Date:** {time.strftime('%B %d, %Y')}")

# Add explanation at the bottom
st.markdown("---")
st.markdown("""
### How the Gemini API Integration Works

1. **Prompt Creation:** The system creates a specific prompt asking Gemini to generate a quiz on the selected subject
2. **API Call:** The prompt is sent to Google's Gemini Pro API
3. **Response Processing:** The JSON response is parsed and structured for the quiz format
4. **WordPress Formatting:** The quiz data is prepared for your WordPress quiz plugin
5. **Page Generation:** A WordPress page is created with the quiz embedded

In this demo, you can toggle between sample data and real Gemini API calls. The final system will exclusively use Gemini to generate unique, high-quality quiz content automatically.
""")

# Add API documentation
with st.expander("View Gemini API Integration Details"):
    st.code("""
# Example Gemini API prompt
prompt = f'''
Create a knowledge quiz about {subject} with {count} questions.

Format your response as a JSON object with the following structure:
{
    "title": "Quiz title here",
    "questions": [
        {
            "question": "Question text here?",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "answer": 0  // Index of correct answer (0-3)
        },
        // More questions...
    ]
}
'''

# API Call
response = genai.generate_content(prompt)
    """, language="python")