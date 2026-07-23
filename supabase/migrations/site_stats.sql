-- 网站访客 / 浏览量计数器
-- 在 Supabase SQL Editor 中运行此文件

-- 统计表: key-value 存储
CREATE TABLE IF NOT EXISTS site_stats (
  key   text PRIMARY KEY,
  value int NOT NULL DEFAULT 0
);

-- 初始化
INSERT INTO site_stats (key, value) VALUES ('site_pv', 0) ON CONFLICT DO NOTHING;
INSERT INTO site_stats (key, value) VALUES ('site_uv', 0) ON CONFLICT DO NOTHING;

-- RLS: 允许匿名读写 site_stats
ALTER TABLE site_stats ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS anon_select ON site_stats;
DROP POLICY IF EXISTS anon_update ON site_stats;
CREATE POLICY anon_select ON site_stats FOR SELECT USING (true);
CREATE POLICY anon_update ON site_stats FOR UPDATE USING (true);

-- 函数: PV +1 并返回新值
CREATE OR REPLACE FUNCTION increment_site_pv()
RETURNS int
LANGUAGE plpgsql
AS $$
DECLARE
  new_val int;
BEGIN
  UPDATE site_stats SET value = value + 1 WHERE key = 'site_pv'
  RETURNING value INTO new_val;
  RETURN new_val;
END;
$$;

-- 函数: UV +1 并返回新值
CREATE OR REPLACE FUNCTION increment_site_uv()
RETURNS int
LANGUAGE plpgsql
AS $$
DECLARE
  new_val int;
BEGIN
  UPDATE site_stats SET value = value + 1 WHERE key = 'site_uv'
  RETURNING value INTO new_val;
  RETURN new_val;
END;
$$;

-- 函数: 只读 UV
CREATE OR REPLACE FUNCTION get_site_uv()
RETURNS int
LANGUAGE sql
AS $$
  SELECT value FROM site_stats WHERE key = 'site_uv';
$$;
