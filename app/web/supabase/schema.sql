-- Dejo Guard hosted data (Supabase project dejo-guard). Applied 16 Oct 2026. RLS on, no policies:
-- only the server (secret key) reads or writes. Card numbers are never stored — only the last 4 of a sandbox card.
create table if not exists public.carts (id uuid primary key default gen_random_uuid(), items jsonb not null default '[]'::jsonb, updated_at timestamptz not null default now());
create table if not exists public.orders (id text primary key, cart_id uuid, items jsonb not null, total_inr integer not null, name text, city text, card_last4 text, created_at timestamptz not null default now());
create table if not exists public.feeds (id text primary key, token_hash text not null unique, label text, created_at timestamptz not null default now());
create table if not exists public.decisions (id text primary key, feed_id text not null references public.feeds(id) on delete cascade, at double precision not null, task_id text, goal text, action text not null, cls text not null, because text, decision text not null, reason text, policy text, delegation_id text, plan_id text, page_url text, words text, ms integer, facts jsonb, received_at timestamptz not null default now());
create index if not exists decisions_feed_at on public.decisions(feed_id, at desc);
alter table public.carts enable row level security;
alter table public.orders enable row level security;
alter table public.feeds enable row level security;
alter table public.decisions enable row level security;
