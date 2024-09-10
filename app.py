import os
import requests
from dotenv import load_dotenv
from docx import Document
import re
import json
import streamlit as st
from io import BytesIO  # For downloading files

class ReviewSnippets:
    def __init__(self):
        load_dotenv()
        self.api_url = os.getenv("Llama_API_URL")
        self.api_key = os.getenv("Llama_API_KEY")

    def get_blog(self, topic, structure):
        # Prepare the request payload for the Llama model API
        messages = [
            {
                "role": "system",
                "content": f'''Generate a blog for my e-commerce site BestViewsReviews for Amazon Products. It is a GenAI platform that analyzes unstructured e-commerce product information like customer reviews, blogs, manufacturer-written product descriptions, etc., and generates insights and product recommendations. 
                Following is the structure of the blog:
                {structure}
                Topic: {topic}'''
            },
            {
                "role": "user",
                "content": f'Topic: {topic}'
            }
        ]

        # Define the headers and payload
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        payload = {
            "model": "meta-llama/Meta-Llama-3-8B-Instruct",
            "temperature": 0.7,
            "top_p": 0.95,
            "messages": messages,
            "max_tokens": 2048
        }

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
            
            response_json = response.json()
            generated_text = response_json['choices'][0]['message']['content']
            return generated_text

        except requests.exceptions.RequestException as e:
            return f"Request failed: {e}"

        except KeyError as e:
            return f"Key error: {e}"

        except json.JSONDecodeError as e:
            return f"JSON decode error: {e}"

    def save_to_doc(self, content):
        doc = Document()
        paragraph = doc.add_paragraph()

        # Split the content by double asterisks to identify bold text
        parts = re.split(r'(\*\*.*?\*\*)', content)

        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                # Add bold text
                run = paragraph.add_run(part[2:-2])
                run.bold = True
            else:
                # Add normal text
                paragraph.add_run(part)

        # Save to a BytesIO object to avoid filesystem issues
        doc_io = BytesIO()
        doc.save(doc_io)
        doc_io.seek(0)  # Reset the pointer to the beginning of the file
        return doc_io

# Streamlit UI
def main():
    st.title("AI Blog Generator for BVR")
    
    # Input fields with default values
    topic = st.text_input("Enter the blog topic", "Best Food Processors in India")
    structure = st.text_area("Enter the blog structure", 
        '''Blog Structure:
        Introduction

        Top picks based on important aspects – two products each aspect (include at least 4 to 5 aspects) - Provide detailed explanation of each product for each aspect, 2 paragraphs for each

        Things to keep in mind while choosing a food processor (6 to 7 factors to consider while buying a food processor)

        Expert tips on how to maintain a food processor

        FAQs - Provide detailed explanations for the following questions:

        Can a food processor replace a blender?
        Can I use a food processor for hot ingredients?
        What are 3 things you can do with a food processor?
        Which is better food processor or juicer?
        What size of food processor do I need?
        '''
    )

    # Check if 'blog_content' exists in session_state, if not, initialize it
    if 'blog_content' not in st.session_state:
        st.session_state.blog_content = ""

    # Button to generate blog content
    if st.button("Generate Blog"):
        extractor = ReviewSnippets()
        blog_content = extractor.get_blog(topic, structure)
        st.session_state.blog_content = blog_content  # Store the generated blog in session state

    # Show the generated content if it exists
    if st.session_state.blog_content:
        st.text_area("Generated Blog Content", st.session_state.blog_content, height=400, key="display_blog")

        # Download the blog as a DOCX file
        doc_io = ReviewSnippets().save_to_doc(st.session_state.blog_content)
        st.download_button(
            label="Download Blog as DOCX",
            data=doc_io,
            file_name="Blog_Content.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    # Display user name below
    st.markdown("---")
    st.markdown("### Created by AkshayTriapthiShorthillsAI")

if __name__ == "__main__":
    main()
