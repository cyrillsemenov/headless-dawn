import os
import shutil
import json


def build_theme():
    dist_dir = "dist"
    dawn_dir = "dawn"
    redirect_dir = "hydrogen-redirect"

    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)

    print("Copying Dawn theme base...")
    shutil.copytree(
        dawn_dir, dist_dir, ignore=shutil.ignore_patterns(".git", ".github")
    )

    print("Injecting redirect templates...")
    templates_dir = os.path.join(redirect_dir, "templates")
    if os.path.exists(templates_dir):
        for item in os.listdir(templates_dir):
            if item.endswith(".json") and item != "cart.json":
                src = os.path.join(templates_dir, item)
                dst = os.path.join(dist_dir, "templates", item)
                shutil.copy2(src, dst)

    print("Injecting redirect section...")
    section_src = os.path.join(redirect_dir, "sections", "main-redirect.liquid")
    if os.path.exists(section_src):
        os.makedirs(os.path.join(dist_dir, "sections"), exist_ok=True)
        shutil.copy2(
            section_src, os.path.join(dist_dir, "sections", "main-redirect.liquid")
        )

    print("Merging settings schema...")
    redirect_schema_path = os.path.join(redirect_dir, "config", "settings_schema.json")
    dawn_schema_path = os.path.join(dist_dir, "config", "settings_schema.json")

    if os.path.exists(redirect_schema_path) and os.path.exists(dawn_schema_path):
        with open(redirect_schema_path, "r", encoding="utf-8") as f:
            redirect_schema = json.load(f)
        with open(dawn_schema_path, "r", encoding="utf-8") as f:
            dawn_schema = json.load(f)

        storefront_settings = [section for section in redirect_schema if section.get("name") != "theme_info"]
        dawn_schema.extend(storefront_settings)

        with open(dawn_schema_path, "w", encoding="utf-8") as f:
            json.dump(dawn_schema, f, indent=2)

    print("Injecting redirect logic into layout/theme.liquid...")
    theme_liquid_path = os.path.join(dist_dir, "layout", "theme.liquid")
    redirect_theme_liquid_path = os.path.join(redirect_dir, "layout", "theme.liquid")

    if os.path.exists(theme_liquid_path) and os.path.exists(redirect_theme_liquid_path):
        with open(redirect_theme_liquid_path, "r", encoding="utf-8") as f:
            redirect_content = f.read()

        redirect_logic = ""
        script_start = redirect_content.rfind(
            "<script>", 0, redirect_content.find("function getCookie(name)")
        )
        script_end = redirect_content.find("</script>", script_start)

        if script_start != -1 and script_end != -1:
            redirect_logic = redirect_content[script_start : script_end + 9]

        with open(theme_liquid_path, "r", encoding="utf-8") as f:
            theme_content = f.read()

        head_end_idx = theme_content.find("</head>")
        if head_end_idx != -1:
            injection = f"""
    {{%- assign should_redirect = false -%}}
    {{%- if template != blank and template.name != 'cart' and template.name != 'login' and template.name != 'register' and template.name != 'account' and template.name != 'addresses' and template.name != 'order' -%}}
      {{%- assign should_redirect = true -%}}
    {{%- endif -%}}
    {{%- if settings.storefront_hostname != blank and should_redirect -%}}
      {redirect_logic}
    {{%- endif -%}}
"""
            theme_content = (
                theme_content[:head_end_idx] + injection + theme_content[head_end_idx:]
            )

            div_start = redirect_content.find('<div class="redirect">')
            div_end = redirect_content.find("</div>", div_start)
            if div_start != -1 and div_end != -1:
                html_logic = redirect_content[div_start : div_end + 6]
                body_start_idx = theme_content.find("<body")
                body_end_idx = theme_content.find(">", body_start_idx)
                if body_end_idx != -1:
                    injection_html = f"""
    {{%- if should_redirect -%}}
      {html_logic}
    {{%- endif -%}}
"""
                    theme_content = (
                        theme_content[: body_end_idx + 1]
                        + injection_html
                        + theme_content[body_end_idx + 1 :]
                    )

            with open(theme_liquid_path, "w", encoding="utf-8") as f:
                f.write(theme_content)

    print("Build complete! Theme generated in dist/")


if __name__ == "__main__":
    build_theme()
