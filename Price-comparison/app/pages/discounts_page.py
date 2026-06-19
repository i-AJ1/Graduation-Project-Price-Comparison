import flet as ft
from db import query
from session import session
from components import (
    card, outlined_button, badge, empty_state,
    PRIMARY, DANGER, TEXT, TEXT_MUTED, BG
)

def discounts_page(page: ft.Page, navigate):
    # ─── FIX: session.user_id could be None, use 0 as fallback ───
    uid = session.user_id if session.user_id else 0

    products = query("""
        SELECT DISTINCT p.*, c.name as category_name,
        (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price,
        (SELECT old_price FROM product_stores WHERE product_id = p.id AND old_price > price LIMIT 1) as old_price,
        EXISTS(SELECT 1 FROM favorites WHERE user_id = %s AND product_id = p.id) as is_favorite
        FROM products p
        JOIN product_stores ps ON p.id = ps.product_id
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE ps.old_price > ps.price
    """, (uid,))

    def discount_pct(old, new):
        if old and new and old > 0:
            return int((1 - new / old) * 100)
        return 0

    def discount_card(p):
        old = p.get('old_price')
        new = p.get('min_price')
        pct = discount_pct(old, new) if old and new else 0
        pid = p['id']

        discount_badge = ft.Container(
            content=ft.Text(f"-{pct}%", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            bgcolor=DANGER,
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
        )

        return card(
        ft.Column([
            ft.Row([
                ft.Container(expand=True),
                discount_badge,
            ]),
            ft.Image(
                src=p.get('image', ''),
                height=110,
                fit="contain",
                error_content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, color=TEXT_MUTED, size=32),
            ),
            ft.Container(height=4),
            badge(p.get('category_name', ''), PRIMARY),
            ft.Text(p.get('name', ''), size=12, weight=ft.FontWeight.W_600,
                    color=TEXT, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
            ft.Container(height=2),
            ft.Row([
                ft.Text(f"{new} ر", size=14, weight=ft.FontWeight.BOLD, color=DANGER),
                ft.Container(width=4),
                ft.Text(
                    f"{old} ر",
                    size=11,
                    color=TEXT_MUTED,
                    style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
                ) if old else ft.Container(),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=6),
            
        ], spacing=3),
        padding=10,
        on_click=lambda e, i=pid: navigate("product", i)  # 👈 هذا اللي يخلي الكارد كله تفاعلي
    )

    # Header
    header = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT, color=DANGER, size=26),
                ft.Text("أقوى عروض اليوم", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ], spacing=8),
            ft.Text("وفر مع أفضل الخصومات من كافة المتاجر",
                    size=12, color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE)),
        ], spacing=6),
        gradient=ft.LinearGradient(["#C62828", "#E53935"], begin=ft.Alignment(-1, -1),
                                    end=ft.Alignment(1, 1)),
        border_radius=12,
        padding=ft.padding.symmetric(vertical=18, horizontal=16),
        margin=ft.margin.only(bottom=14),
    )

    # ─── 2-column grid ───
    def build_grid(products):
        rows = []
        for i in range(0, len(products), 2):
            pair = products[i:i+2]
            row_items = [ft.Container(content=discount_card(p), expand=True) for p in pair]
            if len(row_items) == 1:
                row_items.append(ft.Container(expand=True))
            rows.append(ft.Row(row_items, spacing=10))
        return ft.Column(rows, spacing=10)

    grid = build_grid(products) if products else empty_state(
        ft.Icons.DISCOUNT_OUTLINED, "لا توجد عروض حالية، تفقد الصفحة لاحقاً!"
    )

    return ft.Column([header, grid], scroll=ft.ScrollMode.AUTO, spacing=0)