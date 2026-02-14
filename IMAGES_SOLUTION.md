# 自托管图片解决方案说明 / Self-Hosted Images Solution

[English](#english) | [中文](#chinese)

## <a name="chinese"></a>中文说明

### 问题
- `camo.githubusercontent.com` 和 `github-readme-stats.vercel.app` 的图片无法加载
- 外部服务的可靠性和访问速度问题

### 解决方案
本仓库现在使用自托管的图片解决方案：

1. **GitHub Actions 工作流**：每天自动更新统计图片
   - 文件位置：`.github/workflows/update-stats.yml`
   - 运行时间：每天 UTC 00:00
   - 也可以手动触发运行

2. **本地图片存储**：所有图片存储在 `assets/` 目录
   - `stats.svg` - GitHub 统计卡片
   - `top-langs.svg` - 常用语言统计
   - `simple-my-blog-pin.svg` - simple-my-blog 仓库卡片
   - `linx-pin.svg` - Linx 仓库卡片

3. **README 更新**：所有图片引用已更新为本地路径

### 如何手动触发更新

1. 进入 GitHub 仓库页面
2. 点击 "Actions" 标签
3. 选择 "Update Stats Images" 工作流
4. 点击 "Run workflow" 按钮
5. 选择分支并运行

### 自定义

如果需要修改统计卡片的样式或参数：

1. 编辑 `.github/workflows/update-stats.yml` 文件
2. 在 `images` 字典中修改 URL 参数
3. 提交更改后，工作流会在下次运行时使用新参数

---

## <a name="english"></a>English

### Problem
- Images from `camo.githubusercontent.com` and `github-readme-stats.vercel.app` cannot load
- Reliability and access speed issues with external services

### Solution
This repository now uses a self-hosted images solution:

1. **GitHub Actions Workflow**: Automatically updates stats images daily
   - Location: `.github/workflows/update-stats.yml`
   - Schedule: Daily at 00:00 UTC
   - Can also be triggered manually

2. **Local Image Storage**: All images stored in `assets/` directory
   - `stats.svg` - GitHub stats card
   - `top-langs.svg` - Top languages card
   - `simple-my-blog-pin.svg` - simple-my-blog repository card
   - `linx-pin.svg` - Linx repository card

3. **README Updates**: All image references updated to local paths

### How to Manually Trigger Update

1. Go to your GitHub repository page
2. Click on "Actions" tab
3. Select "Update Stats Images" workflow
4. Click "Run workflow" button
5. Select branch and run

### Customization

To modify the style or parameters of stats cards:

1. Edit `.github/workflows/update-stats.yml` file
2. Modify URL parameters in the `images` dictionary
3. After committing changes, the workflow will use new parameters on next run

### Benefits

- ✅ **Reliable**: Images are stored in your repository, always accessible
- ✅ **Fast**: No dependency on external services
- ✅ **Automatic**: Updates daily without manual intervention
- ✅ **Customizable**: Easy to modify parameters and styles
- ✅ **Self-contained**: All dependencies managed within the repository
