"""Tạo 10 ảnh để học viên tự quan sát bằng visualizer gốc; không đọc đáp án và không gửi ảnh ra mạng."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pipeline.common import ROOT,Dataset,load_config,parse_yolo_line
from scripts.viz_labels import draw

def main():
 ds=Dataset(ROOT/'data/raw',load_config()['classes'])
 out=ROOT/'work/viz';out.mkdir(parents=True,exist_ok=True)
 chosen=[]
 for path in ds.image_files():
  if len(chosen)==10:break
  if not ds.image_size(path.stem):continue
  boxes=[]
  for _,line in ds.read_label_lines(path.stem) or []:
   try:boxes.append(parse_yolo_line(line))
   except (ValueError,OverflowError):continue
  if any(b[3]<0 or b[4]<0 for b in boxes):continue
  try:draw(ds,path.stem,out/f'{path.stem}.png')
  except (ValueError,OSError) as exc:
   print(f'Không vẽ được {path.stem}: {type(exc).__name__}')
   continue
  chosen.append(path.stem)
 cards=''.join(f'<article><h2>{s}</h2><a href="{s}.png" target="_blank"><img src="{s}.png" loading="lazy"></a><label>Quan sát của bạn:<textarea placeholder="Vật nào? Nhãn/box đang sai gì? Nên sửa ra sao?"></textarea></label></article>' for s in chosen)
 template=(ROOT/'docs/review_gallery_template.html').read_text(encoding='utf-8')
 (out/'index.html').write_text(template.replace('{{CARDS}}',cards),encoding='utf-8')
 print(f'Đã tạo {len(chosen)} ảnh: '+', '.join(chosen))
if __name__=='__main__':main()
