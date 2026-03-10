import streamlit as st
import speech_recognition as sr
from datetime import datetime
import time
import io
import json
import re
from ai_engine import gemini_call, parse_json, evaluate_answer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, KeepTogether
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Rect


def record_voice():
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 2.0
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    with sr.Microphone() as source:
        st.info("🎤 Speak now... (pause when done)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=120)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand audio. Please try again."
    except sr.RequestError as e:
        return f"Speech recognition service error: {e}"
    except sr.WaitTimeoutError:
        return "No speech detected. Please try again."


def extract_score(evaluation_text):
    match = re.search(r'Score[:\s]+(\d+)\s*/\s*10', evaluation_text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def calculate_grade(evaluations):
    scores = [extract_score(d["evaluation"]) for d in evaluations.values()
              if extract_score(d["evaluation"]) is not None]
    if not scores:
        return "N/A", 0
    avg = sum(scores) / len(scores)
    grade = "A" if avg >= 8 else "B" if avg >= 6 else "C" if avg >= 4 else "D"
    return grade, round(avg, 1)


def make_score_bar(score, max_score=10, width=120*mm, height=6*mm):
    d = Drawing(width, height)
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor('#E5E7EB'), strokeColor=None))
    fill_width = (score / max_score) * width
    bar_color = (colors.HexColor('#6C63FF') if score >= 6
                 else colors.HexColor('#F59E0B') if score >= 4
                 else colors.HexColor('#EF4444'))
    d.add(Rect(0, 0, fill_width, height, fillColor=bar_color, strokeColor=None))
    return d


