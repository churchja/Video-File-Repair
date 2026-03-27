# Video File Repair

A Python script that attempts to repair corrupted `.mp4` video files using `ffmpeg`. It tries five different recovery strategies automatically and saves each successful result as a separate file.

Compatible with **Python 2.7 and Python 3**.

---

## Requirements

- Python 2.7 or Python 3
- `ffmpeg` installed and available in your PATH

### Install ffmpeg

| Platform | Command |
|----------|---------|
| macOS    | `brew install ffmpeg` |
| Ubuntu   | `sudo apt install ffmpeg` |
| Windows  | Download from [ffmpeg.org](https://ffmpeg.org/download.html) |

---

## Usage

```bash
python fix_mp4.py <your_video.mp4>
```

Or with Python 3:

```bash
python3 fix_mp4.py <your_video.mp4>
```

### Example

```bash
python3 fix_mp4.py /Volumes/SSD/my_video.mp4
```

---

## Repair Strategies

The script tries the following strategies in order, from least to most aggressive:

| # | Strategy | Description |
|---|----------|-------------|
| 1 | **Remux** | Rebuilds the container and index without re-encoding — best quality if it works |
| 2 | **Re-encode video** | Re-encodes video with H.264, copies original audio |
| 3 | **Full re-encode** | Re-encodes both video (H.264) and audio (AAC) from scratch |
| 4 | **Ignore errors** | Copies streams while skipping over corrupted sections |
| 5 | **Force format** | Forces ffmpeg to treat the input as MP4 before reading |

Each successful repair is saved as a separate output file, e.g.:
- `my_video_fixed_remux.mp4`
- `my_video_fixed_reencode.mp4`
- `my_video_fixed_full_reencode.mp4`
- `my_video_fixed_error_ignore.mp4`
- `my_video_fixed_forced_fmt.mp4`

---

## Output Example

```
=======================================================
MP4 REPAIR SCRIPT
=======================================================
Input: kor1.mp4
Size:  1024.3 MB

[OK] ffmpeg found.

[INFO] Probing file with ffprobe...

[TRYING] Remux (copy streams, rebuild index)
[SUCCESS] Remux

...

=======================================================
REPAIR SUMMARY
=======================================================
  [OK]   Remux:             kor1_fixed_remux.mp4  (1024.3 MB)
  [OK]   Re-encode video:   kor1_fixed_reencode.mp4  (980.1 MB)
  [FAIL] Full re-encode:    kor1_fixed_full_reencode.mp4
  [OK]   Ignore errors:     kor1_fixed_error_ignore.mp4  (1024.3 MB)
  [FAIL] Force format:      kor1_fixed_forced_fmt.mp4

At least one repair succeeded! Try opening the output files above.
Tip: The remux version (if successful) has the best quality.
```

---

## What Kind of Corruption Can It Fix?

| Issue | Likely Fixable? |
|-------|----------------|
| Missing or corrupted container headers | Yes |
| Truncated / partially downloaded file | Yes |
| Codec or container mismatch | Yes |
| Corrupted file index | Yes |
| Audio/video sync issues | Possibly |
| Severely corrupted raw frame data | No |

---

## License

MIT License — free to use, modify, and distribute.
