"""
PDF Export Service for Itineraries
Generates beautiful PDF documents for trip itineraries
"""

import logging
from datetime import datetime
from typing import Optional
from io import BytesIO

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image as RLImage
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not installed. PDF export will not work.")

from backend.app.models.itinerary import TripItinerary

logger = logging.getLogger(__name__)


class PDFExportService:
    """Service for exporting itineraries to PDF"""
    
    def __init__(self):
        self.styles = None
        if REPORTLAB_AVAILABLE:
            self._init_styles()
    
    def _init_styles(self):
        """Initialize PDF styles"""
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='DayTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2563EB'),
            spaceAfter=12,
            spaceBefore=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='ActivityTime',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#4B5563'),
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='ActivityTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#111827'),
            fontName='Helvetica-Bold',
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='ActivityDescription',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6B7280'),
            leftIndent=20
        ))
    
    async def export_itinerary_to_pdf(
        self,
        itinerary: TripItinerary,
        include_booking_links: bool = True
    ) -> bytes:
        """
        Export itinerary to PDF
        
        Args:
            itinerary: TripItinerary object
            include_booking_links: Whether to include booking URLs
        
        Returns:
            PDF file as bytes
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "ReportLab is not installed. "
                "Install with: pip install reportlab"
            )
        
        try:
            # Create PDF in memory
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build document content
            story = []
            
            # Title
            title = Paragraph(
                f"<b>{itinerary.title}</b>",
                self.styles['CustomTitle']
            )
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Trip details
            trip_details = [
                ['Destination:', itinerary.destination],
                ['Duration:', f"{itinerary.duration_days} days"],
                ['Dates:', f"{itinerary.start_date.strftime('%B %d, %Y')} - {itinerary.end_date.strftime('%B %d, %Y')}"],
                ['Budget:', f"{itinerary.budget_level.value.title()}"],
                ['Travelers:', str(itinerary.travelers_count)],
                ['Total Cost:', f"${itinerary.total_estimated_cost:.2f} {itinerary.currency}"]
            ]
            
            details_table = Table(trip_details, colWidths=[2*inch, 4*inch])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#111827')),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB'))
            ]))
            
            story.append(details_table)
            story.append(Spacer(1, 30))
            
            # Cost breakdown
            if itinerary.cost_breakdown:
                story.append(Paragraph(
                    "<b>Cost Breakdown</b>",
                    self.styles['Heading2']
                ))
                story.append(Spacer(1, 12))
                
                cost_data = []
                for category, cost in itinerary.cost_breakdown.items():
                    if cost > 0:
                        cost_data.append([
                            category.replace('_', ' ').title(),
                            f"${cost:.2f}"
                        ])
                
                if cost_data:
                    cost_table = Table(cost_data, colWidths=[4*inch, 2*inch])
                    cost_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EFF6FF')),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#111827')),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB'))
                    ]))
                    story.append(cost_table)
                    story.append(Spacer(1, 20))
            
            story.append(PageBreak())
            
            # Day-by-day itinerary
            for day in itinerary.days:
                # Day header
                day_title = Paragraph(
                    f"<b>Day {day.day_number}: {day.title}</b>",
                    self.styles['DayTitle']
                )
                story.append(day_title)
                
                day_date = Paragraph(
                    f"<i>{day.date.strftime('%A, %B %d, %Y')}</i>",
                    self.styles['Normal']
                )
                story.append(day_date)
                story.append(Spacer(1, 12))
                
                # Activities
                for activity in day.activities:
                    # Time slot
                    time_para = Paragraph(
                        f"<b>{activity.time_slot}</b>",
                        self.styles['ActivityTime']
                    )
                    story.append(time_para)
                    story.append(Spacer(1, 4))
                    
                    # Activity title
                    title_text = activity.title
                    if activity.rating:
                        title_text += f" ⭐ {activity.rating}/5"
                    
                    activity_title = Paragraph(
                        f"<b>{title_text}</b>",
                        self.styles['ActivityTitle']
                    )
                    story.append(activity_title)
                    
                    # Description
                    if activity.description:
                        desc = Paragraph(
                            activity.description[:200],
                            self.styles['ActivityDescription']
                        )
                        story.append(desc)
                    
                    # Cost
                    if activity.estimated_cost > 0:
                        cost_para = Paragraph(
                            f"<i>Cost: ${activity.estimated_cost:.2f}</i>",
                            self.styles['ActivityDescription']
                        )
                        story.append(cost_para)
                    
                    # Booking link
                    if include_booking_links and activity.booking_url:
                        booking_para = Paragraph(
                            f"📗 <i>Book online: {activity.booking_partner or 'Available'}</i>",
                            self.styles['ActivityDescription']
                        )
                        story.append(booking_para)
                    
                    # Tips
                    if activity.tips:
                        tips_text = "<br/>".join([f"💡 {tip}" for tip in activity.tips[:2]])
                        tips_para = Paragraph(
                            tips_text,
                            self.styles['ActivityDescription']
                        )
                        story.append(tips_para)
                    
                    story.append(Spacer(1, 16))
                
                # Day total
                if day.total_cost > 0:
                    day_total = Paragraph(
                        f"<b>Day Total: ${day.total_cost:.2f}</b>",
                        self.styles['Normal']
                    )
                    story.append(day_total)
                
                story.append(Spacer(1, 20))
                
                # Page break after each day (except last)
                if day.day_number < itinerary.duration_days:
                    story.append(PageBreak())
            
            # Footer
            story.append(Spacer(1, 30))
            footer = Paragraph(
                f"<i>Generated by Sri Lanka Tourism Chatbot on {datetime.utcnow().strftime('%B %d, %Y')}</i>",
                self.styles['Normal']
            )
            story.append(footer)
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Generated PDF for itinerary {itinerary.id} ({len(pdf_bytes)} bytes)")
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}", exc_info=True)
            raise


# Singleton instance
_pdf_service = None

def get_pdf_export_service() -> PDFExportService:
    """Get PDF export service singleton"""
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFExportService()
    return _pdf_service

