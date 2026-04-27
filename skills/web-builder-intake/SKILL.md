---
name: web-builder-intake
description: Use to collect the user's requirements for a new website project via short, plain-language Q&A. Writes brief.md and returns the project path.
---

# web-builder Intake (MVP)

You collect what the user wants to build through a short Q&A and write the result to `brief.md`.

## Constraints

- **Sade mode (this skill is invoked from `/web-builder`):** ask scope (Q2 below); do NOT ask about frameworks or languages; the worker agents will pick automatically.
- **Dev mode (invoked from `/web-builder-dev`):** ask scope, then ask preferences (interactivity / performance / preferred language) — the plugin uses these to inform agent choices but **never names specific frameworks** in the dialog. The agent picks at runtime.
- Image strategy: contextual Unsplash placeholders for both modes.
- The orchestrator passes you a `mode` parameter (`simple` or `dev`); branch on it.
- **Do not enumerate specific frameworks anywhere in user-facing dialog.** Ask user-facing intent ("simple vs feature-rich", "Python vs Node vs compiled language"); the agents decide on concrete frameworks at generation time.

## Q&A flow

Ask one question at a time. Wait for the user's answer before asking the next.

### Q1: Free-form intro

> Selam! Sana yardım edeceğim. Önce bana biraz anlat: bu site ne için, kim için olacak? Birkaç cümle yeterli.

(English version: "Tell me about it: what is this site for, and who is it for? A couple of sentences is enough.")

Capture the answer as `goal`.

### Q2: Site scope

> Ne tür bir site yapacağız?
>
> A) Tek sayfa (kısa tanıtım, one-pager)
> B) Çok sayfalı tanıtım (ana sayfa + hakkımızda + iletişim falan, hafif ya da hiç etkileşim yok)
> C) Çok sayfalı + bir-iki etkileşim (form, galeri, küçük JS özellikleri)
> D) Üye girişi / sipariş / veri kaydı olan tam uygulama

Map the answer:
- A → `single-page`
- B → `multi-page-static`
- C → `interactive-static`
- D → `full-app`

Capture as `scope`.

In **dev mode only**, after scope, also ask the preference questions below. In **sade mode**, skip them entirely — the agents will pick reasonable defaults based on scope alone.

### Q2-dev-prefs: Dev mode preferences (only if mode == dev)

#### Q2-dev-prefs-1: Performance vs simplicity

> Bu site için ne daha önemli?
>
> A) Mümkün olduğunca basit ve hızlı kurulum (build step bile olmasın istersen)
> B) Modern, hızlı (küçük bundle, fast page loads)
> C) İçerik/feature ağırlıklı (build complexity sorun değil, ama maintainable olsun)
> D) Fark etmez, sen seç

Capture as `preferences.priority` (one of `simple`, `performance`, `feature-richness`, `claude-decides`).

#### Q2-dev-prefs-2: Interactivity (only ask for `interactive-static` or `full-app`)

> Sitede ne kadar JS-tabanlı etkileşim olacak?
>
> A) Az (sadece bir-iki yerde küçük etkileşim)
> B) Orta (form'lar, küçük UI bileşenleri, biraz dinamik içerik)
> C) Çok (gerçek anlamda app — sürekli state, complex flows)
> D) Fark etmez, sen seç

Capture as `preferences.interactivity` (one of `low`, `medium`, `high`, `claude-decides`).

#### Q2-dev-prefs-3: Backend language (only ask for `full-app`)

> Backend tarafı için bir dil/ekosistem tercihin var mı?
>
> A) Frontend'le aynı paket olsun (tek node projesi)
> B) Ayrı bir Node servisi
> C) Python kullanmak isterim
> D) Go / Rust / başka bir compiled language
> E) Java / .NET ekosistemi
> F) Fark etmez, sen seç

Capture as `preferences.backendLang` (one of `same-as-frontend`, `node-separate`, `python`, `compiled`, `enterprise-jvm`, `claude-decides`).

The plugin does NOT enumerate specific frameworks. The agent picks within whichever language/ecosystem bucket the user chose.

#### Q2-dev-prefs-4: Database (only ask for `full-app`)

> Database için tercihin?
>
> A) En basit (file-based, sıfır ayar — sen seçersin)
> B) Klasik SQL (Postgres ya da benzeri — sen seçersin)
> C) Document DB (MongoDB ya da benzeri — sen seçersin)
> D) Yok / kendim halledeceğim
> E) Fark etmez, sen seç

Capture as `preferences.dbStyle` (one of `simple`, `sql`, `document`, `none`, `claude-decides`).

#### Q2-dev-prefs-5: TypeScript

