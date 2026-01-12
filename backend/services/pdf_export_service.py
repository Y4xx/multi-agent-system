"""
PDF Export Service for Cover Letters.
Creates modern, ATS-friendly PDF documents from cover letter text.
"""

import os
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY


class PDFExportService:
    """
    Service for exporting cover letters to PDF format.
    Creates professional, ATS-friendly PDFs.
    """
    
    def __init__(self):
        """Initialize PDF export service."""
        # Create output directory
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "exports"
        )
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _create_styles(self):
        """
        Create custom styles for the PDF.
        
        Returns:
            Dictionary of styles
        """
        styles = getSampleStyleSheet()
        
        # Custom style for contact info
        styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=6
        ))
        
        # Custom style for body text
        styles.add(ParagraphStyle(
            name='BodyText',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            firstLineIndent=0
        ))
        
        # Custom style for salutation
        styles.add(ParagraphStyle(
            name='Salutation',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=12
        ))
        
        return styles
    
    def export_to_pdf(
        self,
        cover_letter_text: str,
        candidate_name: str,
        job_title: str,
        company: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Export cover letter to PDF.
        
        Args:
            cover_letter_text: The cover letter content
            candidate_name: Name of the candidate
            job_title: Job title for the position
            company: Company name
            filename: Optional custom filename (without .pdf extension)
            
        Returns:
            Path to the generated PDF file
        """
        # Generate filename if not provided
        if not filename:
            safe_company = "".join(c for c in company if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_job = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_')).strip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"CoverLetter_{safe_company}_{safe_job}_{timestamp}"
        
        # Ensure .pdf extension
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Get styles
        styles = self._create_styles()
        
        # Build document content
        story = []
        
        # Split cover letter into paragraphs
        paragraphs = cover_letter_text.strip().split('\n\n')
        
        for para_text in paragraphs:
            if not para_text.strip():
                continue
            
            # Clean the paragraph text
            para_text = para_text.strip().replace('\n', ' ')
            
            # Determine style based on content
            if any(keyword in para_text.lower() for keyword in ['dear', 'sincerely', 'regards', 'best']):
                style = styles['Salutation']
            else:
                style = styles['BodyText']
            
            # Add paragraph
            para = Paragraph(para_text, style)
            story.append(para)
            story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def export_with_metadata(
        self,
        cover_letter_text: str,
        cv_data: dict,
        job_data: dict,
        filename: Optional[str] = None
    ) -> str:
        """
        Export cover letter to PDF with metadata from CV and job data.
        
        Args:
            cover_letter_text: The cover letter content
            cv_data: Parsed CV data
            job_data: Job offer data
            filename: Optional custom filename
            
        Returns:
            Path to the generated PDF file
        """
        candidate_name = cv_data.get('name', 'Candidate')
        job_title = job_data.get('title', 'Position')
        company = job_data.get('company') or job_data.get('organization', 'Company')
        
        return self.export_to_pdf(
            cover_letter_text=cover_letter_text,
            candidate_name=candidate_name,
            job_title=job_title,
            company=company,
            filename=filename
        )


# Singleton instance
pdf_export_service = PDFExportService()
