import flet as ft
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from session import session
from components import PRIMARY, BG, TEXT, TEXT_MUTED, DANGER


# Import all pages
from pages.home_page import home_page
from pages.categories_page import categories_page
from pages.product_page import product_page
from pages.discounts_page import discounts_page
from pages.favorites_page import favorites_page
from pages.login_page import login_page
from pages.register_page import register_page
from pages.profile_page import profile_page
from pages.search_page import search_page




def main(page: ft.Page):
    
    
    page.title = "مقارنة الأسعار"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = BG
    page.fonts = {
        "Cairo": "https://fonts.gstatic.com/s/cairo/v28/SLXgc1nY6HkvalIkTp2KeWY.woff2",
    }
    page.theme = ft.Theme(
        font_family="Cairo",
        color_scheme=ft.ColorScheme(
            primary=PRIMARY,
            on_primary=ft.Colors.WHITE,
        )
    )
    page.padding = 0

    # ─── Current page state ───
    current_page = {"name": "home", "args": {}}
    content_area = ft.Ref[ft.Container]()
    nav_ref = ft.Ref[ft.NavigationBar]()

    def navigate(page_name, *args, **kwargs):
        current_page["name"] = page_name
        arg = args[0] if args else None

        if page_name == "home":
            view = home_page(page, navigate)
        elif page_name == "categories":
            view = categories_page(page, navigate, arg)
        elif page_name == "product":
            view = product_page(page, navigate, arg)
        elif page_name == "discounts":
            view = discounts_page(page, navigate)
        elif page_name == "favorites":
            view = favorites_page(page, navigate)
        elif page_name == "login":
            view = login_page(page, navigate)
        elif page_name == "register":
            view = register_page(page, navigate)
        elif page_name == "profile":
            view = profile_page(page, navigate)
    
        elif page_name == "search":
            view = search_page(page, navigate, arg or "")
        else:
            view = home_page(page, navigate)

        if content_area.current:
            content_area.current.content = view
            update_ui_state(page_name)

    def update_ui_state(page_name):
        page.appbar = build_appbar()

        nav_map = {"home": 0, "categories": 1, "discounts": 2, "favorites": 3}

        if page_name in nav_map:
            page.navigation_bar.visible = True
            nav_ref.current.selected_index = nav_map[page_name]
        else:
            page.navigation_bar.visible = False

        page.update()

    # ─── App Bar ───
    def build_appbar():
        actions = []

        actions.append(
            ft.IconButton(
                icon=ft.Icons.SEARCH,
                icon_color=ft.Colors.WHITE,
                on_click=lambda e: navigate("search"),
                tooltip="بحث",
            )
        )

        if session.is_logged_in():
            # ─── FIX: PopupMenuItem uses content= not text= ───
            menu_items = [
                ft.PopupMenuItem(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color=PRIMARY, size=18),
                        ft.Text(f"مرحباً، {session.username}", size=13),
                    ], spacing=8),
                    on_click=lambda e: navigate("profile"),
                ),
                ft.PopupMenuItem(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SETTINGS, color=TEXT_MUTED, size=18),
                        ft.Text("الملف الشخصي", size=13),
                    ], spacing=8),
                    on_click=lambda e: navigate("profile"),
                ),
                ft.PopupMenuItem(
                    content=ft.Row([
                        ft.Icon(ft.Icons.FAVORITE, color=DANGER, size=18),
                        ft.Text("المفضلة", size=13),
                    ], spacing=8),
                    on_click=lambda e: navigate("favorites"),
                ),
                ft.PopupMenuItem(),  # Divider
            ]
            if session.is_admin:
                
                menu_items.append(
                ft.PopupMenuItem(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOGOUT, color=DANGER, size=18),
                        ft.Text("تسجيل الخروج", size=13, color=DANGER),
                    ], spacing=8),
                    on_click=lambda e: logout(),
                )
            )
            actions.append(
                ft.PopupMenuButton(
                    icon=ft.Icons.PERSON,
                    icon_color=ft.Colors.WHITE,
                    items=menu_items,
                )
            )
        else:
            actions.append(
                ft.TextButton(
                    "دخول",
                    icon=ft.Icons.LOGIN,
                    on_click=lambda e: navigate("login"),
                    style=ft.ButtonStyle(color=ft.Colors.WHITE),
                )
            )

        return ft.AppBar(
            leading=ft.IconButton(
            icon=ft.Icons.LOCAL_OFFER,
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: navigate("home"),
            ),
            leading_width=44,
            title=ft.Text("مقارنة الأسعار", color=ft.Colors.WHITE, size=18,
                           weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=PRIMARY,
            actions=actions,
        )

    def logout():
        session.logout()
        navigate("home")

    # ─── Bottom Navigation Bar ───
    def on_nav_change(e):
        destinations = ["home", "categories", "discounts", "favorites"]
        navigate(destinations[e.control.selected_index])

    nav_bar = ft.NavigationBar(
        ref=nav_ref,
        selected_index=0,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="الرئيسية",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.GRID_VIEW_OUTLINED,
                selected_icon=ft.Icons.GRID_VIEW,
                label="الفئات",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.LOCAL_OFFER_OUTLINED,
                selected_icon=ft.Icons.LOCAL_OFFER,
                label="الخصومات",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.FAVORITE_OUTLINE,
                selected_icon=ft.Icons.FAVORITE,
                label="المفضلة",
            ),
        ],
        bgcolor=ft.Colors.WHITE,
        indicator_color=ft.Colors.with_opacity(0.15, PRIMARY),
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
    )

    

    # ─── Main Layout ───
    page.appbar = build_appbar()

    main_content = ft.Container(
        ref=content_area,
        expand=True,
        bgcolor=BG,
        padding=ft.padding.symmetric(horizontal=14, vertical=12),
    )

    page.add(main_content)
    page.navigation_bar = nav_bar

    navigate("home")

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)
