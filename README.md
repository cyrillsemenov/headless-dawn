# Headless Dawn Theme 

Build wrapper combining [Shopify Dawn](https://github.com/Shopify/dawn) and [Hydrogen Redirect Theme](https://github.com/Shopify/hydrogen-redirect-theme).

**Goal**: Headless index/product/collection + native Dawn for cart/account.

## Architecture

- **Submodules**: `dawn/`, `hydrogen-redirect/`
- **`build.py`**: Merges themes. Swaps JSON templates for redirects, injects redirect snippet into `theme.liquid`. Outputs to `dist/`.

## Commands

```bash
# 1. Setup
git clone --recursive https://github.com/cyrillsemenov/headless-dawn.git

# 2. Build
uv run python build.py

# 3. Test
shopify theme dev --path dist
```

**CI**: GitHub Action builds `.zip` artifact automatically on push.
