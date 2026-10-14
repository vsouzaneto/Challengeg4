// Local WASM Postgres only. No remote connection string or network Auth service.
const {PGlite}=await import(process.env.PGLITE_MODULE??'@electric-sql/pglite');import fs from 'node:fs/promises';
const root=new URL('../',import.meta.url).pathname;
const db=new PGlite();
try{
await db.exec(`create role anon;create role authenticated;create role service_role bypassrls;create schema auth;create table auth.users(id uuid primary key,email text,email_confirmed_at timestamptz,banned_until timestamptz,deleted_at timestamptz,is_anonymous boolean default false,raw_app_meta_data jsonb default '{}');create table auth.sessions(id uuid primary key,user_id uuid references auth.users(id),not_after timestamptz);create function auth.uid() returns uuid language sql stable as $$select null::uuid$$;`);
for(const f of ['foundation.sql','normalized_records.sql','ingestion_functions.sql','immutability_hardening.sql','import_api.sql','promotion_idempotency.sql','lineage_indexes.sql','analysis_runtime_guards.sql','web_application.sql','web_account_detail.sql','analysis_materialized.sql','web_parse_reuse_guard.sql','web_conflict_response.sql','decision_scopes.sql','authentication.sql','authenticated_upload_ownership.sql','authentication_api_boundary.sql','assistant.sql','assistant_context_catalog.sql']){try{await db.exec(await fs.readFile(root+'/db/'+f,'utf8'));}catch(e){throw Error(f+': '+e.message);}}
await db.exec(await fs.readFile(root+'/tests/local_users_fixture.sql','utf8'));
await db.exec(await fs.readFile(root+'/supabase/migrations/20261013140604_user_management.sql','utf8'));
await db.exec(await fs.readFile(root+'/tests/local_user_management.sql','utf8'));
console.log('Isolated SQL user-management acceptance passed. No network/Auth service used.');
}catch(e){console.error(e.message,e.detail??'',e.where??'');process.exitCode=1;}finally{await db.close();}
