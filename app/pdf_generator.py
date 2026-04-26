from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(BASE_DIR, 'fonts')

pdfmetrics.registerFont(TTFont('NanumGothic', os.path.join(FONT_PATH, 'NanumGothic.ttf')))
pdfmetrics.registerFont(TTFont('NanumGothicBold', os.path.join(FONT_PATH, 'NanumGothicBold.ttf')))

def generate_evidence_pdf(
    image_bytes: bytes,
    hash_value: str,
    timestamp: str,
    latitude: float | None,
    longitude: float | None,
    confidence: float,
    damage_score: float,
    detected: bool
) -> bytes:

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    elements = []

    # 스타일 정의
    title_style = ParagraphStyle(
        'Title',
        fontName='NanumGothicBold',
        fontSize=20,
        alignment=1,
        spaceAfter=6
    )
    normal_style = ParagraphStyle(
        'Normal',
        fontName='NanumGothic',
        fontSize=10,
        spaceAfter=4
    )
    bold_style = ParagraphStyle(
        'Bold',
        fontName='NanumGothicBold',
        fontSize=10,
        spaceAfter=4
    )
    small_style = ParagraphStyle(
        'Small',
        fontName='NanumGothic',
        fontSize=8,
        spaceAfter=4
    )

    # 제목
    elements.append(Paragraph('Road-Insight 도로 파손 증거 리포트', title_style))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph('AI 기반 도로 파손 탐지 공식 증거 문서', normal_style))
    elements.append(Spacer(1, 0.3*cm))

    # 구분선
    elements.append(Table(
        [['']],
        colWidths=[17*cm],
        style=TableStyle([
            ('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor('#1D9E75')),
        ])
    ))
    elements.append(Spacer(1, 0.3*cm))

    # 탐지 결과
    result_text = '포트홀 감지됨' if detected else '포트홀 미감지'
    result_color = '#A32D2D' if detected else '#085041'
    elements.append(Paragraph(f'<font color="{result_color}"><b>탐지 결과: {result_text}</b></font>', bold_style))
    elements.append(Spacer(1, 0.3*cm))

    # 분석 정보 테이블
    analysis_data = [
        ['항목', '내용'],
        ['AI 신뢰도', f'{confidence * 100:.1f}%'],
        ['위험도 점수', f'{damage_score:.1f} / 100'],
        ['분석 시각', timestamp],
        ['GPS 위도', str(latitude) if latitude else '없음'],
        ['GPS 경도', str(longitude) if longitude else '없음'],
    ]

    analysis_table = Table(
        analysis_data,
        colWidths=[5*cm, 12*cm],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1D9E75')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'NanumGothicBold'),
            ('FONTNAME', (0,1), (-1,-1), 'NanumGothic'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F0F0F0')]),
            ('PADDING', (0,0), (-1,-1), 8),
        ])
    )
    elements.append(analysis_table)
    elements.append(Spacer(1, 0.5*cm))

    # 촬영 이미지
    elements.append(Paragraph('촬영 이미지', bold_style))
    elements.append(Spacer(1, 0.3*cm))
    img_buffer = io.BytesIO(image_bytes)
    img = Image(img_buffer, width=12*cm, height=8*cm)
    elements.append(img)
    elements.append(Spacer(1, 0.5*cm))

    # 무결성 검증
    elements.append(Paragraph('무결성 검증', bold_style))
    elements.append(Spacer(1, 0.3*cm))

    integrity_data = [
        ['항목', '내용'],
        ['SHA-256 해시', hash_value[:32] + '...'],
        ['전체 해시값', hash_value],
        ['타임스탬프', timestamp],
    ]

    integrity_table = Table(
        integrity_data,
        colWidths=[5*cm, 12*cm],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1D9E75')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'NanumGothicBold'),
            ('FONTNAME', (0,1), (-1,-1), 'NanumGothic'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F0F0F0')]),
            ('PADDING', (0,0), (-1,-1), 8),
        ])
    )
    elements.append(integrity_table)
    elements.append(Spacer(1, 0.5*cm))

    # 면책 조항
    elements.append(Table(
        [['']],
        colWidths=[17*cm],
        style=TableStyle([
            ('LINEABOVE', (0,0), (-1,0), 0.5, colors.grey),
        ])
    ))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(
        '본 리포트는 AI 분석 결과이며 참고용입니다. '
        '법적 효력은 공인 타임스탬프에 의합니다. '
        'SHA-256 해시값으로 원본 이미지 위변조 여부를 검증할 수 있습니다.',
        small_style
    ))

    doc.build(elements)
    return buffer.getvalue()
