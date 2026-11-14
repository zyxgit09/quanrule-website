-- ============================================================
-- 增量脚本：让玩家名称在全服唯一，保证福利/私信能准确锁定到人
-- 前提：已跑过 schema.sql。在 Supabase 的 SQL Editor 里整段运行即可。
-- 说明：Postgres 唯一索引允许多个 NULL，所以尚未绑定名称的账号不受影响。
-- ============================================================

-- 先把玩家名称统一去掉首尾空格，避免“张三 ”和“张三”被当成两个人
update public.profiles set player_name = nullif(btrim(player_name), '');

-- 若已存在重名，先保留最早创建的一条，其余清空，让其重新绑定
update public.profiles p set player_name = null
where p.player_name is not null and exists (
  select 1 from public.profiles q
  where q.player_name = p.player_name
    and q.created_at < p.created_at
);

-- 建立唯一索引：一个玩家名称只能被一个账号绑定
drop index if exists profiles_player_name_key;
create unique index profiles_player_name_key
  on public.profiles (player_name);
