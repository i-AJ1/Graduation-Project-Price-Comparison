import flet as ft
from db import query
from session import session
from components import (
    card, outlined_button, empty_state, snack,
    PRIMARY, DANGER, TEXT, TEXT_MUTED, SUCCESS
)

def favorites_page(page: ft.Page, navigate):
    if not session.is_logged_in():
        return ft.Column([
            ft.Container(height=40),
            ft.Column([
                ft.Icon(ft.Icons.LOCK_OUTLINE, size=64, color=TEXT_MUTED),
                ft.Text("يجب تسجيل الدخول لعرض المفضلة", size=16, color=TEXT_MUTED),
                ft.ElevatedButton("تسجيل الدخول", on_click=lambda e: navigate("login")),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    favorites = query("""
        SELECT p.*,
        (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price
        FROM products p
        JOIN favorites f ON p.id = f.product_id
        WHERE f.user_id = %s
    """, (session.user_id,))

    def remove_fav(product_id):
        query("DELETE FROM favorites WHERE user_id=%s AND product_id=%s",
              (session.user_id, product_id), commit=True)
        snack(page, "تمت الإزالة من المفضلة")
        navigate("favorites")

    def fav_card(p):
        pid = p['id']
        price_text = f"{p['min_price']} ر" if p.get('min_price') else "غير محدد"
        return card(
            ft.Column([
                ft.Image(
                    src=p.get('image', ''),
                    height=110,
                    fit="contain",
                    error_content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, color=TEXT_MUTED, size=32),
                ),
                ft.Container(height=4),
                ft.Text(p.get('name', ''), size=12, weight=ft.FontWeight.W_600,
                        color=TEXT, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(f"أقل: {price_text}", size=11, color=PRIMARY, weight=ft.FontWeight.BOLD),
                ft.Container(height=8),
                ft.Row([
                    ft.Container(
                        
                        expand=True,
                    ),
                    ft.Container(width=6),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=DANGER,
                        icon_size=18,
                        padding=0,
                        on_click=lambda e, i=pid: remove_fav(i),
                        tooltip="حذف من المفضلة",
                    ),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=3),
            padding=10,
            on_click=lambda e, i=pid: navigate("product", i)
        )

    # ─── 2-column grid ───
    def build_grid(items):
        rows = []
        for i in range(0, len(items), 2):
            pair = items[i:i+2]
            row_items = [ft.Container(content=fav_card(p), expand=True) for p in pair]
            if len(row_items) == 1:
                row_items.append(ft.Container(expand=True))
            rows.append(ft.Row(row_items, spacing=10))
        return ft.Column(rows, spacing=10)

    grid = build_grid(favorites) if favorites else empty_state(
        ft.Icons.FAVORITE_BORDER,
        "قائمة المفضلة فارغة حالياً",
        "تصفح المنتجات",
        lambda e: navigate("home")
    )

    return ft.Column([
        ft.Row([
            ft.Icon(ft.Icons.FAVORITE, color=DANGER, size=22),
            ft.Text("قائمة مفضلاتي", size=20, weight=ft.FontWeight.BOLD, color=TEXT),
            ft.Container(expand=True),
            ft.Text(f"{len(favorites)} منتج", size=12, color=TEXT_MUTED),
        ], spacing=8),
        ft.Container(height=14),
        grid,
    ], scroll=ft.ScrollMode.AUTO)