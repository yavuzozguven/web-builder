#!/usr/bin/env python3
"""Generate an asciinema v2 cast simulating a /web-builder:start session.

Run: python3 docs/build-demo.py > docs/demo.cast
Then: agg --theme monokai --font-size 16 --speed 1.0 docs/demo.cast docs/demo.gif
"""
import json
import sys

# ANSI helpers
R = "\x1b[0m"
B = "\x1b[1m"
DIM = "\x1b[2m"
CYAN = "\x1b[36m"
BCYAN = "\x1b[1;36m"
GREEN = "\x1b[32m"
BGREEN = "\x1b[1;32m"
YELLOW = "\x1b[33m"
MAGENTA = "\x1b[35m"
GRAY = "\x1b[90m"
WHITE = "\x1b[97m"

WIDTH = 92
HEIGHT = 28

events = []
t = 0.0


def out(text, dt=0.0):
    """Append an output event after dt seconds."""
    global t
    t += dt
    events.append([round(t, 3), "o", text])


def typewrite(text, char_delay=0.04):
    """Simulate human typing, char by char."""
    for ch in text:
        out(ch, char_delay)


def pause(dt):
    global t
    t += dt


# === Scene ===

# Shell prompt
out(f"{BCYAN}~/projects{R} {GRAY}❯{R} ", 0.5)
typewrite("claude", 0.05)
out("\r\n", 0.3)

# Claude banner
pause(0.4)
out(f"{DIM}● Claude Code v2.1 — Opus 4.7{R}\r\n", 0.0)
out(f"{DIM}  Plugin: web-builder@1.0.0 loaded{R}\r\n\r\n", 0.2)

# Claude prompt
out(f"{BCYAN}>{R} ", 0.4)
typewrite("/web-builder:start", 0.04)
out("\r\n\r\n", 0.5)

# Plugin response Q1
pause(0.5)
out(f"{BGREEN}●{R} {B}web-builder{R} {DIM}— intake{R}\r\n", 0.0)
out(f"\r\n", 0.1)
out(f"  {WHITE}Hi! Let's build you a website.{R}\r\n", 0.5)
out(f"  {WHITE}I'll ask a few quick questions.{R}\r\n\r\n", 0.4)
out(f"  {B}1.{R} What kind of site do you want? Tell me in your own words.\r\n\r\n", 0.6)

# User answer Q1
out(f"  {BCYAN}>{R} ", 0.6)
typewrite("a small promo site for my coffee shop in brooklyn —", 0.025)
out(" ", 0.05)
typewrite("coffee + sandwiches, neighborhood vibe", 0.025)
out("\r\n\r\n", 0.5)

# Plugin Q2
pause(0.6)
out(f"  {GRAY}got it. sounds like a multi-page promo site:{R}\r\n", 0.4)
out(f"  {GRAY}  home / menu / about / contact{R}\r\n\r\n", 0.3)
out(f"  {B}2.{R} Does that match what you have in mind?\r\n\r\n", 0.4)
out(f"     {YELLOW}A){R} yes, multi-page promo\r\n", 0.15)
out(f"     {YELLOW}B){R} simpler — one page is enough\r\n", 0.1)
out(f"     {YELLOW}C){R} more complex (sign-in, orders, etc.)\r\n\r\n", 0.1)

out(f"  {BCYAN}>{R} ", 0.6)
typewrite("A", 0.1)
out("\r\n\r\n", 0.5)

# Plugin Q3 — name
pause(0.4)
out(f"  {B}3.{R} Pick a name (or write your own):\r\n\r\n", 0.4)
out(f"     {YELLOW}A){R} brooklyn-coffee\r\n", 0.12)
out(f"     {YELLOW}B){R} corner-coffee\r\n", 0.1)
out(f"     {YELLOW}C){R} third-wave-bk\r\n", 0.1)
out(f"     {YELLOW}D){R} write your own\r\n\r\n", 0.1)

out(f"  {BCYAN}>{R} ", 0.5)
typewrite("A", 0.1)
out("\r\n\r\n", 0.4)

# Q4 content source (compressed)
pause(0.3)
out(f"  {B}4.{R} Content: {YELLOW}A){R} I'll provide  {YELLOW}B){R} generate placeholders\r\n", 0.4)
out(f"  {BCYAN}>{R} ", 0.5)
typewrite("B", 0.1)
out("\r\n\r\n", 0.3)

# Q5 style
out(f"  {B}5.{R} Visual style: {YELLOW}A){R} minimalist  {YELLOW}B){R} warm  {YELLOW}C){R} playful  {YELLOW}D){R} corporate  {YELLOW}E){R} dark\r\n", 0.4)
out(f"  {BCYAN}>{R} ", 0.5)
typewrite("B", 0.1)
out("\r\n\r\n", 0.5)

# Pipeline running
pause(0.4)
out(f"{BGREEN}●{R} {B}web-builder{R} {DIM}— generating brooklyn-coffee/{R}\r\n\r\n", 0.0)

out(f"  {GREEN}▸{R} ui-ux-designer       ", 0.5)
out(f"{GRAY}thinking...{R}", 0.3)
out(f"\r  {GREEN}✓{R} ui-ux-designer       {DIM}style-guide.md written         (warm browns + cream){R}\r\n", 1.2)

out(f"  {GREEN}▸{R} content-writer       {GRAY}+ seo-expert (parallel)...{R}", 0.4)
out(f"\r  {GREEN}✓{R} content-writer       {DIM}content.md written             (4 pages){R}              \r\n", 1.4)
out(f"  {GREEN}✓{R} seo-expert           {DIM}seo.md written                 (titles, sitemap, robots){R}\r\n", 0.4)

out(f"  {GREEN}▸{R} frontend-expert      {GRAY}picking stack...{R}", 0.5)
out(f"\r  {GREEN}✓{R} frontend-expert      {DIM}picked Astro + Tailwind        (content-focused SSG){R}     \r\n", 1.3)
out(f"  {GRAY}                       running pnpm install + build...{R}", 0.4)
out(f"\r  {GREEN}✓{R} frontend-expert      {DIM}4 pages, build succeeded       (dist/ ready){R}            \r\n", 1.5)

out(f"  {GREEN}▸{R} accessibility-reviewer ", 0.4)
out(f"\r  {GREEN}✓{R} accessibility-reviewer {DIM}a11y clean — no issues found{R}                        \r\n\r\n", 1.0)

# Final success
pause(0.5)
out(f"  {BGREEN}✓ Generated{R} {B}brooklyn-coffee/{R}\r\n", 0.3)
out(f"    {DIM}Astro + Tailwind · 4 pages · SEO + sitemap · a11y clean{R}\r\n\r\n", 0.3)

out(f"  Preview at {CYAN}http://localhost:4321{R}? {DIM}(Y/n){R} ", 0.6)
typewrite("Y", 0.15)
out("\r\n", 0.3)
out(f"  {GREEN}▸{R} starting dev server...\r\n", 0.4)
out(f"  {GREEN}✓{R} {CYAN}http://localhost:4321{R} {DIM}— say 'stop' to close{R}\r\n", 0.8)

# Hold on final frame
pause(2.0)

# Header
header = {
    "version": 2,
    "width": WIDTH,
    "height": HEIGHT,
    "timestamp": 1746748800,
    "env": {"TERM": "xterm-256color", "SHELL": "/bin/zsh"},
    "title": "web-builder demo",
}

print(json.dumps(header))
for ev in events:
    print(json.dumps(ev))
