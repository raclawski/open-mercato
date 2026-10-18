// Konfiguracja serwera gry (Supabase). Uzupełnij albo ustaw zmienne środowiskowe na Vercel
// (SUPABASE_URL i SUPABASE_ANON_KEY), wtedy build sam nadpisze ten plik.
// Klucz anon jest publiczny z założenia: przeglądarka i tak go widzi, a dostęp do danych
// ograniczają RLS i funkcje w bazie (supabase/migrations). Nigdy nie wpisuj tu klucza service_role.
window.PK_CONFIG = {
  supabaseUrl: "",
  supabaseAnonKey: ""
};
