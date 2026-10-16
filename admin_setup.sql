CREATE TABLE IF NOT EXISTS public.admin_users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO public.admin_users (email, is_active)
VALUES ('sarika.pramod@gmail.com', TRUE)
ON CONFLICT (email) DO UPDATE SET is_active = EXCLUDED.is_active;