> TypeScript kullanalım mı?
>
> A) Evet
> B) Hayır
> C) Sen seç (scope'a göre uygun olanı)

Capture as `preferences.typescript` (one of `true`, `false`, `claude-decides`).

The whole point is: dev mode collects user-facing intent ("I want fast", "I prefer Python") — never specific tool names. The agent's job is to translate intent into the most appropriate tool **right now**.

### Q3: Project name

Suggest **3 names** based on the goal description from Q1 — make them concrete (mention location/topic if mentioned), short (kebab-case, ≤20 chars), and distinct. Add a "kendin yaz" option.

Example:

> Sana birkaç isim önerdim — beğenirsen seç, beğenmezsen kendin yaz:
>
> • kadikoy-kahve
> • mavi-kapi-cafe
> • korner-kahve
> • [veya kendin yaz]

Validate the chosen name: must be kebab-case, no spaces, no special characters except `-`. If invalid, ask again.

### Q4: Content source

> İçerik (isim, menü, fotoğraflar, hakkımızda metni vs.) için:
>
> A) Ben vereceğim
> B) Sen örnek içerik üret, sonra değiştiririm

If A: ask follow-ups in a focused way — collect the specific content the user has (name, contact info, page-specific text) in 1-3 follow-up questions, then move on. Don't drag this out.
If B: note in the brief that placeholders will be used.

### Q5: Style preset

> Görsel stil için bir tane seç:
>
> A) Minimalist (sade, beyaz/siyah, az renk)
> B) Playful (renkli, eğlenceli, yuvarlak hatlar)
> C) Kurumsal (ciddi, mavi/gri, klasik)
> D) Vintage (sıcak tonlar, retro fontlar)
> E) Dark/Modern (koyu zemin, vurgulu renkler)

Capture the choice as `stylePreset`.

## Side effects

After all 5 questions are answered:

1. Compute project subdirectory path: `{cwd}/{siteName}/`. If it already exists, ask the user to pick another name.
2. Create the subdirectory: `mkdir -p {projectPath}`.
3. Create `{projectPath}/.web-builder/` directory.
4. Write `{projectPath}/brief.md` using the template below.
5. Write `{projectPath}/.web-builder/state.json` with initial state. Set the following fields:
   - `mode: "simple"` or `"dev"` (as passed by orchestrator)
   - `scope: <captured value from Q2>` (one of `single-page`, `multi-page-static`, `interactive-static`, `full-app`)
   - `siteName: <captured>`
   - `siteLanguage: <detected from user's language>`
   - `createdAt: <ISO timestamp>`
   - `lastModified: <ISO timestamp>`
   - `agentRuns: []` (empty array)
   - `preferences: <only in dev mode; sade mode sets to null or empty {}>`:
     - `priority: <captured from Q2-dev-prefs-1 | null>`
     - `interactivity: <captured from Q2-dev-prefs-2 | null>`
     - `backendLang: <captured from Q2-dev-prefs-3 | null>`
     - `dbStyle: <captured from Q2-dev-prefs-4 | null>`
     - `typescript: <captured from Q2-dev-prefs-5 | null>`
   - `chosenStack: { frontend: null, backend: null, database: null, rationale: null }` (agents populate these on first run)
   - Note: subsequent steps (orchestrator git init, deployer) will add `gitInitialized`, `initialCommitSha`, and `deployment` fields. Intake itself does not need to set these — they default to absent.

## brief.md template

```markdown
# Site Briefi: {siteName}

## Scope
{scope value: single-page | multi-page-static | interactive-static | full-app}

## Amaç
{goal verbatim from Q1}

## Hedef Kitle
{infer 1-2 lines from goal; if unsure, write "Belirtilmedi"}

## Sayfa Listesi
- Ana sayfa
- Hakkımızda
- {plus 1-3 more pages inferred from goal: e.g., "Menü", "Hizmetler", "İletişim"}

## İçerik Kaynağı
{"Kullanıcı verecek" or "Plugin örnek içerik üretecek (kullanıcı sonra düzenleyecek)"}

{If user provided specific content in Q4-A, append a "## Kullanıcı Verdiği İçerik" section listing the items.}

## Stil Tercihi
Hazır stil: {stylePreset name}

## Davranış / Etkileşim
- Statik site, form yok.

## Preferences (only populated in dev mode)
- Priority: {simple | performance | feature-richness | claude-decides | null}
- Interactivity: {low | medium | high | claude-decides | null}
- Backend language: {same-as-frontend | node-separate | python | compiled | enterprise-jvm | claude-decides | null}
- Database style: {simple | sql | document | none | claude-decides | null}
- TypeScript: {true | false | claude-decides | null}
```

If the user is writing in English, use English headings: `Scope`, `Goal`, `Audience`, `Pages`, `Content Source`, `Style`, `Interactivity`, `Preferences`.

## Return value

Return the absolute path of the project subdirectory to the orchestrator.
