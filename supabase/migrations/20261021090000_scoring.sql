-- TELETURNIEJ: wynik gracza liczony przez grę (pytania za podwójne punkty, tryb „Kto pierwszy, ten lepszy”).
--
-- Do tej pory baza sama liczyła wynik jako 10 × dobre − kara × złe. Teraz bierze wynik wysłany przez grę,
-- ale przycina go do możliwego zakresu: od −2 × kara × złe do 20 × dobre. Gra bez wyniku liczy się jak dawniej.
-- Wgraj ten plik po 20261020090000_question_history.sql (SQL Editor → Run). Można go uruchomić ponownie.

create or replace function public.pk_norm_players_s(p jsonb)
returns table (name text, name_key text, correct int, wrong int, score int, ord bigint)
language sql immutable
set search_path = ''
as $$
  select n.name, lower(n.name), greatest(0, public.pk_int(e->'correct')), greatest(0, public.pk_int(e->'wrong')),
         case when jsonb_typeof(e->'score') in ('number', 'string') then public.pk_int(e->'score', null) end, k
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

  select count(distinct name_key) into v_n from public.pk_norm_players_s(p_game->'players');
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
           -- wynik od klienta (pytania ×2, tryb „kto pierwszy”), przycięty do tego, co da się zdobyć:
           -- najwyżej 20 za dobrą odpowiedź, najmniej −2 × kara za złą; bez wyniku liczymy 10 × dobre − kara × złe
           greatest(-2 * v_pen * least(sum(wrong), 100000), least(20 * least(sum(correct), 100000),
             coalesce(sum(score), 10 * least(sum(correct), 100000) - v_pen * least(sum(wrong), 100000))))::int as score,
           min(ord) as first_ord
    from public.pk_norm_players_s(p_game->'players') group by name_key
    order by min(ord) limit 16
  ) g;

  return jsonb_build_object('ok', true, 'id', v_id);
exception
  when unique_violation then
    return jsonb_build_object('ok', true, 'id', v_id, 'duplicate', true);
end;
$$;

revoke all on function public.pk_norm_players_s(jsonb) from public, anon, authenticated;
revoke all on function public.pk_submit_game(jsonb) from public;
grant execute on function public.pk_submit_game(jsonb) to anon, authenticated;
