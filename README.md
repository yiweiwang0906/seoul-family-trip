# 首尔，三个人的秋天

2026/10/2–10/6 两大一小的中文旅行手册。无构建依赖、无后端、无追踪；静态 HTML / CSS / JavaScript，原创 SVG 插画。

## 本地预览

在本目录运行 `python -m http.server 8765 --bind 127.0.0.1`，打开 http://127.0.0.1:8765/ 。直接打开 index.html 也能阅读，但离线缓存与剪贴板最好使用 HTTP 或 HTTPS。

## 使用

- 17 张景点卡可筛选、收藏并添加到上午／下午／晚上，初始行程为空。
- 10/2 抵达提醒；10/6 返程保护日不添加游览。午休可调整。
- 编辑活动时间、时长、日期、备注与预约记录；顺序按钮只改变显示顺序。
- 预约标记来自用户手动记录，不代表网站查到空位或确认订单。
- 收藏、行程与清单保存在当前浏览器；导出／导入 JSON 与家人交换，导入确认后替换。
- 打印生成整个旅行手册。第一次联网后可以离线阅读，外部地图、订位和最新资料仍需网络。

## 资料与更新

攻略核实日期为 2026/9/27，来源在地点详情及各专题页面。天气是韩国气象厅 2026/9/27 06:00 KST 发布的快照，不是实时 API；超过24小时标记旧预报。修改 `data.js` 更新内容，并同时更新页面中的核实说明。交通、餐费为规划估算，未对目标时段执行预约或购买。

## 发布

仅在此子目录初始化 Git；不要把上级目录中的酒店确认函和机票图片加入仓库。

1. `gh auth login --hostname github.com --web` 完成用户登录。
2. 创建公开仓库 `seoul-family-trip`，推送本目录到 main。
3. 在仓库 Settings → Pages 将 Source 设为 GitHub Actions。
4. 运行随仓库提供的 Publish travel guide workflow。

工作流只发布7个明确列出的网页文件，不发布测试、说明文档和原始资料。GitHub Pages 子路径使用相对资源地址。

## 检查

`node --check app.js`、`node --check data.js`、`node --check sw.js`。

浏览器测试使用 Python Playwright：在项目父目录启动端口8765服务后，运行 `python seoul-family-trip/tests/browser_test.py`。默认访问 `/seoul-family-trip/`，可通过 `TRIP_TEST_URL` 覆盖。截图保存到被 Git 忽略的 `test-results`。
