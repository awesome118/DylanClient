# GitHub Pages package for the uploaded Eaglercraft HTML

This package splits the original single-file client into 5 binary parts so each file stays below GitHub's browser-upload limit. `index.html` downloads the parts from the same GitHub Pages site and streams the reconstructed HTML into the page.

## Publish using only Chrome on a Chromebook

1. Extract this ZIP using the Chromebook Files app.
2. Create a **public** repository on GitHub. Do not add a README or other starter files when creating it.
3. Open the new empty repository, choose **Add file → Upload files**, and upload **the required files from this extracted folder** (`index.html`, every `client.partXX.bin`, and optionally `README.md` and `manifest.json`). Upload them at the repository root, not inside another folder. The largest part is 18,874,368 bytes (under 18 MiB).
4. Commit the files to the `main` branch.
5. In the repo, open **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, select `main` and `/(root)`, then save.
6. Once Pages finishes deploying, open the `https://YOUR-USERNAME.github.io/REPOSITORY/` URL shown on the Pages settings screen.

If GitHub's upload form struggles with all files at once, upload `index.html` first, then upload the `.bin` parts in two batches. They must all end up in the same repository root.

## Important limitations

- The embedded client Wasm is patched to acknowledge required server resource packs without downloading/reloading them. Server-provided pack textures will not load; Hypixel may still reject this unofficial browser client.
- The source HTML is an unofficial browser client. Hosting it on GitHub does not make it an officially supported way to access Hypixel, and Hypixel may refuse connections from it.
- The repository must be public for the free GitHub Pages setup described above. Anyone can view and download these files. Do not add passwords, access tokens, or other private information.
- On first load, the page fetches about 78.8 MiB of client data. Keep the tab open; a low-memory Chromebook may reload or struggle.

## Integrity

Original file: `eaglercraft-26.2-r1b-nomusic.html`

Original bytes: 84,938,122

Original SHA-256: `1fc41c888077bf1bb63d298f8e812c443e008e75ef7c549592d4be260737202a`

The loader verifies the combined byte count before loading. Part hashes are recorded in `manifest.json` for optional verification.
