// SPDX-FileCopyrightText: 2026 QuanRule Contributors
// SPDX-License-Identifier: Apache-2.0

// 全规则服务器 · Supabase 反向代理（Netlify Edge Function，Deno 运行时）
//
// 浏览器只访问同源的 /sb/*（域名 www.zyxfwq.online，未被封锁），由本函数在
// Netlify 边缘节点把请求转发到真实的 *.supabase.co（Netlify 服务器能正常访问），
// 再把结果原样返回。anon key、RLS、认证全部照常生效。
//
// 路径映射：
//   /sb/rest/v1/...    -> https://<project>.supabase.co/rest/v1/...
//   /sb/auth/v1/...    -> https://<project>.supabase.co/auth/v1/...
//   /sb/storage/v1/... -> https://<project>.supabase.co/storage/v1/...

const SUPABASE_ORIGIN = "https://pmgqucqqasracmxndjtv.supabase.co";

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "86400",
  };
}

export default async (request) => {
  const reqUrl = new URL(request.url);

  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders() });
  }

  // /sb/rest/v1/... -> /rest/v1/...
  const path = reqUrl.pathname.replace(/^\/sb/, "") || "/";
  const target = SUPABASE_ORIGIN + path + reqUrl.search;

  const headers = new Headers();
  for (const [k, v] of request.headers.entries()) {
    const lower = k.toLowerCase();
    if (lower === "host" || lower === "content-length" || lower === "connection") continue;
    headers.set(k, v);
  }

  const init = { method: request.method, headers };
  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = await request.arrayBuffer();
  }

  try {
    const upstream = await fetch(target, init);
    const respHeaders = new Headers(upstream.headers);
    Object.entries(corsHeaders()).forEach(([k, v]) => respHeaders.set(k, v));
    return new Response(upstream.body, {
      status: upstream.status,
      statusText: upstream.statusText,
      headers: respHeaders,
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: "upstream_fetch_failed", detail: String(e) }), {
      status: 502,
      headers: { "Content-Type": "application/json", ...corsHeaders() },
    });
  }
};
