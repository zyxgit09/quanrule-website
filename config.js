// SPDX-FileCopyrightText: 2026 QuanRule Contributors
// SPDX-License-Identifier: Apache-2.0

// ============================================================
// 全规则服务器官网 · Supabase 配置
//
// 由于本机网络封锁了 *.supabase.co，网站不直连 Supabase，而是走自己域名
// www.zyxfwq.online 上的反向代理（Netlify 函数 /sb），由 Netlify 服务器端
// 转发到 Supabase。anon key 仍填 Supabase 的 publishable key，照常生效。
//
// 密钥获取位置：Supabase 控制台 → Settings → API Keys → Publishable key
// ============================================================
const SUPABASE_URL = "https://www.zyxfwq.online/sb";
const SUPABASE_ANON_KEY = "sb_publishable_J_N7n1jRTHmLbv123h5T4A_1DYuhUJS";
