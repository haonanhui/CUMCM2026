"""Render every revision-three PDF page and record measurable layout evidence."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
import pypdfium2 as pdfium
import pdfplumber

root = Path(__file__).resolve().parents[1]
source = root/'paper/revision3/build/main.pdf'
target = root/'reports/npu-r3-evidence/pages'
target.mkdir(parents=True,exist_ok=True)
pdf = pdfium.PdfDocument(str(source))
records=[]
body_count=0
in_body=False
with pdfplumber.open(source) as text_pdf:
    for i,page in enumerate(text_pdf.pages):
        raster=pdf[i]; bitmap=raster.render(scale=2)
        bitmap.to_pil().save(target/f'page-{i+1:02d}.png')
        bitmap.close(); raster.close()
        text=page.extract_text() or ''
        (target/f'page-{i+1:02d}.txt').write_text(text,encoding='utf-8')
        if i==2: in_body=True
        body=text if in_body else ''
        if '参考文献' in body:
            body=body.split('参考文献',1)[0]; in_body=False
        body_count+=len(re.findall('[\u4e00-\u9fff]',body))
        chars=page.chars
        fonts=Counter((c['fontname'],round(c['size'],2)) for c in chars)
        baselines=sorted(set(round(c['bottom'],1) for c in chars if 'SimSun' in c['fontname'] and 11.8<c['size']<12.1 and c['top']<750))
        gaps=Counter(round(b-a,1) for a,b in zip(baselines,baselines[1:]) if 12<b-a<25)
        records.append({'page':i+1,'size':[page.width,page.height],'characters':len(chars),
                        'body_cjk':len(re.findall('[\u4e00-\u9fff]',body)),
                        'fonts':[[f,s,n] for (f,s),n in fonts.most_common(10)],'baseline_gaps':dict(gaps),
                        'left':min((c['x0'] for c in chars),default=0),'right':max((c['x1'] for c in chars),default=0),
                        'first':text[:140],'last':text[-140:]})
pdf.close()
output={'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'pages':records,'body_cjk':body_count,'render_scale':2}
(target.parent/'pdf-inspection.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pages':len(records),'body_cjk':body_count,'sha256':output['sha256']}))
