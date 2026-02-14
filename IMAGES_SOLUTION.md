# 自托管图片解决方案说明 / Self-Hosted Images Solution

[English](#english) | [中文](#chinese)

## <a name="chinese"></a>中文说明

### 问题
- `camo.githubusercontent.com` 和 `github-readme-stats.vercel.app` 的图片无法加载
- 外部服务的可靠性和访问速度问题

### 解决方案
本仓库现在使用**完全自主的统计图片生成方案**，不依赖任何第三方服务：

1. **自定义统计生成脚本**：`scripts/generate_stats.py`
   - 直接使用 GitHub API 获取数据
   - 生成精美的 SVG 统计卡片
   - 支持自定义样式和布局

2. **GitHub Actions 自动化工作流**：每天自动更新统计图片
   - 文件位置：`.github/workflows/update-stats.yml`
   - 运行时间：每天 UTC 00:00
   - 也可以手动触发运行

3. **本地图片存储**：所有图片存储在 `assets/` 目录
   - `stats.svg` - GitHub 统计卡片（仓库数、star、fork、关注者等）
   - `top-langs.svg` - 常用编程语言统计
   - `simple-my-blog-pin.svg` - simple-my-blog 仓库卡片
   - `linx-pin.svg` - Linx 仓库卡片

4. **README 更新**：所有图片引用已更新为本地路径

### 功能特点

- ✅ **完全自主**：不依赖任何第三方服务（vercel.app、camo等）
- ✅ **使用 GitHub API**：直接从 GitHub 获取最新数据
- ✅ **自动更新**：每天自动运行，保持数据最新
- ✅ **可靠稳定**：图片存储在仓库中，永远可访问
- ✅ **高度可定制**：可以自由修改脚本来调整样式和内容
- ✅ **无限制**：不受第三方服务限流影响

### 如何手动触发更新

1. 进入 GitHub 仓库页面
2. 点击 "Actions" 标签
3. 选择 "Update Stats Images" 工作流
4. 点击 "Run workflow" 按钮
5. 选择分支并运行

### 自定义统计卡片

如果需要修改统计卡片的样式、颜色或内容：

1. 编辑 `scripts/generate_stats.py` 文件
2. 修改相应的生成函数：
   - `generate_stats_card()` - 修改统计卡片样式
   - `generate_languages_card()` - 修改语言卡片样式
   - `generate_repo_pin_card()` - 修改仓库卡片样式
3. 提交更改后，工作流会在下次运行时使用新样式

### 添加更多仓库卡片

要显示更多仓库的卡片：

1. 编辑 `scripts/generate_stats.py` 文件
2. 在 `repos_to_pin` 列表中添加仓库：
   ```python
   repos_to_pin = [
       ('simple-my-blog', 'simple-my-blog-pin.svg'),
       ('Linx', 'linx-pin.svg'),
       ('your-new-repo', 'your-new-repo-pin.svg')  # 添加这里
   ]
   ```
3. 在 README.md 中添加对应的图片引用

---

## <a name="english"></a>English

### Problem
- Images from `camo.githubusercontent.com` and `github-readme-stats.vercel.app` cannot load
- Reliability and access speed issues with external services

### Solution
This repository now uses a **completely autonomous stats generation solution** without any third-party dependencies:

1. **Custom Stats Generation Script**: `scripts/generate_stats.py`
   - Directly uses GitHub API to fetch data
   - Generates beautiful SVG stats cards
   - Supports custom styling and layouts

2. **GitHub Actions Automated Workflow**: Automatically updates stats images daily
   - Location: `.github/workflows/update-stats.yml`
   - Schedule: Daily at 00:00 UTC
   - Can also be triggered manually

3. **Local Image Storage**: All images stored in `assets/` directory
   - `stats.svg` - GitHub stats card (repos, stars, forks, followers, etc.)
   - `top-langs.svg` - Top programming languages statistics
   - `simple-my-blog-pin.svg` - simple-my-blog repository card
   - `linx-pin.svg` - Linx repository card

4. **README Updates**: All image references updated to local paths

### Features

- ✅ **Fully Autonomous**: No dependency on third-party services (vercel.app, camo, etc.)
- ✅ **Uses GitHub API**: Fetches latest data directly from GitHub
- ✅ **Automatic Updates**: Runs daily to keep data fresh
- ✅ **Reliable & Stable**: Images stored in repository, always accessible
- ✅ **Highly Customizable**: Freely modify scripts to adjust styles and content
- ✅ **No Limits**: Not affected by third-party service rate limits

### How to Manually Trigger Update

1. Go to your GitHub repository page
2. Click on "Actions" tab
3. Select "Update Stats Images" workflow
4. Click "Run workflow" button
5. Select branch and run

### Customize Stats Cards

To modify the style, colors, or content of stats cards:

1. Edit `scripts/generate_stats.py` file
2. Modify the corresponding generation functions:
   - `generate_stats_card()` - Modify stats card style
   - `generate_languages_card()` - Modify languages card style
   - `generate_repo_pin_card()` - Modify repository card style
3. After committing changes, the workflow will use new styles on next run

### Add More Repository Cards

To display more repository cards:

1. Edit `scripts/generate_stats.py` file
2. Add repositories to the `repos_to_pin` list:
   ```python
   repos_to_pin = [
       ('simple-my-blog', 'simple-my-blog-pin.svg'),
       ('Linx', 'linx-pin.svg'),
       ('your-new-repo', 'your-new-repo-pin.svg')  # Add here
   ]
   ```
3. Add corresponding image references in README.md

### Technical Details

The solution consists of:
- **Python script** that uses GitHub REST API v3
- **SVG generation** with inline styles for GitHub dark theme
- **Automatic commits** via GitHub Actions bot
- **Error handling** with fallback values when API is unavailable
