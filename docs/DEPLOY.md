# 发布 KISIV AI 项目首页

项目包含独立首页 `index.html`，并使用 GitHub Pages 自动部署工作流。

## 自动部署

工作流文件：`.github/workflows/deploy-pages.yml`

向 `main` 分支推送首页或文档变更后，会自动触发部署；也可以在 GitHub 仓库的 **Actions** 页面手动运行 **Deploy KISIV AI homepage to GitHub Pages**。

首次启用时，请打开仓库 **Settings → Pages**，将 **Build and deployment → Source** 设置为 **GitHub Actions**。之后在 Actions 页面确认部署工作流成功。

当前仓库名为 `aegis-ai` 时，预期站点地址为：

https://xiaoxuan0820-ctrl.github.io/aegis-ai/

如果仓库重命名为 `kisiv-ai`，预期地址会变为：

https://xiaoxuan0820-ctrl.github.io/kisiv-ai/

请以 GitHub Pages 设置中显示的实际 URL 为准。工作流已提交并不等于站点已成功发布；必须等待 Actions 运行成功后再对外分享。

## 本地检查

直接在浏览器打开仓库根目录的 `index.html` 即可预览页面。站点使用相对路径引用 `docs/images/` 下的 SVG 图像。
