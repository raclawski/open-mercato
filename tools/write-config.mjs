// Vercel: zapisuje dist/web/config.js ze zmiennych środowiskowych (jeśli są ustawione).
//   SUPABASE_URL + SUPABASE_ANON_KEY (albo NEXT_PUBLIC_… z integracji Supabase w Vercel)
// Bez zmiennych zostaje config.js z repozytorium.
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const env = process.env;
const url = env.SUPABASE_URL || env.NEXT_PUBLIC_SUPABASE_URL || "";
const key = env.SUPABASE_ANON_KEY || env.NEXT_PUBLIC_SUPABASE_ANON_KEY || env.SUPABASE_PUBLISHABLE_KEY || env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || "";
const out = fileURLToPath(new URL("../dist/web/config.js", import.meta.url));

if (url && key) {
  if (/service_role/.test(Buffer.from((key.split(".")[1] || ""), "base64").toString()) || key.startsWith("sb_secret_")) {
    console.error("write-config: to jest klucz service_role/secret. Na stronę idzie tylko klucz anon (publishable).");
    process.exit(1);
  }
  writeFileSync(out, `// Wygenerowane przez tools/write-config.mjs ze zmiennych środowiskowych.\nwindow.PK_CONFIG = ${JSON.stringify({ supabaseUrl: url, supabaseAnonKey: key }, null, 2)};\n`);
  console.log("write-config: dist/web/config.js ze zmiennych środowiskowych");
} else {
  console.log("write-config: brak SUPABASE_URL / SUPABASE_ANON_KEY, zostaje config.js z repozytorium");
}
