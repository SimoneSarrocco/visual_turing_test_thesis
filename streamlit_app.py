import streamlit as st
import os
import random
import pandas as pd

# Update paths to use relative paths
base_path = "images"
inputs_path = os.path.join(base_path, "inputs")
targets_path = os.path.join(base_path, "targets")
outputs_path = os.path.join(base_path, "outputs")

# Constants
COMPARISON_QUESTIONS = 20
PRESERVATION_QUESTIONS = 10
TOTAL_QUESTIONS = COMPARISON_QUESTIONS + PRESERVATION_QUESTIONS

# Create a list of indices
indices = list(range(1, 133))

# Function to get random unique image pairs for comparison
def get_comparison_images(num_questions, available_indices):
    selected_indices = random.sample(available_indices, num_questions)
    questions = []
    for index in selected_indices:
        target_image = os.path.join(targets_path, f"oct_high_quality_{index}.jpeg")
        output_image = os.path.join(outputs_path, f"oct_output_diffusion_{index}.jpeg")
        
        # Randomize the order of images, but the correct answer is always the target image
        if random.choice([True, False]):
            questions.append((target_image, output_image, "A"))  # Target is on the left
        else:
            questions.append((output_image, target_image, "B"))  # Target is on the right
    
    return questions, [index for index in available_indices if index not in selected_indices]

# Function to get random unique image pairs for preservation
def get_preservation_images(num_questions, available_indices):
    selected_indices = random.sample(available_indices, num_questions)
    questions = []
    for index in selected_indices:
        input_image = os.path.join(inputs_path, f"oct_low_quality_{index}.jpeg")
        output_image = os.path.join(outputs_path, f"oct_output_diffusion_{index}.jpeg")
        questions.append((input_image, output_image))
    
    return questions, [index for index in available_indices if index not in selected_indices]

# Initialize session state
if 'phase' not in st.session_state:
    st.session_state.phase = 'intro'
if 'available_indices' not in st.session_state:
    st.session_state.available_indices = indices.copy()
if 'comparison_questions' not in st.session_state:
    st.session_state.comparison_questions = []
if 'preservation_questions' not in st.session_state:
    st.session_state.preservation_questions = []
if 'comparison_responses' not in st.session_state:
    st.session_state.comparison_responses = []
if 'preservation_responses' not in st.session_state:
    st.session_state.preservation_responses = []
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0

# Improved CSS for proper spacing and alignment
st.markdown("""
    <style>
    .image-row {
        display: flex;
        justify-content: space-around;
        align-items: center;
        gap: 100px; /* Set gap between images */
        margin-bottom: 30px;
    }
    .image-row img {
        width: 384px;
        height: 248px;
    }
    .stApp {
        max-width: 1600px;
        margin: auto;
    }
    </style>
""", unsafe_allow_html=True)

