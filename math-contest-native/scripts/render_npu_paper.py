"""Render the final LaTeX PDF for page-by-page visual inspection."""
from pathlib import Path
import json
import pypdfium2 as pdfium
from PIL import Image, ImageOps, ImageDraw

source = Path('paper/build/main.pdf')
target = Path('.local/npu-paper-review')
target.mkdir(parents=True, exist_ok=True)
pdf = pdfium.PdfDocument(str(source))
pages = []
for i in range(len(pdf)):
    page = pdf[i]
    bitmap = page.render(scale=1.4)
    picture = bitmap.to_pil().convert('RGB')
    picture.save(target / f'page-{i+1:02d}.png')
    pages.append(picture)
    bitmap.close()
    page.close()
for start in range(0, len(pages), 4):
    sheet = Image.new('RGB', (1200, 1720), '#dddddd')
    for offset, picture in enumerate(pages[start:start+4]):
        small = ImageOps.contain(picture, (590, 820))
        x, y = (offset % 2)*600, (offset//2)*860
        sheet.paste(small, (x, y+25))
        ImageDraw.Draw(sheet).text((x+10, y+5), f'Page {start+offset+1}', fill='black')
    sheet.save(target / f'contact-{start//4+1}.png')
print(json.dumps({'pages': len(pdf), 'output': str(target)}))
pdf.close()
