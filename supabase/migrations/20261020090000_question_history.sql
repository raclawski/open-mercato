-- TELETURNIEJ: historia pytań dla nicków (dobór pytań, który rzadziej powtarza to, co gracze już widzieli).
--
-- pk_seen_q: który nick widział które pytanie, ile razy i kiedy ostatnio. Id pytania (qid) to `kategoria:skrót treści`
-- z src/templates/shared/mix.js. Pisze tylko pk_mark_seen (po zapisie gry), czyta tylko pk_history.
-- Plik można uruchomić ponownie. Wgraj go po 20261019090000_ranking_accept_all.sql (SQL Editor → Run).

create table if not exists public.pk_seen_q (
  name_key text not null,
  qid      text not null,
  n        int  not null default 1,
  last_at  timestamptz not null default now(),
  primary key (name_key, qid)
);
alter table public.pk_seen_q enable row level security;
revoke all on public.pk_seen_q from anon, authenticated;

-- Gra się skończyła: gracze (do 16 nicków) widzieli te pytania (do 100). Złe dane są pomijane, nie odrzucane.
create or replace function public.pk_mark_seen(p_names jsonb, p_qids jsonb)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare v_rows int;
begin
  if jsonb_typeof(p_names) <> 'array' or jsonb_typeof(p_qids) <> 'array' then
    return jsonb_build_object('ok', true, 'rows', 0);
  end if;
  insert into public.pk_seen_q as s (name_key, qid)
  select distinct nm.k, q.v
  from (select lower(public.pk_clean_name(e #>> '{}')) as k
        from jsonb_array_elements(p_names) with ordinality as t(e, i)
        where jsonb_typeof(e) = 'string' and i <= 16) nm
  cross join (select e #>> '{}' as v
              from jsonb_array_elements(p_qids) with ordinality as t(e, i)
              where jsonb_typeof(e) = 'string' and i <= 100 and (e #>> '{}') ~ '^[a-z]{2,12}:[0-9a-z]{1,8}$') q
  where nm.k <> ''
  on conflict (name_key, qid) do update set n = least(s.n + 1, 100000), last_at = now();
  get diagnostics v_rows = row_count;
  return jsonb_build_object('ok', true, 'rows', v_rows);
end;
$$;

-- Jak bardzo pytania są „ograne” dla tych nicków: {qid: suma po graczach exp(−dni od ostatniego razu / p_tau)}.
-- Pytanie widziane wczoraj przez jednego gracza ≈ 1, przez trzech ≈ 3, sprzed p_tau dni ≈ 0,37. Jeden wiersz jsonb
-- zamiast tabeli, bo Supabase przycina wyniki RPC do 1000 wierszy.
create or replace function public.pk_history(p_names jsonb, p_tau numeric default 20)
returns jsonb
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce(jsonb_object_agg(qid, round(p, 3)), '{}'::jsonb)
  from (
    select s.qid, sum(exp(-greatest(0, extract(epoch from now() - s.last_at)) / 86400.0 / greatest(coalesce(p_tau, 20), 1))) as p
    from public.pk_seen_q s
    where s.name_key in (
      select lower(public.pk_clean_name(e #>> '{}'))
      from jsonb_array_elements(case when jsonb_typeof(p_names) = 'array' then p_names else '[]'::jsonb end) with ordinality as t(e, i)
      where jsonb_typeof(e) = 'string' and i <= 16)
      and s.last_at > now() - interval '365 days'
    group by s.qid
  ) x
$$;

revoke all on function public.pk_mark_seen(jsonb, jsonb) from public;
revoke all on function public.pk_history(jsonb, numeric) from public;
grant execute on function public.pk_mark_seen(jsonb, jsonb) to anon, authenticated;
grant execute on function public.pk_history(jsonb, numeric) to anon, authenticated;