# Display images in a single row with proper separation
def display_images(left, right, phase='comparison'):
    st.markdown('<div class="image-row">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1], gap="large")  # Adjust column width and gap
    with col1:
        if phase == 'comparison':
            caption = "Image A"
        else:
            caption = "ART10" if "inputs" in left else "Generated enhanced version"
        st.image(left, width=384, caption=caption)
    with col2:
        if phase == 'comparison':
            caption = "Image B"
        else:
            caption = "Generated enhanced version" if "outputs" in right else "ART10"
        st.image(right, width=384, caption=caption)
    st.markdown('</div>', unsafe_allow_html=True)

# Function to calculate fool rate
def calculate_fool_rate():
    total_wrong = sum(1 for response, question in zip(st.session_state.comparison_responses, st.session_state.comparison_questions)
                      if response != question[2])  # Fool rate is calculated by incorrect answers (not picking target)
    return (total_wrong / len(st.session_state.comparison_responses)) * 100

# Intro page
if st.session_state.phase == 'intro':
    st.title("Visual Turing Test for Vitreous OCT Images")
    st.write("""
    **Welcome to the Visual Turing Test for Vitreous OCT Images!**
    
    This test is part of the Master's Thesis of Simone Sarrocco conducted at the Department of Biomedical Engineering of the University of Basel, Switzerland, and the University of Bologna, Italy.
            
    The thesis is about enhancing the quality of vitreous OCT images using generative models.
             
    The aim of this test is to assess the clinical practicability of these models, to see whether the generated images may have clinical relevance and help ophthalmologists make even more accurate diagnoses.
    
    The test consists of two phases:
    1. Comparing 20 pairs of images, one real OCT image and one generated by a diffusion model, and selecting the one you think is the real OCT image.
    2. Looking at 10 pairs of images, one ART10 and one enhanced version generated by a model, try to assess whether the anatomical structures present in the ART10 image have been preserved in the generated enhanced version, and potential additional issues that you may notice in the generated image.
             
    There is no time restriction during the test. 
    
    Please answer to the best of your ability. Your responses will be invaluable for our research.
    
    **IMPORTANT**: Please activate "Wide Mode" for optimal image viewing.
    To do this, click on the three dots in the top-right corner, select "Settings", then enable "Wide mode".

    At the end of the test, please click on "Download Results" and send the .csv file to both philippe.valmaggia@unibas.ch and simone.sarrocco@unibas.ch
    """)
    if st.button("Start Test"):
        st.session_state.comparison_questions, st.session_state.available_indices = get_comparison_images(COMPARISON_QUESTIONS, st.session_state.available_indices)
        st.session_state.preservation_questions, st.session_state.available_indices = get_preservation_images(PRESERVATION_QUESTIONS, st.session_state.available_indices)
        st.session_state.phase = 'comparison'
        st.session_state.question_index = 0
        st.rerun()

# Comparison phase
elif st.session_state.phase == 'comparison':
    if st.session_state.question_index < COMPARISON_QUESTIONS:
        st.write(f"Question {st.session_state.question_index + 1}/{COMPARISON_QUESTIONS}")
        st.progress((st.session_state.question_index + 1) / COMPARISON_QUESTIONS)

        image_a, image_b, correct_answer = st.session_state.comparison_questions[st.session_state.question_index]
        display_images(image_a, image_b, phase='comparison')

        st.write("Which image do you think is the real OCT image (i.e., NOT generated by a model)?")
        answer = st.radio("Select your answer:", ["Image A", "Image B"], key=f"q_{st.session_state.question_index}")

        if st.button("Next", key=f"next_{st.session_state.question_index}"):
            st.session_state.comparison_responses.append(answer.split()[1])  # 'A' or 'B'
            st.session_state.question_index += 1
            st.rerun()
    else:
        fool_rate = calculate_fool_rate()
        st.write(f"You have completed the first phase of the test.")
        st.write(f"Your fool rate is: {fool_rate:.2f}%")
        if st.button("Continue to Phase 2"):
            st.session_state.phase = 'preservation'
            st.session_state.question_index = 0
            st.rerun()

# Preservation phase
elif st.session_state.phase == 'preservation':
    if st.session_state.question_index < PRESERVATION_QUESTIONS:
        st.write(f"Question {st.session_state.question_index + 1}/{PRESERVATION_QUESTIONS}")
        st.progress((st.session_state.question_index + 1) / PRESERVATION_QUESTIONS)

        input_image, output_image = st.session_state.preservation_questions[st.session_state.question_index]
        display_images(input_image, output_image, phase='preservation')

        st.write("Please answer the following questions about the images:")
        
        preservation = st.radio("Are all the anatomical structures present in the ART10 image preserved in its enhanced version generated by a model?", 
                                ["Yes", "No"], key=f"preservation_{st.session_state.question_index}")
        
        problems = st.text_area("Explain the main problems that you see in the generated image (e.g., introduction of new artifacts, bad reconstruction of specific anatomical structures, etc.)", 
                                key=f"problems_{st.session_state.question_index}")

        if st.button("Next", key=f"next_{st.session_state.question_index}"):
            st.session_state.preservation_responses.append({
                "preservation": preservation,
                "problems": problems
            })
            st.session_state.question_index += 1
            st.rerun()
    else:
        st.write("Thank you for completing the test!")
        
        # Prepare results for download
        comparison_df = pd.DataFrame({
            "question": range(1, COMPARISON_QUESTIONS + 1),
            "phase": ["comparison"] * COMPARISON_QUESTIONS,
            "response": st.session_state.comparison_responses,
            "correct_answer": [q[2] for q in st.session_state.comparison_questions],
            "fool_rate": [calculate_fool_rate()] * COMPARISON_QUESTIONS
        })
        
        preservation_df = pd.DataFrame({
            "question": range(COMPARISON_QUESTIONS + 1, TOTAL_QUESTIONS + 1),
            "phase": ["preservation"] * PRESERVATION_QUESTIONS,
            "response": [r["preservation"] for r in st.session_state.preservation_responses],
            "correct_answer": ["N/A"] * PRESERVATION_QUESTIONS,
            "fool_rate": ["N/A"] * PRESERVATION_QUESTIONS,
            "problems": [r["problems"] for r in st.session_state.preservation_responses]
        })

        # Merge into a single dataframe with one row per question
        results = pd.concat([comparison_df, preservation_df], axis=0, ignore_index=True)
        csv = results.to_csv(index=False)

        st.download_button(
            label="Download Results",
            data=csv,
            file_name="test_results.csv",
            mime="text/csv",
        )

# Add a note about Wide Mode
st.sidebar.write("**Remember**: Use Wide Mode for optimal viewing.")