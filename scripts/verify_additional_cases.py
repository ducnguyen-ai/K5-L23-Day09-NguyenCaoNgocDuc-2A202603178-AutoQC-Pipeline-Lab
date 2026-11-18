"""Ba ca bổ sung theo GUIDE, ngoài bộ tests được bảo vệ; chỉ dùng dữ liệu tổng hợp trong thư mục tạm."""
import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PIL import Image
import yaml
from pipeline.common import Dataset,load_config
from pipeline.checks import label_format,second_opinion
from pipeline.steps import autofix

def main():
 cfg=load_config();results=[]
 with tempfile.TemporaryDirectory(prefix='day09-cases-') as folder:
  root=Path(folder);(root/'images').mkdir();(root/'labels').mkdir()
  Image.new('RGB',(640,480)).save(root/'images'/'sample.JPG')
  (root/'data.yaml').write_text(yaml.safe_dump({'names':cfg['classes']}),encoding='utf-8')
  ds=Dataset(root,cfg['classes']);label=ds.label_path('sample')
  label.write_text('0 .98 .5 .1 .1\n\n0 .98 .5 .1 .1\n',encoding='utf-8')
  issues=label_format.run(ds,cfg)
  assert {(i.code,i.line) for i in issues}=={('BOX_OUT_OF_IMAGE',1),('BOX_OUT_OF_IMAGE',3),('DUP_BOX',3)}
  fixes=autofix.fix(ds,issues,cfg)
  assert [(f['line'],f['action']) for f in fixes]==[(1,'clip_box'),(3,'drop_line')]
  assert autofix.fix(ds,label_format.run(ds,cfg),cfg)==[]
  results.append('PASS: hai lỗi trên một dòng, có dòng trống; xoá ưu tiên hơn clip, không lệch dòng, lần hai không sửa thêm')
  label.write_text('inf .5 .5 .1 .1\n\n0 .5 .5 .2 .2\n',encoding='utf-8')
  issues=label_format.run(ds,cfg)
  assert [(i.code,i.line) for i in issues]==[('BAD_FORMAT',1)]
  results.append('PASS: ID lớp vô hạn không làm dừng lượt quét; dòng sau vẫn được kiểm')
  label.write_text('0 .5 .5 .2 .2\n\n1 .1 .1 .1 .1\n',encoding='utf-8')
  predictions={'sample':[[0,.99,.5,.5,.2,.2],[2,.99,.8,.8,.1,.2],[3,.99,.2,.7,.1,.2]]}
  issues=second_opinion.run(ds,cfg,preds=predictions)
  assert [(i.code,i.line) for i in issues]==[('POSSIBLE_MISSING',None),('POSSIBLE_MISSING',None),('POSSIBLE_FALSE_POS',3)]
  results.append('PASS: nhiều dự đoán tạo nhiều cảnh báo đúng thứ tự; false positive giữ số dòng gốc')
 for result in results:print(result)
 return results
if __name__=='__main__':main()
