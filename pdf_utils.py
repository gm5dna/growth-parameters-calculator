"""
PDF Export Utilities for Growth Parameters Calculator

This module provides PDF generation functionality for growth parameter reports
using ReportLab library.
"""

from io import BytesIO
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.pdfgen import canvas
from PIL import Image as PILImage


class NumberedCanvas(canvas.Canvas):
    """Custom canvas to add page numbers"""

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        page_num = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(A4[0] - 2*cm, 1.5*cm, page_num)


class GrowthReportPDF:
    """
    Generates professional PDF reports for growth parameter calculations.

    Includes patient information, measurements, growth charts, and warnings.
    """

    def __init__(self, results, patient_info, chart_images=None):
        """
        Initialize PDF report generator.

        Args:
            results (dict): Calculation results from the API
            patient_info (dict): Patient demographic information
            chart_images (dict): Base64 encoded chart images (optional)
        """
        self.results = results
        self.patient_info = patient_info
        self.chart_images = chart_images or {}
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=0,
            borderColor=colors.HexColor('#1e40af'),
            borderRadius=None,
            backColor=colors.HexColor('#eff6ff'),
            leftIndent=6,
            rightIndent=6
        ))

        # Normal text style
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#1f2937')
        ))

        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))

        # Warning style
        self.styles.add(ParagraphStyle(
            name='Warning',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#dc2626'),
            leftIndent=12
        ))

    def _create_header(self):
        """Create report header"""
        elements = []

        # Title
        title = Paragraph("Growth Parameters Report", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*cm))

        # Report metadata
        report_date = datetime.now().strftime('%d/%m/%Y %H:%M')
        reference = self.patient_info.get('reference', 'uk-who')
        reference_text = reference.upper().replace('-', '-')

        metadata_text = f"<font size=9>Generated: {report_date} | Reference: {reference_text}</font>"
        metadata = Paragraph(metadata_text, self.styles['CustomNormal'])
        elements.append(metadata)
        elements.append(Spacer(1, 0.5*cm))

        return elements

    def _create_patient_info_section(self):
        """Create patient information section"""
        elements = []

        # Section heading
        heading = Paragraph("PATIENT INFORMATION", self.styles['SectionHeading'])
        elements.append(heading)
        elements.append(Spacer(1, 0.3*cm))

        # Patient data
        sex = self.patient_info.get('sex', 'Unknown')
        sex_display = 'Male' if sex == 'male' else 'Female' if sex == 'female' else sex

        birth_date = self.patient_info.get('birth_date', 'N/A')
        measurement_date = self.patient_info.get('measurement_date', 'N/A')

        # Get age from results
        age_text = 'N/A'
        age_years = self.results.get('age_years')
        age_calendar = self.results.get('age_calendar')

        if age_years is not None:
            age_text = f"{age_years:.2f} years"
            if age_calendar and isinstance(age_calendar, dict):
                years = age_calendar.get('years', 0)
                months = age_calendar.get('months', 0)
                days = age_calendar.get('days', 0)
                age_text += f" ({years}y {months}m {days}d)"

        # If gestation correction was applied, show corrected age
        if self.results.get('gestation_correction_applied'):
            corrected_age_years = self.results.get('corrected_age_years')
            corrected_age_calendar = self.results.get('corrected_age_calendar')
            if corrected_age_years is not None:
                age_text += f"\nCorrected Age: {corrected_age_years:.2f} years"
                if corrected_age_calendar and isinstance(corrected_age_calendar, dict):
                    years = corrected_age_calendar.get('years', 0)
                    months = corrected_age_calendar.get('months', 0)
                    days = corrected_age_calendar.get('days', 0)
                    age_text += f" ({years}y {months}m {days}d)"

        patient_table_data = [
            ['Sex:', sex_display],
            ['Date of Birth:', birth_date],
            ['Age:', age_text],
            ['Measurement Date:', measurement_date]
        ]

        patient_table = Table(patient_table_data, colWidths=[4*cm, 12*cm])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        elements.append(patient_table)
        elements.append(Spacer(1, 0.5*cm))

        return elements

    def _create_measurements_section(self):
        """Create measurements table section"""
        elements = []

        # Section heading
        heading = Paragraph("MEASUREMENTS", self.styles['SectionHeading'])
        elements.append(heading)
        elements.append(Spacer(1, 0.3*cm))

        # Build measurements table
        table_data = [['Parameter', 'Value', 'Centile', 'SDS']]

        # Weight - access directly from results, not from measurements sub-dict
        weight = self.results.get('weight')
        if weight and isinstance(weight, dict):
            table_data.append([
                'Weight',
                f"{weight.get('value', 'N/A')} kg",
                f"{weight.get('centile', 'N/A')}%",
                f"{weight.get('sds', 'N/A')}"
            ])

        # Height
        height = self.results.get('height')
        if height and isinstance(height, dict):
            table_data.append([
                'Height',
                f"{height.get('value', 'N/A')} cm",
                f"{height.get('centile', 'N/A')}%",
                f"{height.get('sds', 'N/A')}"
            ])

        # BMI
        bmi = self.results.get('bmi')
        if bmi and isinstance(bmi, dict):
            table_data.append([
                'BMI',
                f"{bmi.get('value', 'N/A')}",
                f"{bmi.get('centile', 'N/A')}%",
                f"{bmi.get('sds', 'N/A')}"
            ])

        # OFC
        ofc = self.results.get('ofc')
        if ofc and isinstance(ofc, dict):
            table_data.append([
                'OFC',
                f"{ofc.get('value', 'N/A')} cm",
                f"{ofc.get('centile', 'N/A')}%",
                f"{ofc.get('sds', 'N/A')}"
            ])

        # Create table
        measurements_table = Table(table_data, colWidths=[4*cm, 3.5*cm, 3.5*cm, 3*cm])
        measurements_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data rows
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),

            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(measurements_table)
        elements.append(Spacer(1, 0.5*cm))

        return elements

    def _create_additional_parameters_section(self):
        """Create additional parameters section"""
        elements = []

        # Check if there are any additional parameters
        has_params = False
        params_list = []

        # Height velocity
        height_velocity = self.results.get('height_velocity')
        if height_velocity and isinstance(height_velocity, dict):
            hv_cm = height_velocity.get('height_velocity_cm_year')
            if hv_cm is not None:
                has_params = True
                params_list.append(f"Height Velocity: {hv_cm:.2f} cm/year")

        # BSA - stored as float value with separate method field
        bsa = self.results.get('bsa')
        bsa_method = self.results.get('bsa_method')
        if bsa is not None and isinstance(bsa, (int, float)):
            has_params = True
            method_str = f" ({bsa_method})" if bsa_method else ""
            params_list.append(f"BSA{method_str}: {bsa:.2f} m²")

        # GH Dose - stored as dict with various fields
        gh_dose = self.results.get('gh_dose')
        if gh_dose and isinstance(gh_dose, dict):
            daily_dose = gh_dose.get('daily_dose_mg')
            if daily_dose is not None:
                has_params = True
                params_list.append(f"GH Dose: {daily_dose:.2f} mg/day")
                # Optionally include other formats
                weekly_dose = gh_dose.get('weekly_dose_mg_m2')
                if weekly_dose:
                    params_list.append(f"  ({weekly_dose:.1f} mg/m²/week)")

        # MPH - stored under 'mid_parental_height' key
        mph = self.results.get('mid_parental_height')
        if mph and isinstance(mph, dict):
            mph_value = mph.get('mid_parental_height')
            if mph_value is not None:
                has_params = True
                mph_text = f"Mid-Parental Height: {mph_value:.1f} cm"
                target_min = mph.get('target_range_lower')
                target_max = mph.get('target_range_upper')
                if target_min is not None and target_max is not None:
                    mph_text += f" (Target Range: {target_min:.1f}-{target_max:.1f} cm)"
                params_list.append(mph_text)

        if not has_params:
            return elements

        # Section heading
        heading = Paragraph("ADDITIONAL PARAMETERS", self.styles['SectionHeading'])
        elements.append(heading)
        elements.append(Spacer(1, 0.3*cm))

        # Parameters list
        for param in params_list:
            param_text = f"• {param}"
            param_para = Paragraph(param_text, self.styles['CustomNormal'])
            elements.append(param_para)
            elements.append(Spacer(1, 0.2*cm))

        elements.append(Spacer(1, 0.3*cm))

        return elements

    def _create_charts_section(self):
        """Create growth charts section"""
        elements = []

        if not self.chart_images:
            return elements

        # Section heading
        heading = Paragraph("GROWTH CHARTS", self.styles['SectionHeading'])
        elements.append(heading)
        elements.append(Spacer(1, 0.3*cm))

        # Add each chart image
        for chart_type, base64_image in self.chart_images.items():
            if not base64_image:
                continue

            try:
                # Decode base64 image
                # Remove data:image/png;base64, prefix if present
                if ',' in base64_image:
                    base64_image = base64_image.split(',')[1]

                image_data = base64.b64decode(base64_image)
                image_buffer = BytesIO(image_data)

                # Open with PIL to get dimensions
                pil_image = PILImage.open(image_buffer)
                img_width, img_height = pil_image.size

                # Reset buffer position
                image_buffer.seek(0)

                # Calculate scaling to fit page width (with margins)
                max_width = 15 * cm
                max_height = 10 * cm

                aspect = img_height / img_width

                if img_width > max_width:
                    display_width = max_width
                    display_height = max_width * aspect
                else:
                    display_width = img_width * 0.02645833  # pixels to cm (approximately)
                    display_height = img_height * 0.02645833

                if display_height > max_height:
                    display_height = max_height
                    display_width = max_height / aspect

                # Create chart title
                chart_title = chart_type.replace('_', ' ').title() + " Chart"
                title_para = Paragraph(f"<b>{chart_title}</b>", self.styles['CustomNormal'])
                elements.append(title_para)
                elements.append(Spacer(1, 0.2*cm))

                # Add image
                img = Image(image_buffer, width=display_width, height=display_height)
                elements.append(img)
                elements.append(Spacer(1, 0.5*cm))

            except Exception as e:
                # Skip problematic images
                error_text = f"<i>Error loading {chart_type} chart: {str(e)}</i>"
                error_para = Paragraph(error_text, self.styles['CustomNormal'])
                elements.append(error_para)
                elements.append(Spacer(1, 0.3*cm))

        return elements

    def _create_warnings_section(self):
        """Create warnings section"""
        elements = []

        warnings = self.results.get('warnings', [])
        if not warnings:
            return elements

        # Section heading
        heading = Paragraph("WARNINGS", self.styles['SectionHeading'])
        elements.append(heading)
        elements.append(Spacer(1, 0.3*cm))

        # Warning items
        for warning in warnings:
            warning_text = f"⚠ {warning}"
            warning_para = Paragraph(warning_text, self.styles['Warning'])
            elements.append(warning_para)
            elements.append(Spacer(1, 0.2*cm))

        elements.append(Spacer(1, 0.3*cm))

        return elements

    def _create_footer(self):
        """Create report footer"""
        elements = []

        elements.append(Spacer(1, 1*cm))

        disclaimer_text = """
        <i>This report is generated by the Growth Parameters Calculator using the RCPCH Growth Charts API.
        All calculations should be verified and interpreted by qualified healthcare professionals.
        This tool is for clinical decision support and should not replace clinical judgment.</i>
        """

        disclaimer = Paragraph(disclaimer_text, self.styles['Footer'])
        elements.append(disclaimer)

        return elements

    def generate(self):
        """
        Generate the PDF report.

        Returns:
            BytesIO: Buffer containing the PDF document
        """
        # Create document
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title="Growth Parameters Report"
        )

        # Build story
        story = []

        # Add sections
        story.extend(self._create_header())
        story.extend(self._create_patient_info_section())
        story.extend(self._create_measurements_section())
        story.extend(self._create_additional_parameters_section())
        story.extend(self._create_warnings_section())
        story.extend(self._create_charts_section())
        story.extend(self._create_footer())

        # Build PDF
        doc.build(story, canvasmaker=NumberedCanvas)

        # Reset buffer position to beginning
        self.buffer.seek(0)

        return self.buffer
