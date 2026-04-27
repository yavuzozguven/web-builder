# SEO: kadikoy-kahve

## Site-wide

- Default site name (used in `<title>` template): Kadıköy Kahve
- Default description (homepage fallback): Kadıköy'ün küçük kahvecisi — üçüncü dalga kahve ve ev yapımı sandviçler.
- Default keywords: kadıköy kahve, üçüncü dalga kahve, ev yapımı sandviç, mahalle kafesi
- Open Graph image policy:
  - Style: warm, low-key, neighborhood-cafe vibe — single warm-tone hero
  - Recommended dimensions: 1200x630
  - Placeholder URL: https://picsum.photos/seed/cafe/1200/630
  - PLACEHOLDER: yes

## Per-page SEO

### Page: Ana sayfa (/)
- Title: Kadıköy Kahve — Mahallenin küçük kahvecisi
- Meta description: Kadıköy'de üçüncü dalga kahve ve ev yapımı sandviçler. Mahallenin buluşma noktası.
- Canonical: /
- Open Graph: title=Kadıköy Kahve, description=Mahallenin küçük kahvecisi, type=website, image=site-wide
- Indexable: yes

### Page: Menü (/menu)
- Title: Menü — Kadıköy Kahve
- Meta description: Üçüncü dalga kahve ve ev yapımı sandviç menümüz. Her sabah taze.
- Canonical: /menu
- Open Graph: title=Menü, description=Kahve ve sandviç menümüz, type=website, image=site-wide
- Indexable: yes

### Page: Hakkımızda (/hakkimizda)
- Title: Hakkımızda — Kadıköy Kahve
- Meta description: 2018'den beri Kadıköy'deyiz. Üç arkadaşın kurduğu küçük kafemiz.
- Canonical: /hakkimizda
- Open Graph: title=Hakkımızda, description=Kafemizin hikayesi, type=website, image=site-wide
- Indexable: yes

### Page: İletişim (/iletisim)
- Title: İletişim — Kadıköy Kahve
- Meta description: Kadıköy Moda Caddesi'ndeyiz. Telefon, harita, çalışma saatleri.
- Canonical: /iletisim
- Open Graph: title=İletişim, description=Adresimiz ve çalışma saatleri, type=website, image=site-wide
- Indexable: yes

## Sitemap

- / (priority 1.0, changefreq weekly)
- /menu (priority 0.8, changefreq weekly)
- /hakkimizda (priority 0.5, changefreq monthly)
- /iletisim (priority 0.5, changefreq monthly)

## robots.txt

User-agent: *
Allow: /

Sitemap: https://{deployedDomain}/sitemap.xml
