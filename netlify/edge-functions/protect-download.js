// 全规则服务器 · 启动器下载保护（Netlify Edge Function，Deno 运行时）
//
// 拦截 /downloads/QuanRuleLauncher.exe：
//   - 读取浏览器同源 cookie 里的 launcher_token（登录后由前端写入的 Supabase access_token）
//   - 调用 Supabase /auth/v1/user 验证 token 是否有效
//   - 有效：context.next() 放行，由 Netlify 正常返回静态文件（保留断点续传/Range）
//   - 无效或没有：直接 403，不返回文件内容，避免未登录的爬虫/陌生人反复下载浪费流量

const SUPABASE_ORIGIN = "https://pmgqucqqasracmxndjtv.supabase.co";

function deny() {
  return new Response("请先登录后再下载启动器", {
    status: 403,
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}

export default async (request, context) => {
  // 只处理下载入口
  const url = new URL(request.url);
  if (!url.pathname.startsWith("/downloads/")) {
    return context.next();
  }

  const cookie = request.headers.get("cookie") || "";
  const match = cookie.match(/(?:^|;\s*)launcher_token=([^;]+)/);
  if (!match) {
    return deny();
  }

  const token = decodeURIComponent(match[1]);
  try {
    const verify = await fetch(SUPABASE_ORIGIN + "/auth/v1/user", {
      headers: { Authorization: "Bearer " + token },
    });
    if (verify.status !== 200) {
      return deny();
    }
  } catch (e) {
    return deny();
  }

  // 登录有效，继续到静态文件（CDN 高效返回，支持 Range 断点续传）
  return context.next();
};
