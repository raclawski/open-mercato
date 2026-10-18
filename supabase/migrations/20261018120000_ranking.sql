-- Postaw Krzyżyk: lista wyników.
--
-- Przeglądarka nie ma bezpośredniego dostępu do tabel (RLS bez polityk + revoke).
-- Zapis i odczyt idą wyłącznie przez funkcje RPC poniżej, które sprawdzają dane:
--   pk_submit_game(p_game jsonb)      zapis zakończonej gry (idempotentny po id)
--   pk_leaderboard(...)               ranking graczy (po nicku, bez kont)
--   pk_recent_games(...)              ostatnie gry, opcjonalnie jednego gracza

create table if not exists public.pk_games (
  id               uuid primary key,
  mode             text not null check (mode in ('live', 'teleturniej')),
  level            text not null check (level ~ '^[a-z]{2,12}$'),
  code             text check (code ~ '^[A-Z0-9]{4,6}$'),
  questions_total  int  not null check (questions_total between 1 and 100),
  questions_played int  not null check (questions_played between 1 and 100 and questions_played <= questions_total),
  penalty          int  not null check (penalty in (1, 5, 10)),
  players_count    int  not null check (players_count between 1 and 16),
  created_at       timestamptz not null default now()
);

create table if not exists public.pk_game_players (
  game_id  uuid not null references public.pk_games (id) on delete cascade,
  name     text not null check (char_length(name) between 1 and 20),
  name_key text not null check (char_length(name_key) between 1 and 20),
  score    int  not null,
  correct  int  not null check (correct >= 0),
  wrong    int  not null check (wrong >= 0),
  place    int  not null check (place >= 1),
  primary key (game_id, name_key)
);

create index if not exists pk_games_created_idx on public.pk_games (created_at desc);
create index if not exists pk_game_players_name_idx on public.pk_game_players (name_key);

alter table public.pk_games enable row level security;
alter table public.pk_game_players enable row level security;
revoke all on public.pk_games, public.pk_game_players from anon, authenticated;

-- Nick: bez znaków sterujących i niewidocznych, przycięty, maks. 20 znaków (jak cleanName w grze).
-- Znaki niewidoczne zapisane jako \uXXXX: wklejone dosłownie potrafią zniknąć przy kopiowaniu do SQL Editora i psuć wyrażenie.
create or replace function public.pk_clean_name(p text)
returns text
language sql immutable
set search_path = ''
as $$
  select left(btrim(regexp_replace(coalesce(p, ''), '[[:cntrl:]\u200B-\u200F\u2028-\u202E\u2060-\u206F\uFEFF]', '', 'g')), 20)
$$;

create or replace function public.pk_parse_players(p jsonb)
returns table (name text, name_key text, score int, correct int, wrong int)
language sql immutable
set search_path = ''
as $$
  select n.name, lower(n.name), x.score, x.correct, x.wrong
  from jsonb_to_recordset(p) as x (name text, score int, correct int, wrong int)
  cross join lateral (select public.pk_clean_name(x.name) as name) n
$$;

create or replace function public.pk_submit_game(p_game jsonb)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_id      uuid;
  v_mode    text := p_game->>'mode';
  v_level   text := p_game->>'level';
  v_code    text := nullif(p_game->>'code', '');
  v_total   int;
  v_played  int;
  v_pen     int;
  v_players jsonb := p_game->'players';
  v_n       int;
  v_bad     text;
