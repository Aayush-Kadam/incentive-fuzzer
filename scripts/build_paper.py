"""Render the canonical Markdown research-preview manuscript to a review PDF."""
from pathlib import Path
import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, KeepTogether
from reportlab.graphics.shapes import Drawing, Rect, String, Line

ROOT=Path(__file__).parents[1]
SOURCE=ROOT/"paper"/"INCENTIVE_FUZZER_RESEARCH_PREVIEW.md"
OUTPUT=ROOT/"paper"/"output"/"pdf"/"incentive-fuzzer-research-preview.pdf"

def architecture():
    d=Drawing(470,230); d.add(String(5,215,"Figure 1. Evidence architecture",fontSize=11,fontName="Helvetica-Bold"))
    boxes=[("IncentiveSpec",185,175),("Reference evaluator",175,120),("Search",5,55),("SMT",100,55),("Population",195,55),("Games",290,55),("Repair",385,55),("IF-Bench / regression",175,0)]
    for label,x,y in boxes:
        d.add(Rect(x,y,80 if label not in {"Reference evaluator","IF-Bench / regression"} else 120,30,strokeColor=colors.HexColor("#244a73"),fillColor=colors.HexColor("#f1f5f9"),rx=4,ry=4))
        width=80 if label not in {"Reference evaluator","IF-Bench / regression"} else 120
        d.add(String(x+width/2,y+11,label,textAnchor="middle",fontSize=8))
    d.add(Line(225,175,235,150));
    for x in (45,140,235,330,425): d.add(Line(235,120,x,85))
    for x in (45,140,235,330,425): d.add(Line(x,55,235,30))
    return d

def benchmark_figure():
    d=Drawing(470,220); d.add(String(5,205,"Figure 2. IF-Bench detections and candidate evaluations",fontSize=11,fontName="Helvetica-Bold"))
    methods=[("Random",19,1204),("Grid",19,1061),("Boundary",19,369),("Exhaustive",18,1813),("Combined",19,1261)]
    for i,(name,detected,evaluations) in enumerate(methods):
        y=165-i*33; d.add(String(5,y+5,name,fontSize=8)); w=evaluations*0.16
        d.add(Rect(70,y,w,14,fillColor=colors.HexColor("#3465a4"),strokeColor=None)); d.add(String(75+w,y+3,f"{evaluations}; {detected} cases",fontSize=8))
    d.add(String(5,4,"SMT-only omitted: solve time is not a candidate-evaluation count.",fontSize=8))
    return d

def footer(canvas,doc):
    canvas.saveState(); canvas.setFont("Helvetica",8); canvas.setFillColor(colors.HexColor("#52606d"))
    canvas.drawString(0.7*inch,0.45*inch,"Incentive Fuzzer - Research Preview")
    canvas.drawRightString(7.8*inch,0.45*inch,f"Page {doc.page}"); canvas.restoreState()

def inline(text):
    text=re.sub(r"`([^`]+)`",r"<font name='Courier'>\1</font>",text)
    text=re.sub(r"\*\*([^*]+)\*\*",r"<b>\1</b>",text)
    return text.replace("&","&amp;").replace("<b>","__B__").replace("</b>","__/B__").replace("<font name='Courier'>","__C__").replace("</font>","__/C__").replace("<","&lt;").replace(">","&gt;").replace("__B__","<b>").replace("__/B__","</b>").replace("__C__","<font name='Courier'>").replace("__/C__","</font>")

def main():
    styles=getSampleStyleSheet(); styles.add(ParagraphStyle(name="PaperTitle",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=21,leading=25,textColor=colors.HexColor("#17324d"),spaceAfter=16))
    styles.add(ParagraphStyle(name="H1x",parent=styles["Heading1"],fontSize=15,leading=18,textColor=colors.HexColor("#17324d"),spaceBefore=12,spaceAfter=7))
    styles.add(ParagraphStyle(name="Bodyx",parent=styles["BodyText"],fontSize=9.5,leading=13.2,spaceAfter=7,alignment=0))
    styles.add(ParagraphStyle(name="Quotex",parent=styles["Bodyx"],leftIndent=22,rightIndent=22,textColor=colors.HexColor("#36454f"),borderColor=colors.HexColor("#aab7c4"),borderWidth=0.5,borderPadding=7))
    story=[]; code=False; buffer=[]; first=True
    for raw in SOURCE.read_text(encoding="utf-8").splitlines():
        line=raw.rstrip()
        if line.startswith("```"):
            if code: story.append(Preformatted("\n".join(buffer),ParagraphStyle(name="Code",fontName="Courier",fontSize=7.5,leading=10,leftIndent=12,backColor=colors.HexColor("#f4f6f8"),borderPadding=6))); buffer=[]
            code=not code; continue
        if code: buffer.append(line); continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]),styles["PaperTitle"])); first=False
        elif line.startswith("## "):
            title=line[3:]; story.append(Paragraph(inline(title),styles["H1x"]));
            if title.startswith("4. System Architecture"): story.extend([Spacer(1,6),architecture(),Spacer(1,8)])
            if title.startswith("12. External Evaluation"): story.extend([Spacer(1,6),benchmark_figure(),Spacer(1,8)])
        elif line.startswith("### "): story.append(Paragraph(inline(line[4:]),styles["Heading2"]))
        elif re.match(r"^\d+\. ",line): story.append(Paragraph(inline(line),ParagraphStyle(name="List",parent=styles["Bodyx"],leftIndent=15,firstLineIndent=-12)))
        elif line.startswith("> "): story.append(Paragraph(inline(line[2:]),styles["Quotex"]))
        elif line.startswith("**") or line.startswith("Research Preview") or line.startswith("September"):
            story.append(Paragraph(inline(line.replace("  ","")),ParagraphStyle(name="Meta",parent=styles["Bodyx"],alignment=TA_CENTER)))
        elif line: story.append(Paragraph(inline(line),styles["Bodyx"]))
        else: story.append(Spacer(1,3))
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(OUTPUT),pagesize=LETTER,rightMargin=0.7*inch,leftMargin=0.7*inch,topMargin=0.65*inch,bottomMargin=0.65*inch,title="Incentive Fuzzer: Counterexample-Driven Adversarial Testing of Economic Rules",author="Aayush Kadam")
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(OUTPUT)

if __name__=="__main__": main()
