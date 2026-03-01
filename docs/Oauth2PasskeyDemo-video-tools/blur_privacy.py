#!/usr/bin/env python3
"""Blur privacy-sensitive text in demo video files.

Phase 1: Sparse CLAHE-OCR scan to detect sensitive text positions.
Phase 2: OpenCV frame-by-frame blur with linear interpolation of positions
          between scan points (handles scrolling).
Phase 3: Re-encode with ffmpeg for H.264 output.
"""

import sys
import subprocess
import tempfile
import os
import cv2
import numpy as np
import pytesseract
from PIL import Image

# Keywords to detect (case-insensitive partial match)
KEYWORDS = [
    "ktaka", "oidc", "gmail",
    "114.150", "237.7", "150.237",
]

# How often to sample frames for OCR (every N frames)
SCAN_INTERVAL = 10

# Padding around detected text (pixels)
PADDING = 15

# Blur kernel size (must be odd)
BLUR_KSIZE = 51

# Manual blur regions for cases where OCR fails to detect text
# (e.g., styled button elements in Google dialogs).
# Format: { "filename_prefix": [(start_frame, end_frame, x, y, w, h), ...] }
MANUAL_REGIONS = {
    "o2p-2026-03-01_17.11.16": [
        # Google re-login dialog: email in pill/button element
        (220, 345, 155, 395, 240, 50),
    ],
}


def scan_frame(frame_bgr):
    """Run CLAHE-enhanced OCR on a single frame, return keyword hits."""
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    pil = Image.fromarray(enhanced)
    data = pytesseract.image_to_data(pil, output_type=pytesseract.Output.DICT)

    hits = []
    for i in range(len(data["text"])):
        t = data["text"][i].strip()
        if not t:
            continue
        tl = t.lower()
        for kw in KEYWORDS:
            if kw.lower() in tl:
                hits.append((data["left"][i], data["top"][i],
                             data["width"][i], data["height"][i]))
                break
    return hits


def pad_box(x, y, w, h):
    """Add padding to a box."""
    return (max(0, x - PADDING), max(0, y - PADDING),
            w + 2 * PADDING, h + 2 * PADDING)


def merge_nearby_boxes(boxes, y_threshold=10, x_gap=30):
    """Merge boxes on the same line that are close together."""
    if not boxes:
        return []
    sorted_boxes = sorted(boxes, key=lambda b: (b[1], b[0]))
    merged = [list(sorted_boxes[0])]
    for (x, y, w, h) in sorted_boxes[1:]:
        cur = merged[-1]
        cy_cur = cur[1] + cur[3] // 2
        cy_new = y + h // 2
        x_end_cur = cur[0] + cur[2]
        if abs(cy_cur - cy_new) < y_threshold and x - x_end_cur < x_gap:
            new_x = min(cur[0], x)
            new_y = min(cur[1], y)
            new_x2 = max(cur[0] + cur[2], x + w)
            new_y2 = max(cur[1] + cur[3], y + h)
            merged[-1] = [new_x, new_y, new_x2 - new_x, new_y2 - new_y]
        else:
            merged.append([x, y, w, h])
    return [tuple(b) for b in merged]


def interpolate_boxes(boxes_a, boxes_b, frac):
    """Linearly interpolate blur box positions between two scan frames."""
    if not boxes_a:
        return boxes_b if boxes_b else []
    if not boxes_b:
        return boxes_a

    result = []
    used_b = set()

    for (ax, ay, aw, ah) in boxes_a:
        best_j, best_dist = None, 999
        for j, (bx, by, bw, bh) in enumerate(boxes_b):
            if j not in used_b:
                dist = abs(ax - bx)
                if dist < best_dist:
                    best_dist = dist
                    best_j = j

        if best_j is not None and best_dist < 60:
            bx, by, bw, bh = boxes_b[best_j]
            used_b.add(best_j)
            result.append((
                int(ax + (bx - ax) * frac),
                int(ay + (by - ay) * frac),
                int(aw + (bw - aw) * frac),
                int(ah + (bh - ah) * frac),
            ))
        else:
            result.append((ax, ay, aw, ah))

    for j, box in enumerate(boxes_b):
        if j not in used_b:
            result.append(box)

    return result


def apply_blur(frame, regions):
    """Apply Gaussian blur to specified regions in the frame."""
    fh, fw = frame.shape[:2]
    for (rx, ry, rw, rh) in regions:
        x1, y1 = max(0, rx), max(0, ry)
        x2, y2 = min(fw, rx + rw), min(fh, ry + rh)
        if x2 <= x1 or y2 <= y1:
            continue
        roi = frame[y1:y2, x1:x2]
        frame[y1:y2, x1:x2] = cv2.GaussianBlur(roi, (BLUR_KSIZE, BLUR_KSIZE), 0)
    return frame


def get_manual_regions(filename, frame_idx):
    """Get manual blur regions for a specific frame."""
    regions = []
    for prefix, entries in MANUAL_REGIONS.items():
        if prefix in filename:
            for (start, end, x, y, w, h) in entries:
                if start <= frame_idx <= end:
                    regions.append((x, y, w, h))
    return regions


