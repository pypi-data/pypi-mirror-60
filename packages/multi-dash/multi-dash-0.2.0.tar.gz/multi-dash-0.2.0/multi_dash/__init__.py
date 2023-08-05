from importlib import import_module

import dash
from flask import render_template

# from flask_login import login_required
from .index import dash_index


def slugify(string):
    return string.lower().replace(" ", "_")


class MultiDash:
    def __init__(
        self,
        server,
        *,
        index_slug="",
        template="base.html",
        default_dash_stylesheets=None,
        login_guard=lambda x: x,
    ):
        self.server = server
        self.template = template
        self.index_slug = slugify(index_slug)
        self.default_dash_stylesheets = default_dash_stylesheets or []

        self.pages = []

        server.route("/", endpoint="index")(login_guard(self.show_page))
        server.route("/show/<slug>", endpoint="show")(login_guard(self.show_page))

        server.register_blueprint(dash_index)

    def route(self, *args, **kwargs):
        def decorator(f):
            self.server.route(*args, **kwargs)(login_guard(f))

        return decorator

    def show_page(self, slug=None):
        slug = slug or self.index_slug
        if not slug and self.pages:
            slug = self.pages[0]["slug"]

        selected_page = next(filter(lambda d: d["slug"] == slug, self.pages), None)
        return render_template(
            self.template, pages=self.pages, selected_page=selected_page
        )

    def register_dash(
        self,
        module_name,
        title,
        slug=None,
        icon=None,
        ignore_default_stylesheets=False,
        hide_in_menu=False,
    ):
        """
        Example usage:

            register("simon.db1", "My dashboard", "check-icon")
        """

        slug = slug or slugify(title)
        page_url = f"/internal/{slug}"
        url = f"/show/{slug}"

        def factory(name, **kwargs):
            external_stylesheets = kwargs.pop("external_stylesheets", [])
            if not ignore_default_stylesheets:
                external_stylesheets = (
                    external_stylesheets + self.default_dash_stylesheets
                )
            return dash.Dash(
                name,
                server=self.server,
                url_base_pathname=f"{page_url}/",
                external_stylesheets=external_stylesheets,
                **kwargs,
            )

        import_module(module_name).create_app(factory)

        self.pages.append(
            dict(
                kind="dash",
                slug=slug,
                title=title,
                icon=icon,
                page_url=page_url,
                url=url,
                hide_in_menu=hide_in_menu,
            )
        )

        return self

    def register_page(self, page_url, title, slug=None, icon=None):
        slug = slug or slugify(title)
        url = f"/show/{slug}"
        self.pages.append(
            dict(
                kind="page",
                title=title,
                icon=icon,
                page_url=page_url,
                url=url,
                slug=slug,
                hide_in_menu=False,
            )
        )
        return self

    def register_health(self, url):
        self.server.route(url)(lambda: "healthy")
        return self
