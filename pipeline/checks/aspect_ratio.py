"""Cảnh báo box có tỷ lệ cạnh cực đoan theo pixel; chỉ đọc và không tự sửa nhãn."""
import math

from ..common import WARN, Issue, parse_yolo_line


def run(ds, cfg):
    rules = cfg['bonus']['aspect_ratio']
    limit = float(rules['max_ratio'])
    min_side = float(rules['min_side_px'])
    if not math.isfinite(limit) or not math.isfinite(min_side) or limit < 1 or min_side < 0:
        raise ValueError('max_ratio phải >=1 và min_side_px phải >=0')
    issues = []
    for image in ds.image_files():
        size = ds.image_size(image.stem)
        if not size:
            continue
        for line, text in ds.read_label_lines(image.stem) or []:
            try:
                cls, _, _, width, height = parse_yolo_line(text)
            except (ValueError, OverflowError):
                continue
            if not 0 <= cls < len(ds.classes) or width <= 0 or height <= 0:
                continue
            width_px, height_px = width * size[0], height * size[1]
            short, long = min(width_px, height_px), max(width_px, height_px)
            if short < min_side:
                continue
            ratio = long / short
            if ratio > limit:
                issues.append(Issue(
                    'aspect_ratio', WARN, 'BOX_EXTREME_ASPECT_RATIO', image.stem,
                    f'Tỷ lệ cạnh {ratio:.2f} vượt {limit:g}; cần đối chiếu vật/box', line,
                    {'ratio': round(ratio, 6), 'width_px': round(width_px, 4),
                     'height_px': round(height_px, 4), 'max_ratio': limit},
                ))
    return issues
