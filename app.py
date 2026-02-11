# Import required libraries
from flask import Flask, request, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS (allows frontend to talk to backend)
CORS(app)

# Get API key from .env file
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Route 1: Test route (optional)
@app.route('/', methods=['GET'])
def home():
    return {"message": "PDF Summarizer API is running!"}

# Route 2: Main summarization endpoint
@app.route('/summarize', methods=['POST'])
def summarize():
    try:

        # Step 1: Check if file was uploaded
        if 'file' not in request.files:
            return {"error": "No file uploaded"}, 400

        file = request.files['file']

        # Step 2: Validate it's a PDF
        if not file.filename.endswith('.pdf'):
            return {"error": "Only PDF files are allowed"}, 400

        # Step 3: Extract text from PDF
        pdf_reader = PdfReader(file)
        text = ""

        for page in pdf_reader.pages:
            text += page.extract_text()

        # Check if text was extracted
        if not text.strip():
            return {"error": "Could not extract text from PDF"}, 400

        # Step 4: Send to Gemini AI for summarization
        prompt = f"""Please provide a clear and concise summary of the following document.
Organize it with bullet points if appropriate:
{text[:10000]}"""

        response = model.generate_content(prompt)
        summary = response.text

        # Step 5: Create new PDF with summary
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='darkblue',
            spaceAfter=30,
        )

        # Build PDF content
        story = []
        story.append(Paragraph("Document Summary", title_style))
        story.append(Spacer(1, 0.2 * inch))

        # Add summary text
        for paragraph in summary.split('\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph, styles['BodyText']))
                story.append(Spacer(1, 0.1 * inch))

        # Generate PDF
        doc.build(story)
        buffer.seek(0)

        # Step 6: Send PDF back to frontend
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='summary.pdf'
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}, 500

# Run the Flask server
if __name__ == '__main__':
    app.run(debug=True, port=5000)
