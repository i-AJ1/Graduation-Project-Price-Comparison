import flet as ft
from db import query
from werkzeug.security import generate_password_hash
from components import (
    card, snack,
    PRIMARY, DANGER, SUCCESS, TEXT, TEXT_MUTED
)

def register_page(page: ft.Page, navigate):

    username_ref = ft.Ref[ft.TextField]()
    email_ref = ft.Ref[ft.TextField]()
    password_ref = ft.Ref[ft.TextField]()

    def do_register(e):
        print("🔥 زر التسجيل اشتغل")  # تأكيد الزر

        username = username_ref.current.value if username_ref.current else ""
        email = email_ref.current.value if email_ref.current else ""
        password = password_ref.current.value if password_ref.current else ""

        print("DATA:", username, email, password)

        if not username or not email or not password:
            snack(page, "يرجى ملء جميع الحقول", DANGER)
            return

        if len(password) < 6:
            snack(page, "كلمة المرور يجب أن تكون 6 أحرف على الأقل", DANGER)
            return

        try:
            hashed = generate_password_hash(password)

            result = query(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed),
                commit=True
            )

            print("INSERT OK ID:", result)

            snack(page, "تم إنشاء الحساب بنجاح! سجل دخولك الآن", SUCCESS)
            navigate("login")

        except Exception as ex:
            print("❌ Register Error:", ex)
            snack(page, "خطأ: اسم المستخدم أو البريد مستخدم", DANGER)

    def field(label, icon, password=False, ref=None):
        return ft.TextField(
            ref=ref,
            label=label,
            password=password,
            can_reveal_password=password,
            prefix_icon=icon,
            border_color="#E0E0E0",
            focused_border_color=PRIMARY,
            border_radius=10,
            text_align=ft.TextAlign.RIGHT,
        )

    return ft.Column(
        controls=[
            ft.Container(height=40),

            ft.Container(
                content=card(
                    ft.Column(
                        controls=[

                            ft.Icon(ft.Icons.PERSON_ADD_ROUNDED, size=56, color=PRIMARY),
                            ft.Text("إنشاء حساب", size=24, weight=ft.FontWeight.BOLD, color=TEXT),
                            ft.Text("انضم للحصول على أفضل العروض", size=13, color=TEXT_MUTED),

                            ft.Container(height=20),

                            field("اسم المستخدم", ft.Icons.PERSON_OUTLINE, ref=username_ref),
                            ft.Container(height=12),

                            field("البريد الإلكتروني", ft.Icons.EMAIL_OUTLINED, ref=email_ref),
                            ft.Container(height=12),

                            field("كلمة المرور", ft.Icons.LOCK_OUTLINE, password=True, ref=password_ref),

                            ft.Container(height=20),

                            # 🔥 زر مضبوط 100%
                            ft.ElevatedButton(
                                "إنشاء الحساب",
                                icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                                on_click=do_register,
                                width=300,
                                height=48,
                                style=ft.ButtonStyle(
                                    bgcolor=PRIMARY,
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                )
                            ),

                            ft.Container(height=12),

                            ft.Row(
                                controls=[
                                    ft.Text("لديك حساب؟", size=13, color=TEXT_MUTED),
                                    ft.TextButton(
                                        "سجل دخولك",
                                        on_click=lambda e: navigate("login"),
                                        style=ft.ButtonStyle(color=PRIMARY)
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER
                            ),

                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=32
                ),
                width=400
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO
    )