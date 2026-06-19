import flet as ft
from db import query
from session import session
from components import (
    card, primary_button, outlined_button, badge,
    section_title, product_image, snack,
    PRIMARY, PRIMARY_LIGHT, BG, TEXT, TEXT_MUTED, DANGER
)

def home_page(page: ft.Page, navigate):
    uid = session.user_id if session.user_id else 0

    products = query("""
        SELECT p.*, c.name as category_name,
        (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price,
        EXISTS(SELECT 1 FROM favorites WHERE user_id = %s AND product_id = p.id) as is_favorite
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        ORDER BY p.id DESC LIMIT 8
    """, (uid,))

    def toggle_fav(product_id, current):
        if not session.is_logged_in():
            snack(page, "يجب تسجيل الدخول أولاً للإضافة للمفضلة", DANGER)
            return
        if current:
            query("DELETE FROM favorites WHERE user_id=%s AND product_id=%s",
                  (session.user_id, product_id), commit=True)
        else:
            query("INSERT INTO favorites (user_id, product_id) VALUES (%s,%s)",
                  (session.user_id, product_id), commit=True)
        navigate("home")

    def product_card(p):
        is_fav = bool(p.get('is_favorite'))
        pid = p['id']
        fav_btn = ft.IconButton(
    icon=ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER,
    icon_color=DANGER if is_fav else TEXT_MUTED,
    icon_size=16,
    padding=0,
    on_click=lambda e, i=pid, f=is_fav: toggle_fav(i, f),
)
        price_text = f"{p['min_price']} ر" if p.get('min_price') else "غير محدد"
        return card(
    ft.Column([
        ft.Row([ft.Container(expand=True), fav_btn]),
        product_image(p.get('image', ''), height=110),
        ft.Container(height=4),
        badge(p.get('category_name', ''), PRIMARY),
        ft.Text(p.get('name', ''), size=12, weight=ft.FontWeight.W_600,
                color=TEXT, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
        ft.Container(height=2),
        ft.Text(f"من: {price_text}", size=11, color=PRIMARY, weight=ft.FontWeight.BOLD),
    ], spacing=2),
    padding=10,
    on_click=lambda e, i=pid: navigate("product", i)
)
    
    # ─── 2-column grid ───
    def build_grid(products):
        rows = []
        for i in range(0, len(products), 2):
            pair = products[i:i+2]
            row_items = [ft.Container(content=product_card(p), expand=True) for p in pair]
            if len(row_items) == 1:
                row_items.append(ft.Container(expand=True))
            rows.append(ft.Row(row_items, spacing=10))
        return ft.Column(rows, spacing=10)

    grid = build_grid(products) if products else ft.Text("لا توجد منتجات حالياً", color=TEXT_MUTED)

    return ft.Column([
        section_title("أحدث المنتجات", ft.Icons.STAR),
        ft.Container(height=10),
        grid,
    ], spacing=0, scroll=ft.ScrollMode.AUTO)