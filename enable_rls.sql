-- ============================================================
-- EATI: enable Row Level Security on all public tables
-- ============================================================
--
-- WHY
--   Every table in the `public` schema is exposed through Supabase's
--   auto-generated PostgREST API, which accepts the *anon* key. The anon
--   key is public by design. With RLS off, anyone holding it can read and
--   write every row. EATI's Google login protects the Streamlit UI only --
--   it does nothing for the REST endpoint.
--
-- WHY THIS IS SAFE FOR THE APP
--   The Streamlit app connects as the `postgres` role, which has BYPASSRLS
--   and owns these tables, so RLS never applies to it. server.py and
--   insert_employment_news.py use the service_role key, which also
--   bypasses RLS. Nothing in the codebase uses the anon key.
--
--   Enabling RLS with ZERO policies is a deny-all for anon/authenticated:
--   the REST API returns empty result sets and rejects all writes.
--
-- DO NOT add `FORCE ROW LEVEL SECURITY`. That would apply RLS to the table
--   owner (`postgres`) as well. With no policies defined, the app would
--   read zero rows and every write would fail.
--
-- Run in: Supabase Dashboard -> SQL Editor
-- ============================================================


-- ------------------------------------------------------------
-- 1. Enable RLS on every existing table in `public`
--    Written as a loop so tables added later are picked up by
--    simply re-running this script.
-- ------------------------------------------------------------

DO $$
DECLARE
    target RECORD;
BEGIN
    FOR target IN
        SELECT c.relname
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relkind = 'r'
          AND NOT c.relrowsecurity
    LOOP
        EXECUTE format(
            'ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY',
            target.relname
        );

        RAISE NOTICE 'RLS enabled on public.%', target.relname;
    END LOOP;
END $$;


-- ------------------------------------------------------------
-- 2. Defence in depth: remove the PostgREST grants outright.
--
--    RLS alone already blocks row access. Revoking the grants means the
--    anon key cannot even see that these tables exist, and any future
--    table is denied by default rather than silently exposed.
--
--    Skip this section if you later plan to call Supabase from a browser
--    client with the anon key -- you would need grants plus policies.
-- ------------------------------------------------------------

REVOKE ALL ON ALL TABLES    IN SCHEMA public FROM anon, authenticated;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM anon, authenticated;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    REVOKE ALL ON TABLES FROM anon, authenticated;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    REVOKE ALL ON SEQUENCES FROM anon, authenticated;


-- ------------------------------------------------------------
-- 3. Verify
-- ------------------------------------------------------------

SELECT
    c.relname                                   AS table_name,
    c.relrowsecurity                            AS rls_enabled,
    c.relforcerowsecurity                       AS rls_forced,
    (SELECT count(*) FROM pg_policy p
      WHERE p.polrelid = c.oid)                 AS policy_count,
    has_table_privilege('anon', c.oid, 'SELECT') AS anon_can_select
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relkind = 'r'
ORDER BY c.relname;

-- Expected after running: rls_enabled = true, rls_forced = false,
-- policy_count = 0, anon_can_select = false, for every row.
