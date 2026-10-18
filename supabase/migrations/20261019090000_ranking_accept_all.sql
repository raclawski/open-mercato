-- Postaw Krzyżyk: każda rozegrana gra trafia na listę wyników.
--
-- Pierwsza wersja pk_submit_game odrzucała gry, których dane się nie zgadzały (np. wynik ≠ 10 × dobre − kara × złe).
-- Teraz funkcja niczego nie odrzuca z powodu treści, tylko porządkuje dane:
--   - wynik liczy sama z liczby dobrych i złych odpowiedzi (wynik od klienta jest ignorowany),
--   - złe typy i ujemne liczby zamienia na 0, nieznaną karę na 1, nieznany tryb na „live”,
--     nieprawidłowy poziom na „mix”, liczby pytań przycina do 1–100,
--   - powtórzone imiona (bez względu na wielkość liter) łączy w jednego gracza,
--   - bierze najwyżej 16 graczy, pomija graczy bez imienia.
-- Pomija tylko grę bez żadnego gracza z imieniem ({"ok": true, "skipped": true}).
-- Zapis jest dalej idempotentny po id gry. Wgraj ten plik po 20261018120000_ranking.sql (SQL Editor → Run). Można go uruchomić ponownie.

-- Poprawka pk_clean_name: w pierwszej migracji znaki niewidoczne były wpisane dosłownie. Przy wklejaniu
-- do SQL Editora mogły zniknąć, a wtedy wyrażenie regularne jest błędne i każdy zapis gry kończy się błędem
-- („nieprawidłowe dane graczy”). Tu są zapisane jako \uXXXX, więc kopiowanie ich nie psuje.
create or replace function public.pk_clean_name(p text)
returns text
language sql immutable
set search_path = ''
as $$
  select left(btrim(regexp_replace(coalesce(p, ''), '[[:cntrl:]\u200B-\u200F\u2028-\u202E\u2060-\u206F\uFEFF]', '', 'g')), 20)
$$;

create or replace function public.pk_int(p jsonb, p_default int default 0)
returns int
language sql immutable
set search_path = ''
as $$
  select case
    when jsonb_typeof(p) = 'number' then greatest(-1000000, least(1000000, round((p #>> '{}')::numeric)))::int
    when jsonb_typeof(p) = 'string' and (p #>> '{}') ~ '^\s*-?\d{1,7}\s*$' then btrim(p #>> '{}')::int
    else p_default
  end
$$;

create or replace function public.pk_norm_players(p jsonb)
returns table (name text, name_key text, correct int, wrong int, ord bigint)
language sql immutable
set search_path = ''
as $$
  select n.name, lower(n.name), greatest(0, public.pk_int(e->'correct')), greatest(0, public.pk_int(e->'wrong')), k
  from jsonb_array_elements(case when jsonb_typeof(p) = 'array' then p else '[]'::jsonb end) with ordinality as x (e, k)
  cross join lateral (select public.pk_clean_name(case when jsonb_typeof(e->'name') = 'string' then e->>'name' else '' end) as name) n
  where jsonb_typeof(e) = 'object' and n.name <> ''
$$;

create or replace function public.pk_submit_game(p_game jsonb)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_id     uuid;
  v_mode   text;
  v_level  text;
  v_code   text;
  v_total  int;
  v_played int;
  v_pen    int;
  v_n      int;
begin
  if jsonb_typeof(p_game) is distinct from 'object' then
    raise exception 'pk: gra musi być obiektem JSON' using errcode = '22023';
  end if;

  begin
    v_id := (p_game->>'id')::uuid;
  exception when others then
    v_id := null;
  end;
  v_id := coalesce(v_id, gen_random_uuid());

  if exists (select 1 from public.pk_games where id = v_id) then
    return jsonb_build_object('ok', true, 'id', v_id, 'duplicate', true);
  end if;

  v_mode  := case when p_game->>'mode' in ('live', 'teleturniej') then p_game->>'mode' else 'live' end;
  v_level := case when coalesce(p_game->>'level', '') ~ '^[a-z]{2,12}$' then p_game->>'level' else 'mix' end;
  v_code  := case when coalesce(p_game->>'code', '') ~ '^[A-Z0-9]{4,6}$' then p_game->>'code' else null end;
  v_pen   := public.pk_int(p_game->'penalty', 1);
  if v_pen not in (1, 5, 10) then v_pen := 1; end if;
  v_total  := greatest(1, least(100, public.pk_int(p_game->'questions_total', 1)));
  v_played := greatest(1, least(v_total, public.pk_int(p_game->'questions_played', v_total)));

  select count(distinct name_key) into v_n from public.pk_norm_players(p_game->'players');
  if v_n = 0 then
    return jsonb_build_object('ok', true, 'id', v_id, 'skipped', true);
  end if;

  insert into public.pk_games (id, mode, level, code, questions_total, questions_played, penalty, players_count)
  values (v_id, v_mode, v_level, v_code, v_total, v_played, v_pen, least(v_n, 16));

  insert into public.pk_game_players (game_id, name, name_key, score, correct, wrong, place)
  select v_id, g.name, g.name_key, g.score, g.correct, g.wrong, rank() over (order by g.score desc)
  from (
    select (array_agg(name order by ord))[1] as name, name_key,
           least(sum(correct), 100000)::int as correct, least(sum(wrong), 100000)::int as wrong,
           (10 * least(sum(correct), 100000) - v_pen * least(sum(wrong), 100000))::int as score,
           min(ord) as first_ord
    from public.pk_norm_players(p_game->'players') group by name_key
    order by min(ord) limit 16
  ) g;

  return jsonb_build_object('ok', true, 'id', v_id);
exception
  when unique_violation then
    return jsonb_build_object('ok', true, 'id', v_id, 'duplicate', true);
end;
$$;

revoke all on function public.pk_int(jsonb, int) from public, anon, authenticated;
revoke all on function public.pk_norm_players(jsonb) from public, anon, authenticated;
revoke all on function public.pk_submit_game(jsonb) from public;
grant execute on function public.pk_submit_game(jsonb) to anon, authenticated;
