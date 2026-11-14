# SPDX-FileCopyrightText: 2026 QuanRule Contributors
# SPDX-License-Identifier: Apache-2.0

-- ============================================================
-- 增量脚本：服务器状态表（让服务端电脑主动上报，最准）
-- 如果你已经跑过 schema.sql，只需要在 Supabase 的 SQL Editor 里
-- 再跑这一个文件即可。
-- ============================================================

create table if not exists public.server_status (
  id int primary key default 1,
  online boolean not null default false,
  player_count int not null default 0,
  max_players int not null default 0,
  player_names text,
  updated_at timestamptz not null default now(),
  constraint single_row check (id = 1)
);

alter table public.server_status enable row level security;

drop policy if exists "状态公开可读" on public.server_status;
create policy "状态公开可读" on public.server_status
  for select using (true);

drop policy if exists "允许上报状态" on public.server_status;
create policy "允许上报状态" on public.server_status
  for insert to anon with check (true);

drop policy if exists "允许更新状态" on public.server_status;
create policy "允许更新状态" on public.server_status
  for update to anon using (true);

insert into public.server_status (id) values (1) on conflict do nothing;
