# 标注项目进度 (26.8.2XinJiang)

> [!NOTE]
> 本仓库按完整交付目录组织：图片放在 `images/`，Labelme 标注 JSON 放在 `annotations/`。图片总数在 `config.json` 中配置，GitHub Actions 会在每次推送时自动统计 `annotations/` 中的 JSON 数量并更新此看板。

### 标注状态看板

| 统计项 | 数值 | 占比 / 进度条 |
| :--- | :---: | :--- |
| **总图片数 (Total)** | **403** | `[████████████████████]` 100.0% |
| **已标记 (Completed)** | **66** | `[███░░░░░░░░░░░░░░░░░]` 16.4% |
| **未标记 (Remaining)** | **337** | `[█████████████████░░░]` 83.6% |

**当前总体进度：**
![Progress Badge](https://img.shields.io/badge/Progress-66%20%2F%20403%20(16.4%25)-blue?style=for-the-badge&logo=github)

### 标注进度趋势折线图
![标注进度趋势](progress_chart.svg)

### 目录结构

- `images/`：本地完整图片文件，用于打包交付；默认不上传到 GitHub。
- `annotations/`：Labelme JSON 标注文件，GitHub 看板统计这个目录。
- `sync_from_labelme.ps1`：从 `E:\Labelme\3卢杰` 同步图片和 JSON，并更新看板。
- `watch_labelme_and_push.ps1`：运行时每 20 秒监听一次 JSON 变化，自动同步并推送。

---
_最后更新：2026-08-04 19:16:34 (UTC+8)_

### 每日标注聚合日志

<details open>
<summary><b>2026-08-04</b> : 进度 66/403 (16.4%) | 新增 23 | 加强 18</summary>

**新增文件**

`XinJiang-博湖县-1-4`, `XinJiang-博湖县-1-6`, `XinJiang-博湖县-3-3`, `XinJiang-博湖县-6-1`, `XinJiang-博湖县-6-2`, `XinJiang-博湖县-6-3`, `XinJiang-博湖县-6-4`, `XinJiang-博湖县-6-5`, `XinJiang-博湖县-6-6`, `XinJiang-博湖县-7-1`, `XinJiang-拜城县-15-13`, `XinJiang-拜城县-26-34`, `XinJiang-拜城县-26-35`, `XinJiang-拜城县-26-36`, `XinJiang-拜城县-27-12`, `XinJiang-拜城县-27-13`, `XinJiang-拜城县-27-2`, `XinJiang-拜城县-33-45`, `XinJiang-拜城县-33-7`, `XinJiang-拜城县-34-43`, `XinJiang-拜城县-34-44`, `XinJiang-拜城县-34-45`, `XinJiang-拜城县-35-45`

**加强文件**

`XinJiang-博湖县-6-5`, `XinJiang-巴楚县-16-22`, `XinJiang-巴楚县-19-23`, `XinJiang-拜城县-15-13`, `XinJiang-拜城县-27-2`, `XinJiang-拜城县-35-45`, `XinJiang-拜城县-9-42`, `XinJiang-拜城县-9-43`, `XinJiang-阿克苏市-10-28`, `XinJiang-阿克苏市-16-10`, `XinJiang-阿克苏市-21-10`, `XinJiang-阿克苏市-21-5`, `XinJiang-阿克苏市-22-9`, `XinJiang-阿瓦提县-6-7`, `XinJiang-阿瓦提县-6-8`, `XinJiang-阿瓦提县-7-9`, `XinJiang-阿瓦提县-8-1`, `XinJiang-阿瓦提县-8-2`

</details>

<details>
<summary><b>2026-08-03</b> : 进度 43/403 (10.7%) | 新增 28 | 加强 28</summary>

**新增文件**

`XinJiang-巴楚县-11-32`, `XinJiang-巴楚县-15-27`, `XinJiang-巴楚县-15-28`, `XinJiang-巴楚县-15-29`, `XinJiang-巴楚县-16-15`, `XinJiang-巴楚县-16-16`, `XinJiang-巴楚县-16-18`, `XinJiang-巴楚县-16-19`, `XinJiang-巴楚县-16-22`, `XinJiang-巴楚县-19-21`, `XinJiang-巴楚县-19-23`, `XinJiang-巴楚县-2-52`, `XinJiang-巴楚县-2-53`, `XinJiang-巴楚县-2-54`, `XinJiang-巴楚县-22-6`, `XinJiang-巴楚县-3-52`, `XinJiang-巴楚县-5-53`, `XinJiang-拜城县-9-42`, `XinJiang-拜城县-9-43`, `XinJiang-阿瓦提县-1-7`, `XinJiang-阿瓦提县-10-11`, `XinJiang-阿瓦提县-13-5`, `XinJiang-阿瓦提县-14-4`, `XinJiang-阿瓦提县-7-3`, `XinJiang-阿瓦提县-7-9`, `XinJiang-阿瓦提县-8-1`, `XinJiang-阿瓦提县-8-2`, `XinJiang-阿瓦提县-8-6`

**加强文件**

`XinJiang-巴楚县-15-27`, `XinJiang-巴楚县-15-28`, `XinJiang-巴楚县-15-29`, `XinJiang-巴楚县-16-15`, `XinJiang-巴楚县-16-16`, `XinJiang-巴楚县-16-19`, `XinJiang-巴楚县-16-22`, `XinJiang-巴楚县-22-6`, `XinJiang-巴楚县-5-53`, `XinJiang-拜城县-9-42`, `XinJiang-阿克苏市-10-28`, `XinJiang-阿克苏市-16-10`, `XinJiang-阿克苏市-21-10`, `XinJiang-阿克苏市-21-5`, `XinJiang-阿克苏市-21-6`, `XinJiang-阿克苏市-22-9`, `XinJiang-阿克苏市-24-10`, `XinJiang-阿克苏市-3-23`, `XinJiang-阿克苏市-5-20`, `XinJiang-阿瓦提县-10-11`, `XinJiang-阿瓦提县-14-4`, `XinJiang-阿瓦提县-3-7`, `XinJiang-阿瓦提县-5-3`, `XinJiang-阿瓦提县-5-4`, `XinJiang-阿瓦提县-5-7`, `XinJiang-阿瓦提县-6-7`, `XinJiang-阿瓦提县-6-8`, `XinJiang-阿瓦提县-8-1`

</details>

<details>
<summary><b>2026-08-02</b> : 进度 15/403 (3.7%) | 新增 15 | 加强 0</summary>

**新增文件**

`XinJiang-阿克苏市-10-28`, `XinJiang-阿克苏市-16-10`, `XinJiang-阿克苏市-21-10`, `XinJiang-阿克苏市-21-5`, `XinJiang-阿克苏市-21-6`, `XinJiang-阿克苏市-22-9`, `XinJiang-阿克苏市-24-10`, `XinJiang-阿克苏市-3-23`, `XinJiang-阿克苏市-5-20`, `XinJiang-阿瓦提县-3-7`, `XinJiang-阿瓦提县-5-3`, `XinJiang-阿瓦提县-5-4`, `XinJiang-阿瓦提县-5-7`, `XinJiang-阿瓦提县-6-7`, `XinJiang-阿瓦提县-6-8`

</details>