def process_video(input_path, output_path):
    """Process a single video file."""
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Cannot open {input_path}")
        return False

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Processing: {input_path}")
    print(f"  {width}x{height}, {fps:.1f} fps, {total} frames")

    # --- Phase 1: Sparse OCR scan ---
    print(f"  Phase 1: OCR scan (every {SCAN_INTERVAL} frames)...")
    scan_results = {}  # frame_idx -> [(x, y, w, h), ...]

    for idx in range(0, total, SCAN_INTERVAL):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            break
        hits = scan_frame(frame)
        if hits:
            padded = [pad_box(*h) for h in hits]
            scan_results[idx] = merge_nearby_boxes(padded)

    scan_frames = sorted(scan_results.keys())
    print(f"  Found sensitive text in {len(scan_frames)} scan frames")

    has_manual = any(
        prefix in os.path.basename(input_path)
        for prefix in MANUAL_REGIONS
    )
    if not scan_frames and not has_manual:
        cap.release()
        print("  No sensitive text found, skipping")
        return True

    # --- Phase 2: Frame-by-frame blur with interpolation ---
    print(f"  Phase 2: Applying blur with interpolation...")

    tmp_raw = tempfile.NamedTemporaryFile(suffix=".avi", delete=False)
    tmp_raw_path = tmp_raw.name
    tmp_raw.close()

    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    writer = cv2.VideoWriter(tmp_raw_path, fourcc, fps, (width, height))

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Find surrounding scan frames + manual regions
        regions = get_interpolated_regions(frame_idx, scan_frames, scan_results)
        manual = get_manual_regions(os.path.basename(input_path), frame_idx)
        if manual:
            regions = regions + manual

        if regions:
            frame = apply_blur(frame, regions)

        writer.write(frame)
        frame_idx += 1

        if frame_idx % 200 == 0:
            print(f"    {frame_idx}/{total} ({100 * frame_idx // total}%)")

    cap.release()
    writer.release()
    print(f"  Processed {frame_idx} frames")

    # --- Phase 3: Re-encode with ffmpeg ---
    print(f"  Phase 3: Encoding H.264...")
    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", tmp_raw_path,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        output_path,
    ], capture_output=True, text=True)

    os.unlink(tmp_raw_path)

    if result.returncode != 0:
        print(f"  ffmpeg error: {result.stderr[-500:]}")
        return False

    # Copy audio if present
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=codec_type", "-of", "csv=p=0", input_path],
        capture_output=True, text=True
    )
    if probe.stdout.strip():
        tmp = output_path + ".tmp.mp4"
        os.rename(output_path, tmp)
        subprocess.run([
            "ffmpeg", "-y",
            "-i", tmp, "-i", input_path,
            "-c:v", "copy", "-c:a", "aac",
            "-map", "0:v:0", "-map", "1:a:0",
            "-movflags", "+faststart",
            output_path,
        ], capture_output=True, text=True)
        os.unlink(tmp)

    out_size = os.path.getsize(output_path) / 1024
    print(f"  Output: {output_path} ({out_size:.0f} KB)")
    return True


def get_interpolated_regions(frame_idx, scan_frames, scan_results):
    """Get blur regions for a frame by interpolating between scan points."""
    if not scan_frames:
        return []

    # Before first scan frame
    if frame_idx < scan_frames[0]:
        # Only apply if within half-interval of first scan
        if scan_frames[0] - frame_idx <= SCAN_INTERVAL // 2:
            return scan_results[scan_frames[0]]
        return []

    # After last scan frame
    if frame_idx > scan_frames[-1]:
        if frame_idx - scan_frames[-1] <= SCAN_INTERVAL // 2:
            return scan_results[scan_frames[-1]]
        return []

    # Find bracketing scan frames
    import bisect
    pos = bisect.bisect_right(scan_frames, frame_idx)

    if pos == 0:
        return scan_results.get(scan_frames[0], [])

    prev_idx = scan_frames[pos - 1]

    if pos < len(scan_frames):
        next_idx = scan_frames[pos]
        gap = next_idx - prev_idx

        # If gap is too large, only apply near the scan points
        if gap > SCAN_INTERVAL * 3:
            if frame_idx - prev_idx <= SCAN_INTERVAL // 2:
                return scan_results[prev_idx]
            if next_idx - frame_idx <= SCAN_INTERVAL // 2:
                return scan_results[next_idx]
            return []

        frac = (frame_idx - prev_idx) / gap
        prev_boxes = scan_results[prev_idx]
        next_boxes = scan_results[next_idx]
        return interpolate_boxes(prev_boxes, next_boxes, frac)
    else:
        return scan_results.get(prev_idx, [])


def main():
    video_dir = os.path.dirname(os.path.abspath(__file__))
    input_files = sorted([
        f for f in os.listdir(video_dir)
        if f.startswith("o2p-") and f.endswith(".mp4") and "-blurred" not in f
    ])

    if not input_files:
        print("No input video files found (o2p-*.mp4)")
        sys.exit(1)

    print(f"Found {len(input_files)} video(s) to process")
    print(f"Scan interval: {SCAN_INTERVAL} frames, Padding: {PADDING}px")
    print()

    for filename in input_files:
        input_path = os.path.join(video_dir, filename)
        output_name = filename.replace(".mp4", "-blurred.mp4")
        output_path = os.path.join(video_dir, output_name)
        success = process_video(input_path, output_path)
        print(f"  {'Done' if success else 'FAILED'}!\n")


if __name__ == "__main__":
    main()
