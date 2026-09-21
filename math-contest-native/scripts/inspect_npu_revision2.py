"""Render every page and retain measured typography with the PDF identity."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import pypdfium2 as pdfium
import pdfplumber

root = Path(__file__).resolve().parents[1]
source = root/'paper/revision2/build/main.pdf'
target = root/'reports/npu-r2-evidence/pages'
target.mkdir(parents=True, exist_ok=True)
pdf = pdfium.PdfDocument(str(source))
records = []
with pdfplumber.open(source) as text_pdf:
    for i, page in enumerate(text_pdf.pages):
        raster = pdf[i]
        bitmap = raster.render(scale=2)
        bitmap.to_pil().save(target/f'page-{i+1:02d}.png')
        bitmap.close()
        raster.close()
        chars = page.chars
        sizes = Counter((x['fontname'],round(x['size'],2)) for x in chars)
        body = [x for x in chars if 'SimSun' in x['fontname'] and 11.8<x['size']<12.1 and x['top']<750]
        baselines = sorted(set(round(x['bottom'],1) for x in body))
        gaps = Counter(round(b-a,1) for a,b in zip(baselines,baselines[1:]) if 12<b-a<25)
        text = page.extract_text() or ''
        (target/f'page-{i+1:02d}.txt').write_text(text,encoding='utf-8')
        records.append({'pdf_page':i+1,'size':[page.width,page.height], 'chars':len(chars),
                        'font_sizes':[[a,b,c] for (a,b),c in sizes.most_common(12)],'body_baseline_gaps':dict(gaps),
                        'leftmost':min((x['x0'] for x in chars),default=None),'rightmost':max((x['x1'] for x in chars),default=None),
                        'first_text':text[:110],'last_text':text[-110:]})
pdf.close()
(target.parent/'pdf-inspection.json').write_text(json.dumps({'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'render_scale':2,'pages':records},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'page':r['pdf_page'],'first':r['first_text'],'last':r['last_text'],'gaps':r['body_baseline_gaps']} for r in records],ensure_ascii=False))
