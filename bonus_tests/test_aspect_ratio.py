import hashlib
import pytest
from PIL import Image
from pipeline.common import Dataset
from pipeline.checks import aspect_ratio

@pytest.fixture
def dataset(tmp_path):
    (tmp_path/'images').mkdir(); (tmp_path/'labels').mkdir()
    Image.new('RGB',(1000,100)).save(tmp_path/'images'/'sample.JPG')
    return Dataset(tmp_path,['car','person','truck','bus'])

@pytest.fixture
def cfg():
    return {'bonus':{'aspect_ratio':{'max_ratio':10.0,'min_side_px':2.0}}}

def labels(ds,text):
    ds.label_path('sample').write_text(text,encoding='utf-8')


def test_uses_pixel_ratio_instead_of_normalized_ratio(dataset,cfg):
    labels(dataset,'0 .5 .5 .3 .2\n')  # 300px/20px = 15; normalized ratio only 1.5
    result=aspect_ratio.run(dataset,cfg)
    assert len(result)==1 and result[0].extra['ratio']==15
    assert result[0].severity=='warn' and result[0].code=='BOX_EXTREME_ASPECT_RATIO'


def test_exact_limit_is_silent_and_config_controls_result(dataset,cfg):
    labels(dataset,'0 .5 .5 .2 .2\n')  # 200/20 = 10
    assert aspect_ratio.run(dataset,cfg)==[]
    cfg['bonus']['aspect_ratio']['max_ratio']=9
    assert len(aspect_ratio.run(dataset,cfg))==1


def test_blank_and_bad_lines_keep_original_number(dataset,cfg):
    labels(dataset,'garbage\n\n0 .5 .5 .3 .2\n')
    assert [(i.image,i.line) for i in aspect_ratio.run(dataset,cfg)]==[('sample',3)]


def test_tall_and_wide_boxes_are_symmetric(dataset,cfg):
    Image.new('RGB',(100,1000)).save(dataset.images_dir/'tall.jpg')
    dataset.label_path('tall').write_text('1 .5 .5 .2 .3\n',encoding='utf-8')
    labels(dataset,'0 .5 .5 .3 .2\n')
    assert [i.extra['ratio'] for i in aspect_ratio.run(dataset,cfg)]==[15,15]


def test_invalid_and_subpixel_boxes_are_skipped(dataset,cfg):
    labels(dataset,'93 .5 .5 .3 .2\n0 nan .5 .3 .2\ninf .5 .5 .3 .2\n0 .5 .5 0 .2\n0 .5 .5 -.3 .2\n0 .5 .5 .8 .001\n')
    assert aspect_ratio.run(dataset,cfg)==[]


def test_missing_label_and_corrupt_image_do_not_crash(dataset,cfg):
    assert aspect_ratio.run(dataset,cfg)==[]
    (dataset.images_dir/'broken.png').write_bytes(b'broken')
    dataset.label_path('broken').write_text('0 .5 .5 .3 .2\n',encoding='utf-8')
    assert aspect_ratio.run(dataset,cfg)==[]


def test_check_is_read_only_and_repeatable(dataset,cfg):
    labels(dataset,'0 .5 .5 .3 .2\n')
    paths=[p for p in dataset.root.rglob('*') if p.is_file()]
    before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    first=aspect_ratio.run(dataset,cfg)
    assert first==aspect_ratio.run(dataset,cfg)
    assert before=={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

@pytest.mark.parametrize('limit,side',[(.5,2),(10,-1),(float('nan'),2),(10,float('inf'))])
def test_invalid_settings_are_rejected(dataset,cfg,limit,side):
    cfg['bonus']['aspect_ratio'].update(max_ratio=limit,min_side_px=side)
    with pytest.raises(ValueError):aspect_ratio.run(dataset,cfg)
