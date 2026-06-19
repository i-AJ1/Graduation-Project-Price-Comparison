import flet as ft
from db import query
from session import session
from werkzeug.security import check_password_hash
from components import (
    card, primary_button, text_field, snack,
    PRIMARY, DANGER, SUCCESS, TEXT, TEXT_MUTED
)

def login_page(page: ft.Page, navigate):
    username_ref = ft.Ref[ft.TextField]()
    password_ref = ft.Ref[ft.TextField]()

    def do_login(e):
        username = username_ref.current.value.strip()
        password = password_ref.current.value.strip()

        if not username or not password:
            snack(page, "يرجى ملء جميع الحقول", DANGER)
            return

        user = query("SELECT * FROM users WHERE username = %s", (username,), fetchone=True)
        if user and check_password_hash(user['password'], password):
            session.login(user)
            snack(page, "تم تسجيل الدخول بنجاح ✓", SUCCESS)
            navigate("home")
        else:
            snack(page, "خطأ في اسم المستخدم أو كلمة المرور", DANGER)

    return ft.Column([
        ft.Container(height=40),
        ft.Container(
            content=card(
                ft.Column([
                    ft.Column([
                        ft.Icon(ft.Icons.PERSON_ROUNDED, size=56, color=PRIMARY),
                        ft.Text("تسجيل الدخول", size=24, weight=ft.FontWeight.BOLD, color=TEXT),
                        ft.Text("مرحباً بك مجدداً", size=14, color=TEXT_MUTED),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                    ft.Container(height=20),
                    ft.TextField(
                        ref=username_ref,
                        label="اسم المستخدم",
                        prefix_icon=ft.Icons.PERSON_OUTLINE,
                        border_color="#E0E0E0",
                        focused_border_color=PRIMARY,
                        border_radius=10,
                        text_align=ft.TextAlign.RIGHT,
                    ),
                    ft.Container(height=12),
                    ft.TextField(
                        ref=password_ref,
                        label="كلمة المرور",
                        password=True,
                        can_reveal_password=True,
                        prefix_icon=ft.Icons.LOCK_OUTLINE,
                        border_color="#E0E0E0",
                        focused_border_color=PRIMARY,
                        border_radius=10,
                        text_align=ft.TextAlign.RIGHT,
                        on_submit=do_login,
                    ),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "دخول",
                        icon=ft.Icons.LOGIN,
                        on_click=do_login,
                        width=float('inf'),
                        height=48,
                        style=ft.ButtonStyle(
                            bgcolor=PRIMARY,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=10),
                        )
                    ),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Text("ليس لديك حساب؟", size=13, color=TEXT_MUTED),
                        ft.TextButton("سجل الآن", on_click=lambda e: navigate("register"),
                                      style=ft.ButtonStyle(color=PRIMARY)),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.TextButton("← العودة للرئيسية",
                                  on_click=lambda e: navigate("home"),
                                  style=ft.ButtonStyle(color=TEXT_MUTED)),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=32
            ),
            width=400,
            alignment=ft.Alignment(0, 0),
        )
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)