create table if not exists lojas_coletadas (
  id bigserial primary key,
  regiao text,
  nome text,
  telefone text,
  whatsapp text,
  endereco text,
  categoria text,
  horario text,
  site text,
  nota text,
  url text,
  created_at timestamptz not null default now(),
  url_key text generated always as (
    nullif(btrim(lower(regexp_replace(coalesce(url, ''), '[^a-zA-Z0-9]+', ' ', 'g'))), '')
  ) stored,
  telefone_key text generated always as (
    nullif(regexp_replace(coalesce(telefone, ''), '[^0-9]+', '', 'g'), '')
  ) stored,
  whatsapp_key text generated always as (
    nullif(regexp_replace(coalesce(whatsapp, ''), '[^0-9]+', '', 'g'), '')
  ) stored,
  site_key text generated always as (
    nullif(btrim(lower(regexp_replace(coalesce(site, ''), '[^a-zA-Z0-9]+', ' ', 'g'))), '')
  ) stored,
  nome_endereco_key text generated always as (
    nullif(
      btrim(lower(
        regexp_replace(coalesce(nome, '') || '|' || coalesce(endereco, ''), '[^a-zA-Z0-9]+', ' ', 'g')
      )),
      ''
    )
  ) stored
);

create unique index if not exists lojas_coletadas_url_key_idx
  on lojas_coletadas (url_key)
  where url_key is not null;

create unique index if not exists lojas_coletadas_telefone_key_idx
  on lojas_coletadas (telefone_key)
  where telefone_key is not null;

create unique index if not exists lojas_coletadas_whatsapp_key_idx
  on lojas_coletadas (whatsapp_key)
  where whatsapp_key is not null;

create unique index if not exists lojas_coletadas_site_key_idx
  on lojas_coletadas (site_key)
  where site_key is not null;

create unique index if not exists lojas_coletadas_nome_endereco_key_idx
  on lojas_coletadas (nome_endereco_key)
  where nome_endereco_key is not null;
