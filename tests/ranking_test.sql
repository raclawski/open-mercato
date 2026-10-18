-- Testy funkcji rankingu na czystej bazie Postgres (z rolami anon i authenticated jak w Supabase), po wszystkich migracjach.
--   psql "$PGURL" -v ON_ERROR_STOP=1 -f supabase/migrations/20261018120000_ranking.sql -f supabase/migrations/20261019090000_ranking_accept_all.sql -f tests/ranking_test.sql
-- Każdy błąd przerywa skrypt. Na końcu wszystko jest wycofywane (rollback).

begin;
set local role anon;

-- anon nie widzi tabel bezpośrednio
do $$ begin
  begin perform 1 from public.pk_games; raise exception 'FAIL: anon czyta pk_games';
  exception when insufficient_privilege then null; end;
  begin insert into public.pk_game_players values (gen_random_uuid(), 'x', 'x', 0, 0, 0, 1); raise exception 'FAIL: anon pisze do pk_game_players';
  exception when insufficient_privilege then null; end;
end $$;

-- poprawna gra live: 3 graczy, 20 pytań, kara −1
do $$
declare r jsonb;
begin
  r := public.pk_submit_game('{"id":"11111111-1111-4111-8111-111111111111","mode":"live","level":"pro","code":"KRZY",
    "questions_total":20,"questions_played":20,"penalty":1,
    "players":[{"name":"Adam","score":58,"correct":6,"wrong":2},{"name":" Zając ","score":30,"correct":3,"wrong":0},{"name":"Asia","score":-3,"correct":0,"wrong":3}]}');
  if not (r->>'ok')::bool or r ? 'duplicate' then raise exception 'FAIL: zapis gry %', r; end if;
  -- ponowny zapis tej samej gry jest bezpieczny
  r := public.pk_submit_game('{"id":"11111111-1111-4111-8111-111111111111","mode":"live","level":"pro","questions_total":20,"questions_played":20,"penalty":1,"players":[]}');
  if not (r->>'duplicate')::bool then raise exception 'FAIL: duplikat %', r; end if;
end $$;

-- teleturniej, remis na 1. miejscu, inny zapis nicku (wielkość liter)
select public.pk_submit_game('{"id":"22222222-2222-4222-8222-222222222222","mode":"teleturniej","level":"pop",
  "questions_total":20,"questions_played":12,"penalty":5,
  "players":[{"name":"adam","score":15,"correct":2,"wrong":1},{"name":"Julia","score":15,"correct":2,"wrong":1},{"name":"Tomek","score":-10,"correct":0,"wrong":2}]}');

-- każda gra trafia na listę: dane są porządkowane, a nie odrzucane
do $$
declare r jsonb; g record; n int;
begin
  -- wynik niezgodny z odpowiedziami: liczony od nowa (10 × 1 − 5 × 2 = 0)
  r := public.pk_submit_game('{"id":"33333333-0000-4000-8000-000000000001","mode":"live","level":"pro","questions_total":20,"questions_played":20,"penalty":5,"players":[{"name":"Oszust","score":999,"correct":1,"wrong":2}]}');
  if (r->>'ok')::bool is not true then raise exception 'FAIL: wynik niezgodny nie przyjęty %', r; end if;
  -- powtórzone imię (po normalizacji) łączy się w jednego gracza, zła kara → 1, zły tryb i poziom → live/mix, typy → 0
  r := public.pk_submit_game('{"id":"33333333-0000-4000-8000-000000000002","mode":"hack","level":"PRO; drop","questions_total":500,"questions_played":900,"penalty":3,
    "players":[{"name":"Ola","score":10,"correct":1,"wrong":0},{"name":" ola","score":0,"correct":"2","wrong":1},{"name":"Bez","score":"dużo","correct":"dużo","wrong":-4},{"name":"   ","correct":5},{"name":"​"}]}');
  if (r->>'ok')::bool is not true or r ? 'skipped' then raise exception 'FAIL: gra z bałaganem nie przyjęta %', r; end if;
  -- nieprawidłowe id: nowe id, gra przyjęta
  r := public.pk_submit_game('{"id":"nie-uuid","mode":"live","level":"pro","questions_total":20,"questions_played":20,"penalty":1,"players":[{"name":"Ktoś","correct":0,"wrong":0}]}');
  if (r->>'ok')::bool is not true or (r->>'id') is null then raise exception 'FAIL: gra bez id %', r; end if;
  -- gra bez graczy z imieniem jest pomijana, ale bez błędu
  r := public.pk_submit_game('{"id":"33333333-0000-4000-8000-000000000003","players":[]}');
  if (r->>'skipped')::bool is not true then raise exception 'FAIL: pusta gra %', r; end if;
  -- tylko coś, co nie jest obiektem JSON, to błąd
  begin perform public.pk_submit_game('[1,2]'); raise exception 'FAIL: przyjęto tablicę';
  exception when invalid_parameter_value then null; end;
end $$;

