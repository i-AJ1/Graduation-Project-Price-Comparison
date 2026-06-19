import flet as ft
from db import query
from session import session
from components import (
    card, outlined_button, badge, section_title,
    product_image, snack, empty_state,
    PRIMARY, PRIMARY_LIGHT, TEXT, TEXT_MUTED, DANGER, BG
)

def categories_page(page: ft.Page, navigate, selected_cat_id=None):
    categories = query("SELECT * FROM categories")

    user_id = session.user_id
    if selected_cat_id:
        products = query("""
            SELECT p.*, c.name as category_name,
            (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price,
            EXISTS(SELECT 1 FROM favorites WHERE user_id = %s AND product_id = p.id) as is_favorite
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = %s
        """, (user_id, selected_cat_id))
    else:
        products = query("""
            SELECT p.*, c.name as category_name,
            (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price,
            EXISTS(SELECT 1 FROM favorites WHERE user_id = %s AND product_id = p.id) as is_favorite
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
        """, (user_id,))

    def toggle_fav(product_id, current):
        if not session.is_logged_in():
            snack(page, "يجب تسجيل الدخول أولاً", DANGER)
            return
        if current:
            query("DELETE FROM favorites WHERE user_id=%s AND product_id=%s",
                  (session.user_id, product_id), commit=True)
        else:
            query("INSERT INTO favorites (user_id, product_id) VALUES (%s,%s)",
                  (session.user_id, product_id), commit=True)
        navigate("categories", selected_cat_id)

    # ─── Category chips using ft.Chip instead of ActionChip ───
    cat_chips = [
        ft.Chip(
            label=ft.Text("الكل", size=12),
            on_click=lambda e: navigate("categories"),
            bgcolor=PRIMARY if not selected_cat_id else None,
            selected=not bool(selected_cat_id),
            selected_color=PRIMARY,
            show_checkmark=False,
        )
    ]
    for cat in categories:
        active = selected_cat_id == cat['id']
        cat_chips.append(
            ft.Chip(
                label=ft.Text(cat['name'], size=12),
                on_click=lambda e, cid=cat['id']: navigate("categories", cid),
                bgcolor=PRIMARY if active else None,
                selected=active,
                selected_color=PRIMARY,
                show_checkmark=False,
            )
        )

    def product_card(p):
        is_fav = bool(p.get('is_favorite'))
        pid = p['id']
        price_text = f"{p['min_price']} ر" if p.get('min_price') else "غير محدد"
        return card(
            ft.Column([
                ft.Row([
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER,
                        icon_color=DANGER if is_fav else TEXT_MUTED,
                        icon_size=16,
                        padding=0,
                    )
                ], spacing=0),
                product_image(p.get('image', ''), height=100),
                ft.Container(height=4),
                badge(p.get('category_name', ''), PRIMARY),
                ft.Container(height=2),
                ft.Text(p.get('name', ''), size=12, weight=ft.FontWeight.W_600,
                        color=TEXT, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(f"أقل: {price_text}", size=11, color=PRIMARY, weight=ft.FontWeight.BOLD),
                ft.Container(height=4),
                ft.Row([
                    ft.Container(expand=True),
                    
                ])
            ], spacing=2),
            padding=8,
            on_click=lambda e, i=pid: navigate("product", i)
        )

    # ─── 2-column grid for mobile ───
    def build_grid(products):
        rows = []
        for i in range(0, len(products), 2):
            pair = products[i:i+2]
            row_items = [ft.Container(content=product_card(p), expand=True) for p in pair]
            # fill empty slot if odd
            if len(row_items) == 1:
                row_items.append(ft.Container(expand=True))
            rows.append(ft.Row(row_items, spacing=10))
        return ft.Column(rows, spacing=10)

    products_grid = build_grid(products) if products else empty_state(
        ft.Icons.INVENTORY_2_OUTLINED,
        "لا توجد منتجات في هذا القسم",
        "عرض كل الأقسام",
        lambda e: navigate("categories"),
    )

    return ft.Column([
        ft.Text("تصفح حسب القسم", size=20, weight=ft.FontWeight.BOLD, color=TEXT),
        ft.Text("اختر الفئة للوصول لأفضل العروض", size=13, color=TEXT_MUTED),
        ft.Container(height=8),
        ft.Row(cat_chips, wrap=True, spacing=6, run_spacing=6),
        ft.Container(height=12),
        ft.Row([
            section_title("المنتجات", ft.Icons.GRID_VIEW),
            ft.Container(expand=True),
            ft.Container(
                content=ft.Text(f"{len(products)} منتج", size=11, color=TEXT_MUTED),
                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                bgcolor=PRIMARY_LIGHT,
                border_radius=20,
            )
        ]),
        ft.Container(height=10),
        products_grid,
    ], scroll=ft.ScrollMode.AUTO, spacing=4)