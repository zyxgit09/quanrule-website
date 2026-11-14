# 变更日志（Changelog）

本项目的显著变更记录在此。版本号遵循[语义化版本（SemVer）](https://semver.org/lang/zh-CN/)，并以 Git 标签（tag）标识每次发布。

## 1.0.0 · 2026-11 · 首次开源

- 官网源码以 **Apache License 2.0** 许可证开源
- 新增 `README.md`：项目介绍、功能、技术栈、目录结构与运行方式
- 新增自动化测试套件 `tests/test_website.py`（Python 标准库，无需第三方依赖），
  检查文件完整性、HTML 结构、本地资源引用、许可证与密钥安全
- 新增本变更日志 `CHANGELOG.md`
- 配置 `.gitignore`，排除本地目录、备份与大体积二进制文件

## 网站功能

- 纯静态官网（Minecraft 像素风格，移动端自适应）
- 邮箱注册 / 登录，统一以「玩家名称」识别身份
- 服务器状态与在线人数展示、定时刷新
- 福利、投票、管理员申请、私信等功能
- 基于 Supabase（RLS 行级安全）与 Netlify Edge Function 反向代理

## 安全说明

- 仓库中仅包含可公开的 publishable（anon）密钥，受 RLS 保护
- 不包含任何 service_role 高危密钥或硬编码密码
- 如发现运行时安全漏洞，请通过 GitHub Issues 私密报告
