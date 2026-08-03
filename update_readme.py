# -*- coding: utf-8 -*-
import datetime
import hashlib
import json
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ANNOTATIONS_DIR = os.path.join(BASE_DIR, "annotations")
EXCLUDED_JSON = {"config.json", "progress_history.json"}


def read_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def file_hash(path):
    hasher = hashlib.sha256()
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().replace("\r\n", "\n")
    hasher.update(content.encode("utf-8"))
    return hasher.hexdigest()


def beijing_now():
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
    return now.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d %H:%M:%S")


def progress_bar(value, total, width=20):
    if total <= 0:
        return "░" * width
    filled = max(0, min(width, round(width * value / total)))
    return "█" * filled + "░" * (width - filled)


def list_label_jsons():
    if not os.path.isdir(ANNOTATIONS_DIR):
        return []
    return sorted(
        f
        for f in os.listdir(ANNOTATIONS_DIR)
        if f.endswith(".json") and f not in EXCLUDED_JSON and os.path.isfile(os.path.join(ANNOTATIONS_DIR, f))
    )


def short_name(filename):
    return os.path.splitext(filename)[0]


def build_svg(history, total_images):
    daily = history.get("daily_stats", {})
    points = [(day, int(daily[day].get("total_completed", 0))) for day in sorted(daily)]
    if not points:
        points = [(beijing_now()[0], 0)]

    width, height = 860, 320
    pad_left, pad_right, pad_top, pad_bottom = 70, 30, 35, 55
    chart_w = width - pad_left - pad_right
    chart_h = height - pad_top - pad_bottom
    max_y = max(total_images, max(v for _, v in points), 1)

    coords = []
    for i, (_, value) in enumerate(points):
        x = pad_left + (chart_w * i / max(len(points) - 1, 1))
        y = pad_top + chart_h - (chart_h * value / max_y)
        coords.append((x, y))

    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    circles = "\n".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#2563eb" />' for x, y in coords)
    labels = "\n".join(
        f'<text x="{x:.1f}" y="{height - 22}" text-anchor="middle" font-size="12" fill="#475569">{day[5:]}</text>'
        for (day, _), (x, _) in zip(points, coords)
    )
    latest = points[-1][1]
    pct = latest / total_images * 100 if total_images else 0

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="{pad_left}" y="24" font-size="18" font-family="Arial, sans-serif" fill="#0f172a">Labelme 标注进度趋势：{latest}/{total_images} ({pct:.1f}%)</text>
  <line x1="{pad_left}" y1="{pad_top + chart_h}" x2="{width - pad_right}" y2="{pad_top + chart_h}" stroke="#cbd5e1"/>
  <line x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{pad_top + chart_h}" stroke="#cbd5e1"/>
  <text x="{pad_left - 12}" y="{pad_top + 5}" text-anchor="end" font-size="12" fill="#64748b">{max_y}</text>
  <text x="{pad_left - 12}" y="{pad_top + chart_h + 4}" text-anchor="end" font-size="12" fill="#64748b">0</text>
  <polyline points="{polyline}" fill="none" stroke="#2563eb" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>
  {circles}
  {labels}
