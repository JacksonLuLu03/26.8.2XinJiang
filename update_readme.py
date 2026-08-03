# -*- coding: utf-8 -*-
import datetime
import hashlib
import html
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


def nice_axis_max(value):
    if value <= 10:
        return 10
    if value <= 50:
        step = 10
    elif value <= 100:
        step = 20
    else:
        step = 50
    return ((value + step - 1) // step) * step


def snapshot_label(timestamp):
    parts = timestamp.split(" ")
    if len(parts) == 2:
        day = parts[0][5:]
        hour_minute = ":".join(parts[1].split(":")[:2])
        return f"{day} {hour_minute}"
    return timestamp[5:] if len(timestamp) >= 10 else timestamp


def chart_points(history):
    snapshots = history.get("snapshots", [])
    points = []
    if isinstance(snapshots, list):
        for item in snapshots:
            timestamp = str(item.get("time", ""))
            try:
                value = int(item.get("total_completed", 0))
            except Exception:
                value = 0
            if timestamp:
                points.append((timestamp, value))

    if points:
        return points[-14:]

    daily = history.get("daily_stats", {})
    for day in sorted(daily):
        points.append((day, int(daily[day].get("total_completed", 0))))
    return points


def build_svg(history, total_images):
    points = chart_points(history)
    if not points:
        points = [(beijing_now()[1], 0)]

    width, height = 980, 390
    pad_left, pad_right, pad_top, pad_bottom = 76, 44, 72, 72
    chart_w = width - pad_left - pad_right
    chart_h = height - pad_top - pad_bottom
    latest = points[-1][1]
    max_value = max(v for _, v in points)
    max_y = nice_axis_max(max(max_value + 4, 10))

    coords = []
    for i, (_, value) in enumerate(points):
        x = pad_left + (chart_w * i / max(len(points) - 1, 1))
        y = pad_top + chart_h - (chart_h * value / max_y)
        coords.append((x, y))

    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    area_points = f"{pad_left:.1f},{pad_top + chart_h:.1f} {polyline} {pad_left + chart_w:.1f},{pad_top + chart_h:.1f}"
    pct = latest / total_images * 100 if total_images else 0

    grid_lines = []
    y_labels = []
    for i in range(5):
        value = round(max_y * i / 4)
        y = pad_top + chart_h - (chart_h * value / max_y)
        grid_lines.append(f'<line x1="{pad_left}" y1="{y:.1f}" x2="{width - pad_right}" y2="{y:.1f}" stroke="#e2e8f0" stroke-width="1" />')
        y_labels.append(f'<text x="{pad_left - 14}" y="{y + 4:.1f}" text-anchor="end" font-size="12" fill="#64748b">{value}</text>')

    nodes = []
    x_labels = []
    for idx, ((timestamp, value), (x, y)) in enumerate(zip(points, coords)):
        label = html.escape(snapshot_label(timestamp))
        tag_y = y - 26 if idx % 2 == 0 else y + 35
        tag_y = max(38, min(height - 98, tag_y))
        tag_w = 46 if value < 100 else 54
        nodes.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{tag_y:.1f}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 4" />')
        nodes.append(f'<rect x="{x - tag_w / 2:.1f}" y="{tag_y - 17:.1f}" width="{tag_w}" height="24" rx="7" fill="#0f172a" />')
        nodes.append(f'<text x="{x:.1f}" y="{tag_y - 1:.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">{value}</text>')
        nodes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="#ffffff" stroke="#2563eb" stroke-width="3" />')
        nodes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#14b8a6" />')
        x_labels.append(f'<text x="{x:.1f}" y="{height - 32}" text-anchor="middle" font-size="12" fill="#475569">{label}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#2563eb" />
      <stop offset="100%" stop-color="#14b8a6" />
    </linearGradient>
    <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#93c5fd" stop-opacity="0.38" />
      <stop offset="100%" stop-color="#ccfbf1" stop-opacity="0.05" />
    </linearGradient>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#0f172a" flood-opacity="0.12" />
    </filter>
  </defs>
  <rect width="100%" height="100%" rx="16" fill="#f8fafc"/>
  <rect x="18" y="18" width="{width - 36}" height="{height - 36}" rx="14" fill="#ffffff" filter="url(#softShadow)"/>
  <text x="{pad_left}" y="42" font-size="22" font-weight="800" font-family="Arial, sans-serif" fill="#0f172a">Labelme 标注进度趋势</text>
  <text x="{pad_left}" y="64" font-size="13" font-family="Arial, sans-serif" fill="#64748b">当前累计 {latest}/{total_images}，完成 {pct:.1f}%。节点标签显示每次同步后的累计标注数。</text>
  {"".join(grid_lines)}
  <line x1="{pad_left}" y1="{pad_top + chart_h}" x2="{width - pad_right}" y2="{pad_top + chart_h}" stroke="#94a3b8" stroke-width="1.2"/>
  <line x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{pad_top + chart_h}" stroke="#94a3b8" stroke-width="1.2"/>
  {"".join(y_labels)}
  <polygon points="{area_points}" fill="url(#areaGradient)" />
  <polyline points="{polyline}" fill="none" stroke="url(#lineGradient)" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>
  {"".join(nodes)}
  {"".join(x_labels)}
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
    history.setdefault("snapshots", [])

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

    snapshots = history.setdefault("snapshots", [])
    if not snapshots:
        for day in sorted(history["daily_stats"]):
            snapshots.append({
                "time": day,
                "total_completed": int(history["daily_stats"][day].get("total_completed", 0)),
            })
    if not snapshots or int(snapshots[-1].get("total_completed", -1)) != len(current_files):
        snapshots.append({"time": now_str, "total_completed": len(current_files)})

    write_json(os.path.join(BASE_DIR, "progress_history.json"), history)
    build_svg(history, total_images)
    with open(os.path.join(BASE_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(build_readme(config, history, len(current_files), total_images, now_str))
        f.write("\n")


if __name__ == "__main__":
    main()
