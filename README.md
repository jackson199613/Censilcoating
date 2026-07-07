# Censilcoating

Marketing website for **Censilcoating** — waterborne silica matting agents, a 1:1 performance match for European premium brands (Evonik ACEMATT® / Grace SYLOID®), built for Southeast Asia.

## Stack

Static site — plain HTML + Tailwind CSS (via CDN). No build step required.

## Pages

- `index.html` — Home
- `products.html` — Product range, application selector, specs, technology, documents
- `solutions.html` — Three matting solutions with case data
- `about.html` — Company positioning
- `contact.html` — Free-sample request form
- `blog.html` — Resources / articles

## Deploy (Netlify)

This repo is a static site — no build command needed.

- **Build command:** *(leave empty)*
- **Publish directory:** `.` (repository root)

Netlify will serve `index.html` as the entry point automatically.

## Notes

- `censilcoating.com` is a placeholder domain in the meta tags / sitemap — replace with the real domain before launch.
- The sample-request form is front-end only; connect it to a form backend (e.g. Netlify Forms) to receive submissions.
