import flet as ft
from db import query
from session import session
from components import (
    card, primary_button, snack, badge,
    PRIMARY, TEXT, TEXT_MUTED, DANGER, SUCCESS, BG
)

def product_page(page: ft.Page, navigate, product_id):
    # جلب بيانات المنتج
    product_info = query("""
        SELECT p.*, c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.id = %s
    """, (product_id,), fetchone=True)

    if not product_info:
        return ft.Column([
            ft.Text("المنتج غير موجود", size=18, color=DANGER),
            ft.ElevatedButton("العودة", on_click=lambda e: navigate("home"))
        ])

    # جلب قائمة المتاجر والأسعار
    stores = query("""
    SELECT ps.*, s.name as store_name, s.logo as store_logo
    FROM product_stores ps
    JOIN stores s ON ps.store_id = s.id
    WHERE ps.product_id = %s
    ORDER BY ps.price ASC
""", (product_id,))

    # التحقق من حالة المفضلة
    is_fav = False
    if session.is_logged_in():
        fav = query("SELECT 1 FROM favorites WHERE user_id=%s AND product_id=%s",
                    (session.user_id, product_id), fetchone=True)
        is_fav = fav is not None

    # دالة إضافة/إزالة المفضلة
    def toggle_fav(e):
        if not session.is_logged_in():
            snack(page, "يجب تسجيل الدخول أولاً", DANGER)
            return
        if is_fav:
            query("DELETE FROM favorites WHERE user_id=%s AND product_id=%s",
                  (session.user_id, product_id), commit=True)
            snack(page, "تمت الإزالة من المفضلة")
        else:
            query("INSERT INTO favorites (user_id, product_id) VALUES (%s,%s)",
                  (session.user_id, product_id), commit=True)
            snack(page, "تمت الإضافة للمفضلة", SUCCESS)
        navigate("product", product_id)

    # دالة بناء صف المتجر
    def store_row(s):
        product_url = s.get('product_url', '')

        # دالة لفتح الرابط
        def open_link(e):
            if product_url and product_url.startswith("http"):
                page.run_javascript(f"window.open('{product_url}', '_blank')")
            else:
                snack(page, "الرابط غير متوفر لهذا المتجر", DANGER)

        price_col = ft.Column([
            ft.Text(f"{s['price']} ريال", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY),
            ft.ElevatedButton(
                "اذهب للمتجر",
                icon=ft.Icons.OPEN_IN_NEW,
                url=product_url if product_url and product_url.startswith("http") else None,
                on_click=None if product_url and product_url.startswith("http") else lambda e: snack(page, "الرابط غير متوفر لهذا المتجر", DANGER),
                style=ft.ButtonStyle(
                    bgcolor=SUCCESS,
                    color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=8),
    )
)
        ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.END)

        store_info = ft.Column([
            ft.Image(src=s.get('store_logo', ''), width=50, height=30, fit="contain",
                     error_content=ft.Icon(ft.Icons.STORE, color=TEXT_MUTED)),
            ft.Text(s.get('store_name', ''), size=14, weight=ft.FontWeight.W_600, color=TEXT),
        ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        return card(
            ft.Row([store_info, ft.Container(expand=True), price_col],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=14
        )

    # قائمة المتاجر
    stores_list = ft.Column(
        [store_row(s) for s in stores] if stores
        else [ft.Text("لا يوجد أسعار متاحة حالياً", color=TEXT_MUTED)],
        spacing=10
    )

    fav_icon = ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER
    fav_color = DANGER if is_fav else TEXT_MUTED

    return ft.Column([
        # زر العودة
        ft.TextButton(
            "← العودة",
            on_click=lambda e: navigate("home"),
            style=ft.ButtonStyle(color=PRIMARY)
        ),
        ft.Container(height=8),

        # بطاقة تفاصيل المنتج
        card(
            ft.Column([
                ft.Image(
                    src=product_info.get('image', ''),
                    width=180,
                    height=180,
                    fit="contain",
                    error_content=ft.Icon(ft.Icons.IMAGE, size=60, color=TEXT_MUTED)
                ),
                ft.Container(height=10),
                ft.Row([
                    ft.Text(
                        product_info.get('name', ''),
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT,
                        expand=True
                    ),
                    ft.IconButton(
                        icon=fav_icon,
                        icon_color=fav_color,
                        icon_size=24,
                        on_click=toggle_fav,
                    )
                ]),
                badge(product_info.get('category_name', ''), PRIMARY),
                ft.Container(height=6),
                ft.Text(
                    product_info.get('description', ''),
                    size=13,
                    color=TEXT_MUTED,
                    max_lines=4,
                    overflow=ft.TextOverflow.ELLIPSIS
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6),
            padding=16
        ),

        ft.Container(height=16),
        ft.Text("مقارنة الأسعار في المتاجر", size=18,
                weight=ft.FontWeight.BOLD, color=TEXT),
        ft.Container(height=8),
        stores_list,
        ft.Container(height=20),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)