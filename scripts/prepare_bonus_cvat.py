"""Chuẩn bị task bonus CVAT từ bản sao pipeline; tạo YOLO 1.1 và bảng đối chiếu width<20 với BOX_TINY."""
import csv,json,shutil,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pipeline.common import ROOT,Dataset,load_config,parse_yolo_line
from pipeline.checks import label_format


def main():
    cfg=load_config();ds=Dataset(ROOT/'work/run/ds',cfg['classes'])
    queued=[r['image'] for r in csv.DictReader((ROOT/'submission/reports/05_review_queue.csv').open(encoding='utf-8'))]
    measurements={}
    for image in ds.image_files():
        size=ds.image_size(image.stem)
        if not size:continue
        boxes=[]
        for line,text in ds.read_label_lines(image.stem) or []:
            try:cls,x,y,w,h=parse_yolo_line(text)
            except (ValueError,OverflowError):continue
            if not 0<=cls<len(ds.classes) or w<=0 or h<=0:continue
            width,height=w*size[0],h*size[1]
            boxes.append(dict(image=image.name,line=line,label=cfg['classes'][cls],width_px=width,height_px=height,width_lt20=width<20,pipeline_tiny=min(width,height)<cfg['label_format']['min_box_px']))
        measurements[image.stem]=boxes
    candidates=sorted((s for s,boxes in measurements.items() if any(b['width_lt20'] for b in boxes)),key=lambda s:(queued.index(s) if s in queued else len(queued),s))
    if len(candidates)<5:raise SystemExit('Không đủ 5 ảnh có width<20 để làm minh chứng.')
    selected=sorted(set(queued[:20]+candidates[:5]))
    out=ROOT/'work/bonus/cvat';images=out/'images';images.mkdir(parents=True,exist_ok=True)
    wanted={ds.image_path(s).name for s in selected}
    existing={p.name for p in images.iterdir() if p.is_file()}
    if existing-wanted:raise SystemExit('Thư mục cũ có ảnh ngoài lựa chọn; dùng thư mục sạch trước khi chuẩn bị lại.')
    for s in selected:shutil.copy2(ds.image_path(s),images/ds.image_path(s).name)
    labels=json.loads((ROOT/'cvat/labels.json').read_text(encoding='utf-8'))
    for label in labels:
        for attr in label.get('attributes',[]):
            if attr['input_type']=='checkbox' and not attr.get('values'):attr['values']=['false']
    (out/'labels_compatible.json').write_text(json.dumps(labels,ensure_ascii=False,indent=2),encoding='utf-8')
    with zipfile.ZipFile(out/'annotations_yolo11.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('obj.names','\n'.join(cfg['classes'])+'\n')
        z.writestr('obj.data',f"classes = {len(cfg['classes'])}\ntrain = train.txt\nnames = obj.names\nbackup = backup/\n")
        z.writestr('train.txt',''.join(f'obj_train_data/{ds.image_path(s).name}\n' for s in selected))
        for s in selected:z.write(ds.label_path(s),f'obj_train_data/{s}.txt')
    evidence=ROOT/'submission/bonus/cvat';evidence.mkdir(parents=True,exist_ok=True)
    comparison=[];all_boxes=[]
    for frame,s in enumerate(selected):
        boxes=measurements[s];all_boxes.extend(dict(frame=frame,**b) for b in boxes)
        comparison.append(dict(frame=frame,image=ds.image_path(s).name,width_lt20_count=sum(b['width_lt20'] for b in boxes),pipeline_box_tiny_count=sum(b['pipeline_tiny'] for b in boxes),overlap_count=sum(b['width_lt20'] and b['pipeline_tiny'] for b in boxes)))
    for name,rows in [('expected_filters.csv',comparison),('box_measurements.csv',all_boxes)]:
        with (evidence/name).open('w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    plan={'task_name':'Day09-178-bonus-small-boxes','project_name':'Day09-178-bonus','source':'work/run/ds','selection':'20 first review queue images plus first 5 width<20 candidate images; unique, sorted by filename', 'images':[ds.image_path(s).name for s in selected],'screenshots_target_images':[ds.image_path(s).name for s in candidates[:5]],'n_images':len(selected),'yolo_format':'YOLO 1.1','filter':'width < 20'}
    (out/'selection.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
    (evidence/'selection.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(plan,ensure_ascii=False))

if __name__=='__main__':main()