</svg>
'''
    with open(os.path.join(BASE_DIR, "progress_chart.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


def build_readme(config, history, completed, total_images, now_str):
    remaining = max(total_images - completed, 0)
    pct = completed / total_images * 100 if total_images else 0
    owner = config.get("github_owner", "JacksonLuLu03")
    repo = config.get("github_repo", "26.7.10.ShanXi")
    project = config.get("project_name", repo)
    title = config.get("display_title", "标注项目进度")
    cache_buster = int(time.time())

    lines = [
        f"# {title} ({project})",
        "",
        "> [!NOTE]",
        "> 本仓库按完整交付目录组织：图片放在 `images/`，Labelme 标注 JSON 放在 `annotations/`。图片总数在 `config.json` 中配置，GitHub Actions 会在每次推送时自动统计 `annotations/` 中的 JSON 数量并更新此看板。",
        "",
        "### 标注状态看板",
        "",
        "| 统计项 | 数值 | 占比 / 进度条 |",
        "| :--- | :---: | :--- |",
        f"| **总图片数 (Total)** | **{total_images}** | `[{progress_bar(total_images, total_images)}]` 100.0% |",
        f"| **已标记 (Completed)** | **{completed}** | `[{progress_bar(completed, total_images)}]` {pct:.1f}% |",
        f"| **未标记 (Remaining)** | **{remaining}** | `[{progress_bar(remaining, total_images)}]` {100 - pct:.1f}% |",
        "",
        "**当前总体进度：**",
        f"![Progress Badge](https://img.shields.io/badge/Progress-{completed}%20%2F%20{total_images}%20({pct:.1f}%25)-blue?style=for-the-badge&logo=github)",
        "",
        "### 标注进度趋势折线图",
        "![标注进度趋势](progress_chart.svg)",
        "",
        "### 目录结构",
        "",
        "- `images/`：本地完整图片文件，用于打包交付；默认不上传到 GitHub。",
        "- `annotations/`：Labelme JSON 标注文件，GitHub 看板统计这个目录。",
        "- `sync_from_labelme.ps1`：从 `E:\\Labelme\\3卢杰` 同步图片和 JSON，并更新看板。",
        "- `watch_labelme_and_push.ps1`：运行时每 20 秒监听一次 JSON 变化，自动同步并推送。",
        "",
        "---",
        f"_最后更新：{now_str} (UTC+8)_",
        "",
        "### 每日标注聚合日志",
        "",
    ]

    daily = history.get("daily_stats", {})
    latest_day = sorted(daily.keys())[-1] if daily else None
    if not daily:
        lines.append("暂无历史记录。")
    for day in sorted(daily.keys(), reverse=True):
        item = daily[day]
        total = int(item.get("total_completed", 0))
        day_pct = total / total_images * 100 if total_images else 0
        new_files = item.get("new_files", [])
        strengthened = item.get("strengthened_files", [])
        lines.extend(
            [
                "<details open>" if day == latest_day else "<details>",
                f"<summary><b>{day}</b> : 进度 {total}/{total_images} ({day_pct:.1f}%) | 新增 {len(new_files)} | 加强 {len(strengthened)}</summary>",
                "",
            ]
        )
        if new_files:
            lines.extend(["**新增文件**", "", ", ".join(f"`{short_name(f)}`" for f in sorted(new_files)), ""])
        if strengthened:
            lines.extend(["**加强文件**", "", ", ".join(f"`{short_name(f)}`" for f in sorted(strengthened)), ""])
        lines.extend(["</details>", ""])

    return "\n".join(lines)


def main():
    today, now_str = beijing_now()
    config = read_json(os.path.join(BASE_DIR, "config.json"), {})
    total_images = int(config.get("total_images", 0))
    history = read_json(os.path.join(BASE_DIR, "progress_history.json"), {"file_hashes": {}, "daily_stats": {}})
    history.setdefault("file_hashes", {})
    history.setdefault("daily_stats", {})

    current_files = list_label_jsons()
    current_hashes = {f: file_hash(os.path.join(ANNOTATIONS_DIR, f)) for f in current_files}
    old_hashes = history.get("file_hashes", {})
    new_files = [f for f in current_files if f not in old_hashes]
    strengthened = [f for f in current_files if f in old_hashes and old_hashes[f] != current_hashes[f]]

    item = history["daily_stats"].setdefault(today, {"total_completed": 0, "new_files": [], "strengthened_files": []})
    item["total_completed"] = len(current_files)
    item["new_files"] = sorted(set(item.get("new_files", []) + new_files))
    item["strengthened_files"] = sorted(set(item.get("strengthened_files", []) + strengthened))
    history["file_hashes"] = current_hashes

    write_json(os.path.join(BASE_DIR, "progress_history.json"), history)
    build_svg(history, total_images)
    with open(os.path.join(BASE_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(build_readme(config, history, len(current_files), total_images, now_str))
        f.write("\n")


if __name__ == "__main__":
    main()
