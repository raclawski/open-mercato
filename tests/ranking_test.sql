-- Testy funkcji rankingu na czystej bazie Postgres (z rolami anon i authenticated jak w Supabase).
--   psql "$PGURL" -v ON_ERROR_STOP=1 -f supabase/migrations/20261018120000_ranking.sql -f tests/ranking_test.sql
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

-- odrzucane zgłoszenia
do $$
declare bad text[] := array[
  -- wynik niezgodny z odpowiedziami
  '{"id":"33333333-0000-4000-8000-000000000001","mode":"live","level":"pro","questions_total":20,"questions_played":20,"penalty":1,"players":[{"name":"Oszust","score":999,"correct":1,"wrong":0}]}',
  -- więcej dobrych odpowiedzi niż pytań
  '{"id":"33333333-0000-4000-8000-000000000002","mode":"live","level":"pro","questions_total":20,"questions_played":5,"penalty":1,"players":[{"name":"A","score":40,"correct":4,"wrong":0},{"name":"B","score":20,"correct":2,"wrong":0}]}',
  -- teleturniej: więcej odpowiedzi niż pytań
  '{"id":"33333333-0000-4000-8000-000000000003","mode":"teleturniej","level":"pro","questions_total":20,"questions_played":3,"penalty":1,"players":[{"name":"A","score":19,"correct":2,"wrong":1},{"name":"B","score":-1,"correct":0,"wrong":1}]}',
  -- powtórzone imię (po normalizacji)
  '{"id":"33333333-0000-4000-8000-000000000004","mode":"live","level":"pro","questions_total":20,"questions_played":20,"penalty":1,"players":[{"name":"Ola","score":10,"correct":1,"wrong":0},{"name":" ola","score":0,"correct":0,"wrong":0}]}',
  -- zła kara, zły tryb, zły poziom, za dużo pytań
  '{"id":"33333333-0000-4000-8000-000000000005","mode":"live","level":"pro","questions_total":20,"questions_played":20,"penalty":3,"players":[{"name":"A","score":10,"correct":1,"wrong":0}]}',
  '{"id":"33333333-0000-4000-8000-000000000006","mode":"hack","level":"pro","questions_total":20,"questions_played":20,"penalty":1,"players":[{"name":"A","score":10,"correct":1,"wrong":0}]}',
  '{"id":"33333333-0000-4000-8000-000000000007","mode":"live","level":"PRO; drop","questions_total":20,"questions_played":20,"penalty":1,"players":[{"name":"A","score":10,"correct":1,"wrong":0}]}',
  '{"id":"33333333-0000-4000-8000-000000000008","mode":"live","level":"pro","questions_total":20,"questions_played":21,"penalty":1,"players":[{"name":"A","score":10,"correct":1,"wrong":0}]}',
  -- puste imię, imię z samych znaków niewidocznych, brak graczy, typy
  '{"id":"33333333-0000-4000-8000-000000000009","mode":"live","level":"pro","questions_total":20,"questions_played":20,"penalty":1,"players":[{"name":"   ","score":10,"correct":1,"wrong":0}]}',
  '{"id":"33333333-0000-4000-8000-00000000000a","mode":"live","level":"pro","questions_total":20,"questions_played":20,"penalty":1,"players":[{"name":"​​","score":10,"correct":1,"wrong":0}]}',
  '{"id":"33333333-0000-4000-8000-00000000000b","mode":"live","level":"pro","questions_total":20,"questions_played":20,"penalty":1,"players":[]}',
  '{"id":"33333333-0000-4000-8000-00000000000c","mode":"live","level":"pro","questions_total":20,"questions_played":20,"penalty":1,"players":[{"name":"A","score":"dużo","correct":1,"wrong":0}]}',
  '{"id":"nie-uuid","mode":"live","level":"pro","questions_total":20,"questions_played":20,"penalty":1,"players":[{"name":"A","score":10,"correct":1,"wrong":0}]}',
  -- gra bez żadnej odpowiedzi
  '{"id":"33333333-0000-4000-8000-00000000000d","mode":"live","level":"pro","questions_total":20,"questions_played":20,"penalty":1,"players":[{"name":"A","score":0,"correct":0,"wrong":0}]}'
];
b text;
begin
  foreach b in array bad loop
    begin
      perform public.pk_submit_game(b::jsonb);
      raise exception 'FAIL: przyjęto %', b;
    exception when invalid_parameter_value then null;
    end;
  end loop;
end $$;

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

rollback;
\echo 'ranking_test.sql: OK'