def build_pdf_report(result, questions, evaluations, candidate_name, job_role):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=18*mm, leftMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm
    )

    PURPLE      = colors.HexColor('#6C63FF')
    DARK_PURPLE = colors.HexColor('#4C1D95')
    LIGHT_BG    = colors.HexColor('#F5F3FF')
    DARK        = colors.HexColor('#1A1A2E')
    GRAY        = colors.HexColor('#6B7280')
    GREEN       = colors.HexColor('#059669')
    RED         = colors.HexColor('#EF4444')
    WHITE       = colors.white

    def style(name, **kwargs):
        return ParagraphStyle(name, **kwargs)

    title_s    = style('T',   fontSize=22, fontName='Helvetica-Bold', textColor=PURPLE,      alignment=1, spaceAfter=2)
    subtitle_s = style('ST',  fontSize=11, fontName='Helvetica',      textColor=GRAY,        alignment=1, spaceAfter=2)
    section_s  = style('SEC', fontSize=13, fontName='Helvetica-Bold', textColor=DARK_PURPLE, spaceBefore=10, spaceAfter=5)
    q_label_s  = style('QL',  fontSize=10, fontName='Helvetica-Bold', textColor=PURPLE,      spaceAfter=2)
    q_text_s   = style('QT',  fontSize=11, fontName='Helvetica-Bold', textColor=DARK,        spaceAfter=4, leading=16)
    body_s     = style('B',   fontSize=10, fontName='Helvetica',      textColor=DARK,        spaceAfter=3, leading=14)
    label_s    = style('L',   fontSize=10, fontName='Helvetica-Bold', textColor=DARK_PURPLE, spaceAfter=2)
    eval_s     = style('E',   fontSize=10, fontName='Helvetica',      textColor=DARK,        spaceAfter=3, leading=14,
                       backColor=LIGHT_BG, borderPadding=(6, 8, 6, 8))
    na_s       = style('NA',  fontSize=10, fontName='Helvetica-Oblique', textColor=GRAY)
    summary_s  = style('SUM', fontSize=11, fontName='Helvetica-Bold', textColor=GREEN,       alignment=1)
    footer_s   = style('F',   fontSize=8,  fontName='Helvetica',      textColor=GRAY,        alignment=1)

    story = []
    grade, avg_score = calculate_grade(evaluations)

    story.append(Paragraph("SkillBridge AI", title_s))
    story.append(Paragraph("AI Mock Interview Evaluation Report", subtitle_s))
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=2.5, color=PURPLE))
    story.append(Spacer(1, 5*mm))

    info_data = [
        ["Candidate Name", candidate_name or "Not provided",  "Report Date", datetime.now().strftime('%d %b %Y')],
        ["Target Job Role", job_role or "Not provided",       "Report Time", datetime.now().strftime('%I:%M %p')],
        ["Total Questions", str(len(questions)),              "Evaluated",   f"{len(evaluations)} / {len(questions)}"],
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

    story.append(Paragraph("Compatibility Score", section_s))
    compat_score = result.get('compatibility_score', 0)
    try:
        compat_val = int(str(compat_score).replace('%', '').strip())
    except:
        compat_val = 0
    compat_data = [[
        Paragraph(f"<b>{compat_val}%</b>", style('CS', fontSize=18, fontName='Helvetica-Bold', textColor=PURPLE, alignment=1)),
        make_score_bar(compat_val, 100, width=115*mm, height=8*mm),
        Paragraph("Job Fit", style('JF', fontSize=9, fontName='Helvetica', textColor=GRAY, alignment=1))
    ]]
    compat_table = Table(compat_data, colWidths=[20*mm, 120*mm, 20*mm])
    compat_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 4)]))
    story.append(compat_table)
    story.append(Spacer(1, 6*mm))

    story.append(Paragraph("Overall Interview Performance", section_s))
    grade_color = GREEN if grade == 'A' else PURPLE if grade == 'B' else colors.HexColor('#F59E0B') if grade == 'C' else RED
    grade_data = [[
        Paragraph(grade, style('GG', fontSize=36, fontName='Helvetica-Bold', textColor=grade_color, alignment=1)),
        Paragraph(f"Average Score<br/><b>{avg_score} / 10</b>",
                  style('AVG', fontSize=12, fontName='Helvetica', textColor=DARK, alignment=1, leading=18)),
        Paragraph("A = Excellent (8-10)<br/>B = Good (6-7)<br/>C = Average (4-5)<br/>D = Needs Work (0-3)",
                  style('GL', fontSize=9, fontName='Helvetica', textColor=GRAY, leading=14))
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

    if evaluations:
        story.append(Paragraph("Score Per Question", section_s))
        chart_data = [["Question", "Score", "Visual"]]
        for i, question in enumerate(questions, start=1):
            if i in evaluations:
                sc = extract_score(evaluations[i]["evaluation"]) or 0
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

    story.append(HRFlowable(width="100%", thickness=1.5, color=PURPLE))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("Detailed Interview Evaluation", section_s))
    story.append(Spacer(1, 2*mm))

    for i, question in enumerate(questions, start=1):
        block = []
        block.append(Paragraph(f"Question {i} of {len(questions)}", q_label_s))
        block.append(Paragraph(question, q_text_s))
        if i in evaluations:
            data = evaluations[i]
            sc = extract_score(data["evaluation"])
            if sc is not None:
                score_row = [[
                    Paragraph(f"<b>Score: {sc}/10</b>", style('SB', fontSize=10, fontName='Helvetica-Bold',
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

    roadmap = st.session_state.get("roadmap", [])
    if roadmap:
        story.append(HRFlowable(width="100%", thickness=1.5, color=PURPLE))
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph("Learning Roadmap", section_s))
        desc_style = style('RD', fontSize=9, fontName='Helvetica', textColor=DARK, leading=13, wordWrap='CJK')
        roadmap_data = [[
            Paragraph("<b>Week</b>", style('RH1', fontSize=9, fontName='Helvetica-Bold', textColor=WHITE)),
            Paragraph("<b>Skill</b>", style('RH2', fontSize=9, fontName='Helvetica-Bold', textColor=WHITE)),
            Paragraph("<b>Description</b>", style('RH3', fontSize=9, fontName='Helvetica-Bold', textColor=WHITE)),
        ]]
        for item in roadmap:
            desc_style2 = style('RD2', fontSize=9, fontName='Helvetica', textColor=DARK, leading=13, wordWrap='CJK')
            roadmap_data.append([
                Paragraph(item.get('week', ''), desc_style2),
                Paragraph(item.get('skill', ''), desc_style2),
                Paragraph(item.get('description', ''), desc_style2),
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
        f"Completed {len(evaluations)}/{len(questions)} questions  |  Grade: {grade}  |  Avg Score: {avg_score}/10",
        summary_s
    ))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("Generated by SkillBridge AI — Powered by Gemini 2.5 Flash", footer_s))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def show_mock_interview():

    st.markdown("<h2 style='color:#1A1A2E;'>🎤 AI Smart Mock Interview</h2>", unsafe_allow_html=True)

    if "result" not in st.session_state:
        st.warning("⚠️ Run Resume Analysis first.")
        return

    result         = st.session_state["result"]
    matched_skills = result.get("matched_skills", [])
    missing_skills = result.get("missing_skills", [])

    if "mock_questions" not in st.session_state:
        with st.spinner("🤖 Generating interview questions based on your skills..."):
            prompt = f"""
You are a senior technical interviewer. Generate exactly 5 smart interview questions
based on the candidate's matched and missing skills.

Return ONLY valid JSON — no markdown, no extra text.

Format:
{{
    "mock_questions": ["Q1?", "Q2?", "Q3?", "Q4?", "Q5?"]
}}

Matched Skills: {json.dumps(matched_skills)}
Missing Skills: {json.dumps(missing_skills)}
"""
            raw, err = gemini_call(prompt)
            if err:
                st.error(f"❌ {err}")
                return
            data, err = parse_json(raw)
            if err:
                st.error(f"❌ {err}")
                return
            st.session_state["mock_questions"] = data.get("mock_questions", [])

    questions = st.session_state.get("mock_questions", [])

    if not questions:
        st.error("❌ Could not generate questions. Please try again.")
        if st.button("🔄 Retry", use_container_width=True):
            st.session_state.pop("mock_questions", None)
            st.rerun()
        return

    st.metric("Compatibility Score", f"{result.get('compatibility_score', 'N/A')}%")
    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("👤 Enter Your Info for PDF Report", expanded=False):
        candidate_name = st.text_input("Your Name", placeholder="e.g. Rakasri L", key="candidate_name")
        job_role       = st.text_input("Target Job Role", placeholder="e.g. Backend Developer", key="job_role")

    if st.button("🔄 Generate New Questions", use_container_width=False):
        st.session_state.pop("mock_questions", None)
        st.session_state.pop("evaluations", None)
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if "evaluations" not in st.session_state:
        st.session_state["evaluations"] = {}

    for i, question in enumerate(questions, start=1):
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.6);backdrop-filter:blur(12px);
            -webkit-backdrop-filter:blur(12px);border:1px solid rgba(108,99,255,0.18);
            border-radius:16px;padding:24px 28px;margin-bottom:8px;
            box-shadow:0 4px 16px rgba(108,99,255,0.07);'>
            <div style='font-size:13px;font-weight:600;color:#6C63FF;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:8px;'>Question {i} of {len(questions)}</div>
            <div style='font-size:16px;font-weight:600;color:#1A1A2E;line-height:1.5;'>{question}</div>
        </div>
        """, unsafe_allow_html=True)

        mode = st.radio("Answer Mode", ["Type Answer", "Voice Answer"], key=f"mode_{i}", horizontal=True)
        user_answer = ""

        if mode == "Type Answer":
            user_answer = st.text_area("✍️ Your Answer", placeholder="Type your answer here...",
                                       height=150, key=f"text_{i}")
            user_answer = st.session_state.get(f"text_{i}", "")
        else:
            if f"voice_text_{i}" not in st.session_state:
                st.session_state[f"voice_text_{i}"] = ""
            if st.button(f"🎤 Record Voice for Q{i}", key=f"voice_{i}"):
                recognized = record_voice()
                st.session_state[f"voice_text_{i}"] = recognized
            user_answer = st.text_area("📝 Recognized Answer", height=150, key=f"voice_text_{i}")

        if st.button(f"🚀 Evaluate Answer Q{i}", key=f"eval_{i}", use_container_width=True):
            if not user_answer:
                st.warning("⚠️ Please provide an answer first.")
            else:
                with st.spinner("🤖 Evaluating with Gemini AI..."):
                    evaluation = evaluate_answer(question, user_answer)
                st.session_state["evaluations"][i] = {
                    "question":   question,
                    "answer":     user_answer,
                    "evaluation": evaluation
                }

        if i in st.session_state["evaluations"]:
            eval_data = st.session_state["evaluations"][i]
            sc = extract_score(eval_data["evaluation"])
            st.markdown(f"""
            <div style='background:rgba(108,99,255,0.06);border:1px solid rgba(108,99,255,0.2);
                border-radius:14px;padding:20px 24px;margin-top:12px;'>
                <div style='font-size:15px;font-weight:700;color:#4C1D95;margin-bottom:10px;'>
                    📊 AI Evaluation {"— Score: " + str(sc) + "/10" if sc else ""}
                </div>
                <div style='color:#1A1A2E;font-size:14px;line-height:1.7;white-space:pre-wrap;'>
                    {eval_data["evaluation"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    st.divider()

    evaluated_count  = len(st.session_state.get("evaluations", {}))
    grade, avg_score = calculate_grade(st.session_state.get("evaluations", {}))

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Evaluated",     f"{evaluated_count}/{len(questions)}")
    col_b.metric("Avg Score",     f"{avg_score}/10")
    col_c.metric("Overall Grade", grade)

    if evaluated_count < len(questions):
        st.warning(f"⚠️ {len(questions) - evaluated_count} question(s) not yet evaluated.")

    st.markdown("<br>", unsafe_allow_html=True)

    cname = st.session_state.get("candidate_name", "")
    jrole = st.session_state.get("job_role", "")

    st.download_button(
        "📥 Download PDF Report",
        build_pdf_report(result, questions, st.session_state["evaluations"], cname, jrole),
        f"SkillBridge_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        "application/pdf",
        use_container_width=True
    )
    

    

    

