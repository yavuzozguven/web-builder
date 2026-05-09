# SEO: brooklyn-coffee

## Site-wide

- Default site name (used in `<title>` template): Brooklyn Coffee
- Default description (homepage fallback): Brooklyn's little coffee shop — third-wave coffee and homemade sandwiches.
- Default keywords: brooklyn coffee, third-wave coffee, homemade sandwiches, neighborhood cafe
- Open Graph image policy:
  - Style: warm, low-key, neighborhood-cafe vibe — single warm-tone hero
  - Recommended dimensions: 1200x630
  - Placeholder URL: https://picsum.photos/seed/cafe/1200/630
  - PLACEHOLDER: yes

## Per-page SEO

### Page: Home (/)
- Title: Brooklyn Coffee — The neighborhood's little coffee shop
- Meta description: Third-wave coffee and homemade sandwiches in Brooklyn. The neighborhood's gathering spot.
- Canonical: /
- Open Graph: title=Brooklyn Coffee, description=The neighborhood's little coffee shop, type=website, image=site-wide
- Indexable: yes

### Page: Menu (/menu)
- Title: Menu — Brooklyn Coffee
- Meta description: Our third-wave coffee and homemade sandwich menu. Fresh every morning.
- Canonical: /menu
- Open Graph: title=Menu, description=Our coffee and sandwich menu, type=website, image=site-wide
- Indexable: yes

### Page: About (/about)
- Title: About — Brooklyn Coffee
- Meta description: We've been in Brooklyn since 2018. Our little cafe, founded by three friends.
- Canonical: /about
- Open Graph: title=About, description=Our cafe's story, type=website, image=site-wide
- Indexable: yes

### Page: Contact (/contact)
- Title: Contact — Brooklyn Coffee
- Meta description: We're on Brooklyn's Main Street. Phone, map, hours.
- Canonical: /contact
- Open Graph: title=Contact, description=Our address and hours, type=website, image=site-wide
- Indexable: yes

## Sitemap

- / (priority 1.0, changefreq weekly)
- /menu (priority 0.8, changefreq weekly)
- /about (priority 0.5, changefreq monthly)
- /contact (priority 0.5, changefreq monthly)

## robots.txt

User-agent: *
Allow: /

Sitemap: https://{deployedDomain}/sitemap.xml
