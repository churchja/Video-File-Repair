#!/usr/bin/env python3
"""
MP4 Video Repair Script
Attempts multiple strategies to fix a corrupted .mp4 file using ffmpeg.
Requires: ffmpeg installed and available in your PATH.
  - macOS:   brew install ffmpeg
  - Ubuntu:  sudo apt install ffmpeg
  - Windows: https://ffmpeg.org/download.html
"""

import subprocess
import shutil
import sys
import os


def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print("❌ ffmpeg not found. Please install it first.")
        print("   macOS:   brew install ffmpeg")
        print("   Ubuntu:  sudo apt install ffmpeg")
        print("   Windows: https://ffmpeg.org/download.html")
        sys.exit(1)
    print("✅ ffmpeg found.\n")


def run(cmd, label):
    """Run a command, return True on success."""
    print(f"🔧 Trying: {label}")
    print(f"   Command: {' '.join(cmd)}\n")
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Success: {label}\n")
            return True
        else:
            print(f"⚠️  Failed: {label}")
            # Print last few lines of stderr for clues
            errors = result.stderr.strip().splitlines()
            for line in errors[-5:]:
                print(f"   {line}")
            print()
            return False
    except Exception as e:
        print(f"❌ Error running ffmpeg: {e}\n")
        return False


def probe(input_file):
    """Use ffprobe to check what's readable in the file."""
    print("🔍 Probing file with ffprobe...")
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams",
         "-show_format", "-print_format", "compact", input_file],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if result.stdout.strip():
        print("   Detected streams:")
        for line in result.stdout.strip().splitlines():
            print(f"   {line}")
    else:
        print("   ⚠️  ffprobe couldn't read any stream info (file may be severely corrupted).")
    print()


def repair(input_file):
    base, ext = os.path.splitext(input_file)
    results = []

    # ── Strategy 1: Remux without re-encoding (fixes container/index issues) ──
    out1 = f"{base}_fixed_remux.mp4"
    ok = run([
        "ffmpeg", "-y",
        "-i", input_file,
        "-c", "copy",           # no re-encoding
        "-movflags", "faststart",  # rebuild moov atom at front
        out1
    ], "Remux (copy streams, rebuild index)")
    results.append((ok, out1, "Remux"))

    # ── Strategy 2: Re-encode video + copy audio ──────────────────────────────
    out2 = f"{base}_fixed_reencode.mp4"
    ok = run([
        "ffmpeg", "-y",
        "-i", input_file,
        "-vcodec", "libx264",
        "-acodec", "copy",
        "-crf", "23",           # quality (18=high, 28=low)
        "-preset", "fast",
        out2
    ], "Re-encode video with libx264, copy audio")
    results.append((ok, out2, "Re-encode video"))

    # ── Strategy 3: Re-encode everything (most aggressive) ───────────────────
    out3 = f"{base}_fixed_full_reencode.mp4"
    ok = run([
        "ffmpeg", "-y",
        "-i", input_file,
        "-vcodec", "libx264",
        "-acodec", "aac",
        "-crf", "23",
        "-preset", "fast",
        "-movflags", "faststart",
        out3
    ], "Full re-encode (video + audio)")
    results.append((ok, out3, "Full re-encode"))

    # ── Strategy 4: Ignore errors and extract what's possible ────────────────
    out4 = f"{base}_fixed_error_ignore.mp4"
    ok = run([
        "ffmpeg", "-y",
        "-err_detect", "ignore_err",
        "-i", input_file,
        "-c", "copy",
        out4
    ], "Copy streams while ignoring errors")
    results.append((ok, out4, "Ignore errors + copy"))

    # ── Strategy 5: Force input format to mp4 ────────────────────────────────
    out5 = f"{base}_fixed_forced_fmt.mp4"
    ok = run([
        "ffmpeg", "-y",
        "-f", "mp4",            # force-treat input as mp4
        "-i", input_file,
        "-c", "copy",
        out5
    ], "Force input format as mp4, copy streams")
    results.append((ok, out5, "Force format"))

    # ── Summary ───────────────────────────────────────────────────────────────
    print("=" * 55)
    print("📋 REPAIR SUMMARY")
    print("=" * 55)
    any_success = False
    for ok, outfile, label in results:
        status = "✅" if ok else "❌"
        size = ""
        if ok and os.path.exists(outfile):
            mb = os.path.getsize(outfile) / (1024 * 1024)
            size = f"  ({mb:.1f} MB)"
            any_success = True
        print(f"  {status} {label}: {outfile}{size}")

    print()
    if any_success:
        print("🎉 At least one repair succeeded! Try opening the output files above.")
        print("   Tip: The remux version (if successful) has the best quality since")
        print("        it doesn't re-encode. Use the re-encoded versions as fallback.")
    else:
        print("😞 All strategies failed. The file may be too severely corrupted.")
        print("   You could try a dedicated tool like 'recover_mp4' or 'MP4box'.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_mp4.py <your_video.mp4>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        sys.exit(1)

    print("=" * 55)
    print("🎬 MP4 REPAIR SCRIPT")
    print("=" * 55)
    print(f"Input: {input_file}")
    print(f"Size:  {os.path.getsize(input_file) / (1024*1024):.1f} MB\n")

    check_ffmpeg()
    probe(input_file)
    repair(input_file)
