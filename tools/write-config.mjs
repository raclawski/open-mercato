// Vercel: zapisuje dist/web/config.js ze zmiennych środowiskowych (jeśli są ustawione).
//   SUPABASE_URL + SUPABASE_ANON_KEY (zalecane), a także nazwy z integracji Supabase w Vercel
//   (NEXT_PUBLIC_…, POSTGRES_…) i inne popularne warianty (…_PUBLISHABLE_KEY, VITE_…, PUBLIC_…).
// Bez zmiennych zostaje config.js z repozytorium. Log builda mówi, które nazwy znalazł.
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const env = process.env;
const pick = (names) => { for (const n of names) if (env[n] && env[n].trim()) return [n, env[n].trim()]; return [null, ""]; };
const pre = ["", "NEXT_PUBLIC_", "VITE_", "PUBLIC_"];
const [urlName, url] = pick(pre.map((p) => p + "SUPABASE_URL"));
const [keyName, key] = pick(pre.flatMap((p) => [p + "SUPABASE_ANON_KEY", p + "SUPABASE_PUBLISHABLE_KEY", p + "SUPABASE_KEY"]));
const out = fileURLToPath(new URL("../dist/web/config.js", import.meta.url));
const seen = Object.keys(env).filter((n) => /SUPABASE/i.test(n)).sort();

console.log(`write-config: środowisko Vercel: ${env.VERCEL_ENV || "(brak, build lokalny)"}`);
console.log(`write-config: zmienne z „SUPABASE” w nazwie: ${seen.length ? seen.join(", ") : "żadnych"}`);

if (url && key) {
  let payload = "";
  try { payload = Buffer.from((key.split(".")[1] || ""), "base64").toString(); } catch (e) { }
  if (/service_role/.test(payload) || key.startsWith("sb_secret_")) {
    console.error(`write-config: ${keyName} to klucz service_role/secret. Na stronę idzie tylko klucz anon (publishable).`);
    process.exit(1);
  }
  if (!/^https:\/\/[^/]+$/.test(url.replace(/\/+$/, ""))) console.warn(`write-config: ${urlName} nie wygląda jak adres projektu (https://xxxx.supabase.co): ${url}`);
  writeFileSync(out, `// Wygenerowane przez tools/write-config.mjs ze zmiennych środowiskowych.\nwindow.PK_CONFIG = ${JSON.stringify({ supabaseUrl: url.replace(/\/+$/, ""), supabaseAnonKey: key }, null, 2)};\n`);
  console.log(`write-config: dist/web/config.js z ${urlName} i ${keyName}`);
} else {
  console.warn(`write-config: brak ${url ? "klucza (SUPABASE_ANON_KEY)" : "adresu (SUPABASE_URL)"}${!url && !key ? " i klucza (SUPABASE_ANON_KEY)" : ""}. Zostaje config.js z repozytorium.`);
  console.warn("write-config: ustaw zmienne w Vercel (Settings → Environment Variables, zaznacz Production) i zrób Redeploy.");
}