begin
  begin
    v_id     := (p_game->>'id')::uuid;
    v_total  := (p_game->>'questions_total')::int;
    v_played := (p_game->>'questions_played')::int;
    v_pen    := (p_game->>'penalty')::int;
  exception when others then
    raise exception 'pk: nieprawidłowe pola gry' using errcode = '22023';
  end;
  if v_id is null or v_total is null or v_played is null or v_pen is null then
    raise exception 'pk: brak wymaganych pól' using errcode = '22023';
  end if;

  if exists (select 1 from public.pk_games where id = v_id) then
    return jsonb_build_object('ok', true, 'id', v_id, 'duplicate', true);
  end if;

  if jsonb_typeof(v_players) is distinct from 'array' then
    raise exception 'pk: players musi być tablicą' using errcode = '22023';
  end if;
  v_n := jsonb_array_length(v_players);
  if v_n < 1 or v_n > 16 then
    raise exception 'pk: od 1 do 16 graczy' using errcode = '22023';
  end if;

  begin
    perform count(*) from public.pk_parse_players(v_players);
  exception when others then
    raise exception 'pk: nieprawidłowe dane graczy' using errcode = '22023';
  end;

  select case
    when exists (select 1 from public.pk_parse_players(v_players) where name = '' or score is null or correct is null or wrong is null) then 'puste pola gracza'
    when (select count(distinct name_key) from public.pk_parse_players(v_players)) <> v_n then 'powtórzone imiona'
    when exists (select 1 from public.pk_parse_players(v_players) where correct < 0 or wrong < 0) then 'ujemne liczniki'
    -- wynik musi wynikać z odpowiedzi: +10 za dobrą, −kara za złą
    when exists (select 1 from public.pk_parse_players(v_players) where score <> 10 * correct - v_pen * wrong) then 'wynik nie zgadza się z odpowiedziami'
    -- każde pytanie ma najwyżej jedną dobrą odpowiedź
    when (select sum(correct) from public.pk_parse_players(v_players)) > v_played then 'za dużo dobrych odpowiedzi'
    -- teleturniej: jedna odpowiedź na pytanie; live: każdy gracz najwyżej raz na pytanie
    when v_mode = 'teleturniej' and (select sum(correct + wrong) from public.pk_parse_players(v_players)) > v_played then 'za dużo odpowiedzi'
    when exists (select 1 from public.pk_parse_players(v_players) where correct + wrong > v_played) then 'za dużo odpowiedzi gracza'
    when (select sum(correct + wrong) from public.pk_parse_players(v_players)) = 0 then 'gra bez odpowiedzi'
  end into v_bad;
  if v_bad is not null then
    raise exception 'pk: %', v_bad using errcode = '22023';
  end if;

  insert into public.pk_games (id, mode, level, code, questions_total, questions_played, penalty, players_count)
  values (v_id, v_mode, v_level, v_code, v_total, v_played, v_pen, v_n);

  insert into public.pk_game_players (game_id, name, name_key, score, correct, wrong, place)
  select v_id, name, name_key, score, correct, wrong, rank() over (order by score desc)
  from public.pk_parse_players(v_players);

  return jsonb_build_object('ok', true, 'id', v_id);
exception
  when unique_violation then
    return jsonb_build_object('ok', true, 'id', v_id, 'duplicate', true);
  when check_violation then
    raise exception 'pk: dane gry poza zakresem' using errcode = '22023';
end;
$$;

create or replace function public.pk_leaderboard(
  p_level text default null,
  p_mode  text default null,
  p_days  int  default null,
  p_limit int  default 100
)
returns table (
  name        text,
  games       bigint,
  wins        bigint,
  points      bigint,
  best        int,
  avg_points  numeric,
  correct     bigint,
  wrong       bigint,
  last_played timestamptz
)
language sql
stable
security definer
set search_path = ''
as $$
  select
    (array_agg(gp.name order by g.created_at desc))[1],
    count(*),
    count(*) filter (where gp.place = 1 and gp.score > 0 and g.players_count >= 2),
    sum(gp.score),
    max(gp.score),
    round(avg(gp.score), 1),
    sum(gp.correct),
    sum(gp.wrong),
    max(g.created_at)
  from public.pk_game_players gp
  join public.pk_games g on g.id = gp.game_id
  where (p_level is null or g.level = p_level)
    and (p_mode is null or g.mode = p_mode)
    and (p_days is null or g.created_at > now() - make_interval(days => p_days))
  group by gp.name_key
  order by sum(gp.score) desc, 3 desc, count(*) asc
  limit least(greatest(coalesce(p_limit, 100), 1), 500)
$$;

create or replace function public.pk_recent_games(
  p_limit int  default 20,
  p_name  text default null
)
returns table (
  id               uuid,
  mode             text,
  level            text,
  created_at       timestamptz,
  questions_played int,
  penalty          int,
  players          jsonb
)
language sql
stable
security definer
set search_path = ''
as $$
  select g.id, g.mode, g.level, g.created_at, g.questions_played, g.penalty,
    (select jsonb_agg(jsonb_build_object('name', p.name, 'score', p.score, 'correct', p.correct, 'wrong', p.wrong, 'place', p.place)
                      order by p.place, p.name)
       from public.pk_game_players p where p.game_id = g.id)
  from public.pk_games g
  where p_name is null
     or exists (select 1 from public.pk_game_players p
                where p.game_id = g.id and p.name_key = lower(public.pk_clean_name(p_name)))
  order by g.created_at desc
  limit least(greatest(coalesce(p_limit, 20), 1), 100)
$$;

revoke all on function public.pk_parse_players(jsonb) from public, anon, authenticated;
revoke all on function public.pk_submit_game(jsonb) from public;
revoke all on function public.pk_leaderboard(text, text, int, int) from public;
revoke all on function public.pk_recent_games(int, text) from public;
grant execute on function public.pk_submit_game(jsonb) to anon, authenticated;
grant execute on function public.pk_leaderboard(text, text, int, int) to anon, authenticated;
grant execute on function public.pk_recent_games(int, text) to anon, authenticated;
