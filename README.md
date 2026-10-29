# halawipartners.com

Website of Halawi & Partners, built by `build.py` from the content in `content/` and the images in `media/`, and published on GitHub Pages by the workflow in `.github/workflows/pages.yml`.

- Edit content at https://halawipartners.com/admin (sign in with GitHub). Every save rebuilds the site in about a minute.
- Or edit the JSON files in `content/` directly.
- Build locally: `pip install -r requirements.txt && python3 build.py`, then open `public/index.html`.
- Sign-in to the content manager still goes through the Netlify project "halawipartners" (Project configuration, Security, OAuth). Keep that project. Its builds are stopped, so it no longer publishes the site.
