<!--
SPDX-FileCopyrightText: 2026 QuanRule Contributors
SPDX-License-Identifier: Apache-2.0
-->

# QuanRule Website（全规则服务器官网）

全规则（QuanRule）Minecraft 服务器的官方网站源码。纯静态网页 + 云后端，采用 Minecraft 像素风格，支持手机端自适应。

- 线上地址：<https://www.zyxfwq.online/>
- 游戏服务器地址：`mc.zyxfwq.online`

## 功能

- 服务器介绍、规则与状态展示（在线人数定时刷新）
- 邮箱注册 / 登录，全站统一用「玩家名称」识别身份
- 福利、投票、管理员申请、私信等功能
- 启动器下载（登录后可访问）

## 技术栈

- 前端：原生 HTML / CSS / JavaScript（无构建步骤，单文件 `index.html`）
- 账号与数据库：Supabase（免费云数据库 + 邮箱认证，RLS 行级安全）
- 托管与反向代理：Netlify（免费、自动 HTTPS），用 Edge Function 在云端代理 Supabase
- 状态上报：Python 脚本从服务器本机主动上报在线人数

## 目录结构

```
quanrule-website/
├── index.html                  # 官网（MC 像素风，含认证/读写/状态刷新逻辑）
├── config.js                   # 中转地址 + 可公开的 publishable key
├── netlify.toml                # Edge Function 路由、缓存与安全头
├── netlify/edge-functions/     # sb 反向代理、下载保护（Deno）
├── assets/                     # 图片素材
├── status-reporter/            # 在线人数上报脚本（Python）
└── supabase/                   # 建表 SQL
```

## 本地运行

这是纯静态网站，直接用浏览器打开 `index.html` 即可预览；完整功能（认证、数据库）依赖
Supabase 与 Netlify Edge Function，需按部署说明配置。

## 部署

详见 [`部署说明.md`](部署说明.md)。托管在 Netlify，使用 Edge Function 反向代理 Supabase。

## 许可证

本项目基于 [Apache License 2.0](LICENSE) 发布，包含明确的专利授权条款。
