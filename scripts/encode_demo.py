"""Encode the actual Playwright recordings into a captioned, browser-playable MP4."""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / ".runtime/demo-recording"
DESTINATION = ROOT / "docs/demo"
DESTINATION.mkdir(parents=True, exist_ok=True)
recording = json.loads((SOURCE / "recording.json").read_text())


def run(arguments):
    subprocess.run(arguments, check=True, stdout=subprocess.DEVNULL)


def timestamp(seconds, separator=".", centiseconds=False):
    multiplier = 100 if centiseconds else 1000
    units = round(max(0, seconds) * multiplier)
    seconds, fraction = divmod(units, multiplier)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}{separator}{fraction:0{2 if centiseconds else 3}d}"


captions = ["WEBVTT", ""]
chapters = []
encoded = []
offset = 0
for number, segment in enumerate(recording["segments"]):
    first = segment["markers"][0]["start"]
    duration = float(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                segment["video"],
            ]
        )
    )
    ass = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1440",
        "PlayResY: 1080",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,DejaVu Sans,20,&H00FFFFFF,&H00FFFFFF,&H001D302A,&H001D302A,0,0,0,0,100,100,0,0,1,0,0,2,28,28,16,1",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for index, marker in enumerate(segment["markers"]):
        start = marker["start"] - first
        end = (
            segment["markers"][index + 1]["start"]
            if index + 1 < len(segment["markers"])
            else duration
        ) - first
        title = marker["title"].replace("{", "").replace("}", "")
        caption = marker["caption"].replace("{", "").replace("}", "")
        text = r"{\b1\fs24}" + title + r"{\b0\fs20}\N" + caption
        ass.append(
            f"Dialogue: 0,{timestamp(start, centiseconds=True)},{timestamp(end, centiseconds=True)},Default,,0,0,0,,{text}"
        )
        captions += [
            f"{timestamp(offset + start)} --> {timestamp(offset + end)}",
            title,
            caption,
            "",
        ]
        chapters.append({"seconds": round(offset + start, 2), "title": title})
    ass_path = SOURCE / f"segment-{number}.ass"
    ass_path.write_text("\n".join(ass) + "\n")
    output = SOURCE / f"segment-{number}.mp4"
    filters = (
        "fps=25,scale=1440:1000:force_original_aspect_ratio=decrease,"
        "pad=1440:1080:(ow-iw)/2:0:color=0x102c28,setsar=1,"
        f"subtitles={ass_path.as_posix()}"
    )
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "warning",
            "-y",
            "-ss",
            str(first),
            "-i",
            segment["video"],
            "-vf",
            filters,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "24",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    encoded.append(output)
    offset += duration - first

manifest = SOURCE / "concat.txt"
manifest.write_text("\n".join(f"file '{video.as_posix()}'" for video in encoded) + "\n")
movie = DESTINATION / "careerlens-demo.mp4"
run(
    [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "warning",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(manifest),
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        "-metadata",
        "title=CareerLens feature walkthrough",
        str(movie),
    ]
)
(DESTINATION / "careerlens-demo.vtt").write_text("\n".join(captions))
(DESTINATION / "chapters.json").write_text(json.dumps(chapters, indent=2) + "\n")
dashboard = next(
    chapter["seconds"] for chapter in chapters if chapter["title"] == "Dashboard"
)
run(
    [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        str(dashboard + 2),
        "-i",
        str(movie),
        "-frames:v",
        "1",
        "-update",
        "1",
        "-q:v",
        "2",
        str(DESTINATION / "poster.jpg"),
    ]
)
print(
    f"Encoded {len(encoded)} real recording segments: {offset:.1f} seconds; {movie.stat().st_size / 1024 / 1024:.1f} MiB."
)
