"""Chạy phép kiểm bonus bằng dispatcher chuẩn, không đổi registry/cấu hình/gate của bài chính."""
import argparse
import json
import sys
from pathlib import Path
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pipeline import checks
from pipeline.common import ROOT, Dataset, load_config
from pipeline.steps.report import write_report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--src',default='work/run/ds')
    parser.add_argument('--config',default='configs/bonus.yaml')
    parser.add_argument('--out',default='submission/bonus/aspect_ratio')
    args=parser.parse_args()
    cfg=load_config()
    cfg.update(yaml.safe_load((ROOT/args.config).read_text(encoding='utf-8')))
    ds=Dataset(ROOT/args.src,cfg['classes'])
    if not ds.image_files():raise SystemExit('Không có ảnh; chạy pipeline chính trước hoặc truyền --src.')
    issues=checks.run_checks(['aspect_ratio'],ds,cfg)
    out=ROOT/args.out;out.parent.mkdir(parents=True,exist_ok=True)
    write_report(issues,out,'Bonus: box có tỷ lệ cạnh cực đoan (cảnh báo, không sửa)',len(ds.image_files()))
    summary={'check':'aspect_ratio','source':args.src,'n_images':len(ds.image_files()),
             'n_issues':len(issues),'n_flagged_images':len({i.image for i in issues}),
             'rules':cfg['bonus']['aspect_ratio'],'read_only':True,'affects_core_gate':False}
    out.with_suffix('.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':main()
