import flet as ft
from db import query
from session import session
from components import (
    card, outlined_button, badge, empty_state,
    PRIMARY, TEXT, TEXT_MUTED
)

def search_page(page: ft.Page, navigate, search_query=""):
    search_ref = ft.Ref[ft.TextField]()
    results_ref = ft.Ref[ft.Column]()

    def do_search(e=None):
        q = search_ref.current.value.strip()
        if not q:
            return
        products = query("""
            SELECT p.*, c.name as category_name,
            (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.name LIKE %s OR p.description LIKE %s
        """, (session.user_id if session.user_id else None, f'%{q}%', f'%{q}%') if False
             else (f'%{q}%', f'%{q}%'))

        if products:
            cards = [
                ft.Column([
                    card(ft.Column([
                        ft.Image(src=p.get('image', ''), height=120, fit="contain",
                                  error_content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, color=TEXT_MUTED, size=30)),
                        ft.Container(height=6),
                        badge(p.get('category_name', ''), PRIMARY),
                        ft.Text(p.get('name', ''), size=13, weight=ft.FontWeight.W_600, color=TEXT,
                                max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"يبدأ من: {p.get('min_price') or '?'} ريال", size=12,
                                color=PRIMARY, weight=ft.FontWeight.BOLD),
                        ft.Container(height=6),
                        outlined_button("مقارنة الأسعار",
                                        on_click=lambda e, i=p['id']: navigate("product", i),
                                        width=float('inf')),
                    ], spacing=4), padding=10)
                ], col={"xs": 12, "sm": 6, "md": 3})
                for p in products
            ]
            results_ref.current.controls = [
                ft.Text(f"تم العثور على {len(products)} منتج", size=13, color=TEXT_MUTED),
                ft.Container(height=10),
                ft.ResponsiveRow(cards, spacing=12, run_spacing=12)
            ]
        else:
            results_ref.current.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, size=56, color=TEXT_MUTED),
                        ft.Text("لم نجد ما تبحث عنه", size=16, color=TEXT_MUTED),
                        ft.Text("تأكد من الكلمة أو جرب كلمات أخرى", size=13, color=TEXT_MUTED),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    alignment=ft.Alignment(0, 0),
                    padding=40,
                )
            ]
        page.update()

    # Run search if query provided
    initial_results = ft.Column([], spacing=0)

    search_bar = ft.Row([
        ft.TextField(
            ref=search_ref,
            hint_text="ابحث عن منتج...",
            value=search_query,
            expand=True,
            border_radius=10,
            prefix_icon=ft.Icons.SEARCH,
            border_color="#E0E0E0",
            focused_border_color=PRIMARY,
            on_submit=do_search,
            text_align=ft.TextAlign.RIGHT,
        ),
        ft.ElevatedButton(
            "بحث",
            on_click=do_search,
            style=ft.ButtonStyle(
                bgcolor=PRIMARY, color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=24, vertical=14),
            )
        ),
    ], spacing=10)

    view = ft.Column([
        ft.Text("البحث عن منتج", size=22, weight=ft.FontWeight.BOLD, color=TEXT),
        ft.Container(height=12),
        search_bar,
        ft.Container(height=20),
        ft.Column(ref=results_ref, controls=[], spacing=0),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)

    # Trigger search if query passed
    if search_query:
        import threading
        def delayed():
            import time; time.sleep(0.1)
            do_search()
        threading.Thread(target=delayed, daemon=True).start()

    return view