import io
import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle, KeepTogether,
)
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Rect


PURPLE      = colors.HexColor('#6C63FF')
DARK_PURPLE = colors.HexColor('#4C1D95')
LIGHT_BG    = colors.HexColor('#F5F3FF')
DARK        = colors.HexColor('#1A1A2E')
GRAY        = colors.HexColor('#6B7280')
GREEN       = colors.HexColor('#059669')
RED         = colors.HexColor('#EF4444')
WHITE       = colors.white


def s(name, **kwargs):
    return ParagraphStyle(name, **kwargs)


def make_score_bar(score, max_score=10, width=120*mm, height=6*mm):
    d = Drawing(width, height)
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor('#E5E7EB'), strokeColor=None))
    fill_w = (score / max_score) * width
    bar_color = (PURPLE if score >= 6
                 else colors.HexColor('#F59E0B') if score >= 4
                 else RED)
    d.add(Rect(0, 0, fill_w, height, fillColor=bar_color, strokeColor=None))
    return d


def extract_score(evaluation_text: str):
    match = re.search(r'Score[:\s]+(\d+)\s*/\s*10', evaluation_text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def calculate_grade(evaluations: dict):
    scores = []
    for v in evaluations.values():
        sc = extract_score(v.get("evaluation", ""))
        if sc is not None:
            scores.append(sc)
    if not scores:
        return "N/A", 0
    avg = sum(scores) / len(scores)
    grade = "A" if avg >= 8 else "B" if avg >= 6 else "C" if avg >= 4 else "D"
    return grade, round(avg, 1)


def build_pdf_report(
    result: dict,
    questions: list,
    evaluations: dict,
    candidate_name: str = "",
    job_role: str = "",
    roadmap: list = [],
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=18*mm, leftMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm,
    )

    title_s    = s('T',   fontSize=22, fontName='Helvetica-Bold', textColor=PURPLE,      alignment=1, spaceAfter=2)
    subtitle_s = s('ST',  fontSize=11, fontName='Helvetica',      textColor=GRAY,        alignment=1, spaceAfter=2)
    section_s  = s('SEC', fontSize=13, fontName='Helvetica-Bold', textColor=DARK_PURPLE, spaceBefore=10, spaceAfter=5)
    q_label_s  = s('QL',  fontSize=10, fontName='Helvetica-Bold', textColor=PURPLE,      spaceAfter=2)
    q_text_s   = s('QT',  fontSize=11, fontName='Helvetica-Bold', textColor=DARK,        spaceAfter=4, leading=16)
    body_s     = s('B',   fontSize=10, fontName='Helvetica',      textColor=DARK,        spaceAfter=3, leading=14)
    label_s    = s('L',   fontSize=10, fontName='Helvetica-Bold', textColor=DARK_PURPLE, spaceAfter=2)
    eval_s     = s('E',   fontSize=10, fontName='Helvetica',      textColor=DARK,        spaceAfter=3, leading=14,
                   backColor=LIGHT_BG, borderPadding=(6, 8, 6, 8))
    na_s       = s('NA',  fontSize=10, fontName='Helvetica-Oblique', textColor=GRAY)
    summary_s  = s('SUM', fontSize=11, fontName='Helvetica-Bold', textColor=GREEN,       alignment=1)
    footer_s   = s('F',   fontSize=8,  fontName='Helvetica',      textColor=GRAY,        alignment=1)

    story = []
    # Convert evaluations keys to ints if they are strings
    evals = {}
    for k, v in evaluations.items():
        try:
            evals[int(k)] = v
        except Exception:
            evals[k] = v

    grade, avg_score = calculate_grade(evals)

    story.append(Paragraph("SkillBridge AI", title_s))
    story.append(Paragraph("AI Mock Interview Evaluation Report", subtitle_s))
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=2.5, color=PURPLE))
    story.append(Spacer(1, 5*mm))

    info_data = [
        ["Candidate Name", candidate_name or "Not provided",  "Report Date", datetime.now().strftime('%d %b %Y')],
        ["Target Job Role", job_role or "Not provided",       "Report Time", datetime.now().strftime('%I:%M %p')],
        ["Total Questions", str(len(questions)),              "Evaluated",   f"{len(evals)} / {len(questions)}"],
    ]
    info_table = Table(info_data, colWidths=[38*mm, 60*mm, 30*mm, 42*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME',    (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME',    (0,0), (0,-1),  'Helvetica-Bold'),
        ('FONTNAME',    (2,0), (2,-1),  'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 9),
        ('TEXTCOLOR',   (0,0), (0,-1),  PURPLE),
        ('TEXTCOLOR',   (2,0), (2,-1),  PURPLE),
        ('TEXTCOLOR',   (1,0), (1,-1),  DARK),
        ('TEXTCOLOR',   (3,0), (3,-1),  DARK),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [LIGHT_BG, WHITE]),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 6),
        ('TOPPADDING',     (0,0), (-1,-1), 6),
        ('LEFTPADDING',    (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#E5E7EB')),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 6*mm))

    # Compatibility Score
    story.append(Paragraph("Compatibility Score", section_s))
    compat_score = result.get('compatibility_score', 0)
    try:
        compat_val = int(str(compat_score).replace('%', '').strip())
    except Exception:
        compat_val = 0
    compat_data = [[
        Paragraph(f"<b>{compat_val}%</b>", s('CS', fontSize=18, fontName='Helvetica-Bold', textColor=PURPLE, alignment=1)),
        make_score_bar(compat_val, 100, width=115*mm, height=8*mm),
        Paragraph("Job Fit", s('JF', fontSize=9, fontName='Helvetica', textColor=GRAY, alignment=1))
    ]]
    compat_table = Table(compat_data, colWidths=[20*mm, 120*mm, 20*mm])
    compat_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 4)]))
    story.append(compat_table)
    story.append(Spacer(1, 6*mm))

    # Overall Grade
    story.append(Paragraph("Overall Interview Performance", section_s))
    grade_color = GREEN if grade == 'A' else PURPLE if grade == 'B' else colors.HexColor('#F59E0B') if grade == 'C' else RED
    grade_data = [[
        Paragraph(str(grade), s('GG', fontSize=36, fontName='Helvetica-Bold', textColor=grade_color, alignment=1)),
        Paragraph(f"Average Score<br/><b>{avg_score} / 10</b>",
                  s('AVG', fontSize=12, fontName='Helvetica', textColor=DARK, alignment=1, leading=18)),
        Paragraph("A = Excellent (8-10)<br/>B = Good (6-7)<br/>C = Average (4-5)<br/>D = Needs Work (0-3)",
                  s('GL', fontSize=9, fontName='Helvetica', textColor=GRAY, leading=14))
    ]]
    grade_table = Table(grade_data, colWidths=[30*mm, 60*mm, 80*mm])
    grade_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (0,0), LIGHT_BG),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#E5E7EB')),
    ]))
    story.append(grade_table)
    story.append(Spacer(1, 6*mm))

    # Skills
    matched = result.get('matched_skills', [])
    missing = result.get('missing_skills', [])
    story.append(Paragraph("Skills Analysis", section_s))
    max_rows = max(len(matched), len(missing), 1)
    skills_data = [["Matched Skills", "Missing Skills"]]
    for idx in range(max_rows):
        skills_data.append([
            matched[idx] if idx < len(matched) else "",
            missing[idx] if idx < len(missing) else ""
        ])
    skills_table = Table(skills_data, colWidths=[85*mm, 85*mm])
    skills_table.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',  (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (0,0),   GREEN),
        ('TEXTCOLOR', (1,0), (1,0),   RED),
        ('TEXTCOLOR', (0,1), (0,-1),  DARK),
        ('TEXTCOLOR', (1,1), (1,-1),  DARK),
        ('BACKGROUND',     (0,0), (-1,0),  LIGHT_BG),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, colors.HexColor('#FAFAFA')]),
        ('GRID',          (0,0), (-1,-1),  0.3, colors.HexColor('#E5E7EB')),
        ('BOTTOMPADDING', (0,0), (-1,-1),  5),
        ('TOPPADDING',    (0,0), (-1,-1),  5),
        ('LEFTPADDING',   (0,0), (-1,-1),  8),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 6*mm))

    # Per-question scores
    if evals:
        story.append(Paragraph("Score Per Question", section_s))
        chart_data = [["Question", "Score", "Visual"]]
        for i, question in enumerate(questions, start=1):
            if i in evals:
                sc = extract_score(evals[i]["evaluation"]) or 0
                chart_data.append([f"Q{i}", f"{sc}/10", make_score_bar(sc, 10, width=80*mm, height=5*mm)])
            else:
                chart_data.append([f"Q{i}", "N/A", Paragraph("Not attempted", na_s)])
        chart_table = Table(chart_data, colWidths=[15*mm, 20*mm, 135*mm])
        chart_table.setStyle(TableStyle([
            ('FONTNAME',   (0,0), (-1,0),  'Helvetica-Bold'),
            ('FONTSIZE',   (0,0), (-1,-1), 9),
            ('TEXTCOLOR',  (0,0), (-1,0),  WHITE),
            ('BACKGROUND', (0,0), (-1,0),  PURPLE),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT_BG, WHITE]),
            ('GRID',  (0,0), (-1,-1), 0.3, colors.HexColor('#E5E7EB')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING',    (0,0), (-1,-1), 5),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ]))
        story.append(chart_table)
        story.append(Spacer(1, 6*mm))

    # Detailed evaluation
    story.append(HRFlowable(width="100%", thickness=1.5, color=PURPLE))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("Detailed Interview Evaluation", section_s))
    story.append(Spacer(1, 2*mm))

    for i, question in enumerate(questions, start=1):
        block = []
        block.append(Paragraph(f"Question {i} of {len(questions)}", q_label_s))
        block.append(Paragraph(question, q_text_s))
        if i in evals:
            data = evals[i]
            sc = extract_score(data["evaluation"])
            if sc is not None:
                score_row = [[
                    Paragraph(f"<b>Score: {sc}/10</b>", s('SB', fontSize=10, fontName='Helvetica-Bold',
                              textColor=PURPLE, alignment=1)),
                    make_score_bar(sc, 10, width=110*mm, height=5*mm)
                ]]
                score_t = Table(score_row, colWidths=[30*mm, 115*mm])
                score_t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 4)]))
                block.append(score_t)
                block.append(Spacer(1, 2*mm))
            block.append(Paragraph("Your Answer:", label_s))
            ans_clean = data['answer'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            block.append(Paragraph(ans_clean, body_s))
            block.append(Spacer(1, 2*mm))
            block.append(Paragraph("AI Evaluation:", label_s))
            clean_eval = (data['evaluation'].replace('*', '').replace('#', '')
                          .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            block.append(Paragraph(clean_eval, eval_s))
        else:
            block.append(Paragraph("This question was not attempted.", na_s))
        block.append(Spacer(1, 3*mm))
        block.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E5E7EB')))
        block.append(Spacer(1, 3*mm))
        story.append(KeepTogether(block))

    # Roadmap
    if roadmap:
        story.append(HRFlowable(width="100%", thickness=1.5, color=PURPLE))
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph("Learning Roadmap", section_s))
        desc_style = s('RD', fontSize=9, fontName='Helvetica', textColor=DARK, leading=13, wordWrap='CJK')
        roadmap_data = [[
            Paragraph("<b>Week</b>", s('RH1', fontSize=9, fontName='Helvetica-Bold', textColor=WHITE)),
            Paragraph("<b>Skill</b>", s('RH2', fontSize=9, fontName='Helvetica-Bold', textColor=WHITE)),
            Paragraph("<b>Description</b>", s('RH3', fontSize=9, fontName='Helvetica-Bold', textColor=WHITE)),
        ]]
        for item in roadmap:
            ds = s('RD2', fontSize=9, fontName='Helvetica', textColor=DARK, leading=13, wordWrap='CJK')
            roadmap_data.append([
                Paragraph(item.get('week', ''), ds),
                Paragraph(item.get('skill', ''), ds),
                Paragraph(item.get('description', ''), ds),
            ])
        roadmap_table = Table(roadmap_data, colWidths=[22*mm, 48*mm, 104*mm])
        roadmap_table.setStyle(TableStyle([
            ('FONTNAME',   (0,0), (-1,0),  'Helvetica-Bold'),
            ('FONTSIZE',   (0,0), (-1,-1), 9),
            ('TEXTCOLOR',  (0,0), (-1,0),  WHITE),
            ('BACKGROUND', (0,0), (-1,0),  PURPLE),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT_BG, WHITE]),
            ('GRID',  (0,0), (-1,-1), 0.3, colors.HexColor('#E5E7EB')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ]))
        story.append(roadmap_table)
        story.append(Spacer(1, 6*mm))

    story.append(HRFlowable(width="100%", thickness=2, color=PURPLE))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        f"Completed {len(evals)}/{len(questions)} questions  |  Grade: {grade}  |  Avg Score: {avg_score}/10",
        summary_s
    ))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("Generated by SkillBridge AI — Powered by Gemini 2.5 Flash", footer_s))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