reset role;
do $$
declare g record; n int;
begin
  select score, correct, wrong into g from public.pk_game_players where game_id = '33333333-0000-4000-8000-000000000001';
  -- wynik od gry przycięty do możliwego zakresu (migracja 20261021090000_scoring): 999 → najwyżej 20 × 1 dobra
  if g.score <> 20 or g.correct <> 1 or g.wrong <> 2 then raise exception 'FAIL: przycięty wynik %', row_to_json(g); end if;
  select mode, level, penalty, questions_total, questions_played, players_count into g from public.pk_games where id = '33333333-0000-4000-8000-000000000002';
  if g.mode <> 'live' or g.level <> 'mix' or g.penalty <> 1 or g.questions_total <> 100 or g.questions_played <> 100 or g.players_count <> 2 then raise exception 'FAIL: porządkowanie gry %', row_to_json(g); end if;
  select score, correct, wrong into g from public.pk_game_players where game_id = '33333333-0000-4000-8000-000000000002' and name_key = 'ola';
  if g.correct <> 3 or g.wrong <> 1 or g.score <> 10 then raise exception 'FAIL: łączenie imion %', row_to_json(g); end if;
  select score, correct, wrong into g from public.pk_game_players where game_id = '33333333-0000-4000-8000-000000000002' and name_key = 'bez';
  if g.correct <> 0 or g.wrong <> 0 or g.score <> 0 then raise exception 'FAIL: złe typy %', row_to_json(g); end if;
  select count(*) into n from public.pk_games where id = '33333333-0000-4000-8000-000000000003';
  if n <> 0 then raise exception 'FAIL: zapisano pustą grę'; end if;
  -- sprzątanie, żeby dalsze sprawdzenia rankingu liczyły tylko dwie główne gry
  delete from public.pk_games where id::text like '33333333-%' or id in (select game_id from public.pk_game_players where name = 'Ktoś');
end $$;
set local role anon;

-- ranking: Adam (2 gry, nick bez względu na wielkość liter; w jednej transakcji obie gry mają ten sam czas, więc pisownia jest dowolna), wygrane tylko w grach z ≥2 graczami i wynikiem > 0
do $$
declare r record; n int;
begin
  select count(*) into n from public.pk_leaderboard();
  if n <> 5 then raise exception 'FAIL: liczba graczy w rankingu %', n; end if;
  select * into r from public.pk_leaderboard() limit 1;
  if lower(r.name) <> 'adam' or r.games <> 2 or r.points <> 73 or r.wins <> 2 or r.best <> 58 or r.correct <> 8 or r.wrong <> 3 then
    raise exception 'FAIL: lider rankingu %', row_to_json(r);
  end if;
  select * into r from public.pk_leaderboard() where name = 'Zając';
  if r.games <> 1 or r.wins <> 0 then raise exception 'FAIL: Zając %', row_to_json(r); end if;
  select count(*) into n from public.pk_leaderboard(p_level => 'pop');
  if n <> 3 then raise exception 'FAIL: filtr poziomu %', n; end if;
  select count(*) into n from public.pk_leaderboard(p_mode => 'live');
  if n <> 3 then raise exception 'FAIL: filtr trybu %', n; end if;
  select count(*) into n from public.pk_leaderboard(p_days => 7);
  if n <> 5 then raise exception 'FAIL: filtr dni %', n; end if;
end $$;

-- nick: znaki niewidoczne i sterujące znikają (wyrażenie w migracji jest zapisane samym ASCII)
do $$
begin
  if public.pk_clean_name('  To' || chr(8203) || 'm' || chr(65279) || 'ek' || chr(8238) || chr(9) || ' ') <> 'Tomek' then
    raise exception 'FAIL: pk_clean_name %', public.pk_clean_name('To' || chr(8203) || 'mek');
  end if;
end $$;

-- ostatnie gry i historia gracza
do $$
declare r record; n int;
begin
  select count(*) into n from public.pk_recent_games();
  if n <> 2 then raise exception 'FAIL: ostatnie gry %', n; end if;
  select count(*) into n from public.pk_recent_games(p_name => 'ADAM ');
  if n <> 2 then raise exception 'FAIL: historia Adama %', n; end if;
  select count(*) into n from public.pk_recent_games(p_name => 'Julia');
  if n <> 1 then raise exception 'FAIL: historia Julii %', n; end if;
  select * into r from public.pk_recent_games() where level = 'pop';
  if r.players->0->>'place' <> '1' or r.players->1->>'place' <> '1' or r.players->2->>'place' <> '3' then
    raise exception 'FAIL: miejsca przy remisie %', r.players;
  end if;
end $$;

-- pytanie ×2 i „kto pierwszy”: wynik od gry, gdy mieści się w zakresie; gra bez wyniku liczy się jak dawniej
select public.pk_submit_game('{"id":"44444444-0000-4000-8000-000000000001","mode":"live","level":"pro","questions_total":10,"questions_played":10,"penalty":5,
    "players":[{"name":"Dubel","score":35,"correct":2,"wrong":1},{"name":"Minus","score":-30,"correct":0,"wrong":2},{"name":"Stary","correct":3,"wrong":1}]}');
reset role;
do $$
declare g record;
begin
  select score into g from public.pk_game_players where game_id = '44444444-0000-4000-8000-000000000001' and name_key = 'dubel';
  if g.score <> 35 then raise exception 'FAIL: wynik ×2 %', g.score; end if;
  select score into g from public.pk_game_players where game_id = '44444444-0000-4000-8000-000000000001' and name_key = 'minus';
  if g.score <> -20 then raise exception 'FAIL: dolna granica %', g.score; end if;
  select score into g from public.pk_game_players where game_id = '44444444-0000-4000-8000-000000000001' and name_key = 'stary';
  if g.score <> 25 then raise exception 'FAIL: wynik bez pola score %', g.score; end if;
end $$;

rollback;
\echo 'ranking_test.sql: OK'
