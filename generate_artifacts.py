import os
from fpdf import FPDF
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor


def generate_pdf(title, text_content, output_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(5)
    
    pdf.set_font("Helvetica", size=10)
    for line in text_content.split('\n'):
        # Sanitize text for FPDF latin-1
        clean_line = line.encode('latin-1', 'replace').decode('latin-1')
        if not clean_line.strip():
            pdf.ln(3)
        elif clean_line.startswith('# '):
            pdf.set_font("Helvetica", 'B', 14)
            pdf.cell(0, 8, clean_line[2:], new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", size=10)
        elif clean_line.startswith('## '):
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 6, clean_line[3:], new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", size=10)
        else:
            pdf.multi_cell(0, 5, clean_line, new_x="LMARGIN", new_y="NEXT")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    print(f"Generated PDF: {output_path}")


def generate_presentation(output_path):
    prs = Presentation()
    
    # Title Slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "Healthcare Patient Management System"
    subtitle.text = "Full-Stack ETL Data Pipeline, MySQL Database & React Dashboard\nUCI Diabetes 130-US Hospitals Dataset"
    
    # Slide 2: Problem Statement
    bullet_slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    title_shape.text = "Project Objectives & Business Need"
    tf = body_shape.text_frame
    tf.text = "Automated processing of 100,000+ hospital encounter records."
    p = tf.add_paragraph()
    p.text = "Clean raw CSV dataset and eliminate missing values ('?')."
    p = tf.add_paragraph()
    p.text = "Normalize data into MySQL relational tables (Patients & Encounters)."
    p = tf.add_paragraph()
    p.text = "Expose REST APIs via FastAPI microservice with live Swagger UI."
    p = tf.add_paragraph()
    p.text = "Build executive React + Vite dashboard for operational analytics."

    # Slide 3: Technology Stack
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    title_shape.text = "Technology Stack & Frameworks"
    tf = body_shape.text_frame
    tf.text = "Data Processing: Python 3.10+, Pandas"
    p = tf.add_paragraph()
    p.text = "Database Engine: MySQL 8.0, SQLAlchemy ORM, PyMySQL"
    p = tf.add_paragraph()
    p.text = "Backend Microservice: FastAPI, Uvicorn, Pydantic, python-dotenv"
    p = tf.add_paragraph()
    p.text = "Frontend Interface: React 18, Vite 6, Axios, Recharts, Lucide React"

    # Slide 4: Empirical Results
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    title_shape.text = "Operational Analytics & Findings"
    tf = body_shape.text_frame
    tf.text = "Unique Patients Ingested: 71,518 Records"
    p = tf.add_paragraph()
    p.text = "Total Hospital Encounters: 101,766 Records"
    p = tf.add_paragraph()
    p.text = "30-Day Readmission Rate: 46.09% (>30d: 34.93%, <30d: 11.16%)"
    p = tf.add_paragraph()
    p.text = "Average Length of Inpatient Stay: 4.40 Days"
    p = tf.add_paragraph()
    p.text = "Average Prescribed Medications per Visit: 16.02"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    print(f"Generated PowerPoint Presentation: {output_path}")


if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Read design doc markdown
    design_md_path = os.path.join(BASE_DIR, 'design', 'Design_Document.md')
    if os.path.exists(design_md_path):
        with open(design_md_path, 'r', encoding='utf-8') as f:
            design_text = f.read()
        generate_pdf("System Design Document", design_text, os.path.join(BASE_DIR, 'design', 'Design_Document.pdf'))
        
    # Read architecture markdown
    arch_md_path = os.path.join(BASE_DIR, 'architecture', 'Architecture_Diagram.md')
    if os.path.exists(arch_md_path):
        with open(arch_md_path, 'r', encoding='utf-8') as f:
            arch_text = f.read()
        generate_pdf("System Architecture Diagram", arch_text, os.path.join(BASE_DIR, 'architecture', 'Architecture_Diagram.pdf'))
        
    # Generate presentation deck
    generate_presentation(os.path.join(BASE_DIR, 'presentation', 'Project_Presentation.pptx'))
