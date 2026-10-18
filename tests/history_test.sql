-- Testy historii pytań (pk_mark_seen, pk_history). Uruchamia je npm run test:sql po migracjach. Na końcu rollback.
begin;
set local role anon;

do $$ begin
  begin perform 1 from public.pk_seen_q; raise exception 'FAIL: anon czyta pk_seen_q';
  exception when insufficient_privilege then null; end;
end $$;

do $$
declare r jsonb; h jsonb;
begin
  r := public.pk_mark_seen('["Ola", " ola ", "Kuba", 5, ""]', '["std:abc1", "std:abc2", "ZŁE ID", 7, "pop:x9"]');
  if (r->>'rows')::int <> 6 then raise exception 'FAIL: zapis historii %', r; end if;
  r := public.pk_mark_seen('["OLA"]', '["std:abc1"]');
  h := public.pk_history('["ola", "Kuba"]');
  if (h->>'std:abc1')::numeric < 1.99 or (h->>'std:abc2')::numeric < 1.99 or h ? 'ZŁE ID' then raise exception 'FAIL: historia dwóch graczy %', h; end if;
  h := public.pk_history('["Kuba"]');
  if (h->>'std:abc1')::numeric not between 0.99 and 1.0 or jsonb_typeof(h) <> 'object' then raise exception 'FAIL: historia jednego gracza %', h; end if;
  if public.pk_history('["Nikt"]') <> '{}'::jsonb or public.pk_history('"zły"') <> '{}'::jsonb then raise exception 'FAIL: pusta historia'; end if;
  r := public.pk_mark_seen('{"a":1}', '[]');
  if (r->>'rows')::int <> 0 then raise exception 'FAIL: złe dane %', r; end if;
end $$;

-- historia wygasa: pytanie sprzed 20 dni waży ok. 0,37
reset role;
update public.pk_seen_q set last_at = now() - interval '20 days' where name_key = 'kuba' and qid = 'pop:x9';
set local role anon;
do $$
declare h jsonb := public.pk_history('["Kuba"]');
begin
  if (h->>'pop:x9')::numeric not between 0.36 and 0.38 then raise exception 'FAIL: wygasanie %', h; end if;
end $$;

rollback;
\echo 'history_test.sql: OK'
