import re,sys
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
def convert(src,dst,base=11):
    lines=open(src).read().split('\n'); doc=Document()
    sec=doc.sections[0]; sec.page_width=Inches(8.5); sec.page_height=Inches(11)
    for m in ('left_margin','right_margin'): setattr(sec,m,Inches(1))
    sec.top_margin=Inches(0.8); sec.bottom_margin=Inches(0.8)
    st=doc.styles['Normal']; st.font.name='Times New Roman'; st.element.rPr.rFonts.set(qn('w:eastAsia'),'Times New Roman'); st.font.size=Pt(base)
    st.paragraph_format.space_after=Pt(6); st.paragraph_format.line_spacing=1.05
    for s in ('List Bullet','List Number','Heading 1'):
        doc.styles[s].font.name='Times New Roman'
    fp=sec.footer.paragraphs[0]; fp.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=fp.add_run()
    for t,v in (('begin',None),(None,'PAGE'),('end',None)):
        if t: e=OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'),t)
        else: e=OxmlElement('w:instrText'); e.set(qn('xml:space'),'preserve'); e.text=v
        r._r.append(e)
    r.font.size=Pt(9)
    def runs(p,text,size=None):
        for part in re.split(r'(\*\*[^*]+\*\*|(?<![\w,%.])\*[A-Za-z][^*]*\*(?!\w))',text):
            if not part: continue
            if part.startswith('**'): rr=p.add_run(part[2:-2]); rr.bold=True
            elif re.fullmatch(r'\*[A-Za-z][^*]*\*',part): rr=p.add_run(part[1:-1]); rr.italic=True
            else: rr=p.add_run(part)
            if size: rr.font.size=Pt(size)
    block=[]; insrc=False
    def flush():
        nonlocal block
        if block:
            p=doc.add_paragraph()
            for i,l in enumerate(block):
                runs(p,l,9.5 if insrc else None)
                if i<len(block)-1: p.add_run().add_break()
        block=[]
    for l in lines:
        if l.startswith('# '):
            flush(); h=doc.add_heading(level=1); rr=h.add_run(l[2:]); rr.font.size=Pt(13); rr.font.name='Times New Roman'
        elif l.startswith('## '):
            flush(); insrc=(l[3:].strip()=='Sources'); p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(8); p.paragraph_format.keep_with_next=True
            rr=p.add_run(l[3:]); rr.bold=True; rr.font.size=Pt(base+1)
        elif l.startswith('- '):
            flush(); p=doc.add_paragraph(style='List Bullet'); runs(p,l[2:])
        elif re.match(r'^\d+\. ',l):
            flush()
            if insrc:
                p=doc.add_paragraph(); p.paragraph_format.left_indent=Inches(0.3); p.paragraph_format.first_line_indent=Inches(-0.3); p.paragraph_format.space_after=Pt(2); runs(p,l,9.5)
            else:
                p=doc.add_paragraph(style='List Number'); runs(p,re.sub(r'^\d+\. ','',l))
        elif l.strip()=='': flush()
        else: block.append(l)
    flush(); doc.save(dst)
if __name__=='__main__':
    for a in sys.argv[1:]:
        s,d=a.split('::'); convert(s,d, 10.5 if 'Clerk' in s else 11.5)
