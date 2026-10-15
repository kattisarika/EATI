# JMT Employment Market Dashboard

## 1. Enable read-only access in Supabase

In **Supabase → SQL Editor**, run this policy for a dashboard that uses a publishable key:

```sql
ALTER TABLE public.workforce_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Dashboard read workforce events"
ON public.workforce_events
FOR SELECT
TO anon
USING (true);
```

**Important:** This makes *all rows* in `workforce_events` publicly readable to anyone using your publishable key. Use this only if the table contains public news data that you intend to expose. If you need private access, use Supabase Auth and a more restrictive policy instead. Do not create an INSERT/UPDATE policy for the dashboard.

If the policy already exists, skip creating it.

## 2. Install packages

```bash
cd ~/Documents/EATI
python3 -m pip install -r requirements.txt
```

## 3. Set your `.env`

```dotenv
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_YOUR_KEY
```

Keep any existing `SUPABASE_SERVICE_ROLE_KEY` only for trusted backend scripts. **Never** deploy it in dashboard secrets or client code. Keep `.env` out of Git.

## 4. Run the dashboard

```bash
python3 -m streamlit run app.py
```

## 5. Notes

- This app reads the existing `public.workforce_events` table; it does not insert or modify rows.
- The `state_or_region` column includes combined strings such as `Texas (Dallas)` and `National / Remote (US)`. The state filter therefore filters the exact stored region labels, not standardized 50-state names.
- Source-reported job counts may be unverified and should not be interpreted as official labor statistics.
- The app loads records in pages of 1,000 and caches results for 10 minutes; click Refresh data to reload.
