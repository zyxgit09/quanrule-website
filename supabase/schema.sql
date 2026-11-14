# SPDX-FileCopyrightText: 2026 QuanRule Contributors
# SPDX-License-Identifier: Apache-2.0

-- ============================================================
-- 全规则服务器官网 · Supabase 数据库建表脚本
-- 使用方法：在 Supabase 控制台左侧 SQL Editor 里整段粘贴运行
-- ============================================================

-- ---------- 1. 用户档案表（和系统登录账号 auth.users 自动关联） ----------
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  player_name text,
  created_at timestamptz not null default now()
);

-- 新用户注册后自动建立一条档案
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, email, player_name)
  values (new.id, new.email, null)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------- 2. 私信表 ----------
create table if not exists public.messages (
  id bigint generated always as identity primary key,
  sender_id uuid not null references auth.users(id) on delete cascade,
  sender_name text not null,
  receiver_id uuid references auth.users(id) on delete set null,
  receiver_name text not null,
  content text not null,
  is_read boolean not null default false,
  created_at timestamptz not null default now()
);

-- ---------- 3. 寒假24小时开服投票表 ----------
create table if not exists public.votes_winter24 (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  player_name text not null,
  vote boolean not null default true,
  created_at timestamptz not null default now(),
  unique (user_id)
);

-- ---------- 4. 福利领取记录表 ----------
create table if not exists public.reward_claims (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  player_name text not null,
  reward_type text not null,
  created_at timestamptz not null default now(),
  unique (user_id, reward_type)
);

-- ---------- 5. 管理员竞选申请表 ----------
create table if not exists public.admin_applications (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  player_name text not null,
  play_time text not null,
  reason text not null,
  online_time text not null,
  status text not null default '待审核',
  created_at timestamptz not null default now()
);

-- ============================================================
-- 行级安全策略（RLS）：保证每个人只能看到/操作自己的数据
-- ============================================================
alter table public.profiles enable row level security;
alter table public.messages enable row level security;
alter table public.votes_winter24 enable row level security;
alter table public.reward_claims enable row level security;
alter table public.admin_applications enable row level security;

-- profiles：登录后可读；本人可改
drop policy if exists "profiles read" on public.profiles;
create policy "profiles read" on public.profiles
  for select using (auth.role() = 'authenticated');
drop policy if exists "profiles update own" on public.profiles;
create policy "profiles update own" on public.profiles
  for update using (auth.uid() = id);

-- messages：只能看/发自己作为发件人或收件人的消息
drop policy if exists "messages own read" on public.messages;
create policy "messages own read" on public.messages
  for select using (auth.uid() = sender_id or auth.uid() = receiver_id);
drop policy if exists "messages own insert" on public.messages;
create policy "messages own insert" on public.messages
  for insert with check (auth.uid() = sender_id);
drop policy if exists "messages receiver update" on public.messages;
create policy "messages receiver update" on public.messages
  for update using (auth.uid() = receiver_id);

-- votes：本人可投，所有登录用户可看汇总
drop policy if exists "votes read" on public.votes_winter24;
create policy "votes read" on public.votes_winter24
  for select using (auth.role() = 'authenticated');
drop policy if exists "votes own insert" on public.votes_winter24;
create policy "votes own insert" on public.votes_winter24
  for insert with check (auth.uid() = user_id);

-- reward_claims：只能看/写自己的领取记录
drop policy if exists "rewards own read" on public.reward_claims;
create policy "rewards own read" on public.reward_claims
  for select using (auth.uid() = user_id);
drop policy if exists "rewards own insert" on public.reward_claims;
create policy "rewards own insert" on public.reward_claims
  for insert with check (auth.uid() = user_id);

-- admin_applications：只能看/写自己的申请
drop policy if exists "admin own read" on public.admin_applications;
create policy "admin own read" on public.admin_applications
  for select using (auth.uid() = user_id);
drop policy if exists "admin own insert" on public.admin_applications;
create policy "admin own insert" on public.admin_applications
  for insert with check (auth.uid() = user_id);
