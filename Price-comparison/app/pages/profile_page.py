import flet as ft
from db import query, get_db
from session import session
from werkzeug.security import generate_password_hash, check_password_hash
from components import (
    card, snack,
    PRIMARY, DANGER, SUCCESS, TEXT, TEXT_MUTED
)

def profile_page(page: ft.Page, navigate):
    if not session.is_logged_in():
        navigate("login")
        return ft.Container()

    user = query("SELECT * FROM users WHERE id = %s", (session.user_id,), fetchone=True)
    fav_count = query("SELECT COUNT(*) as count FROM favorites WHERE user_id = %s",
                      (session.user_id,), fetchone=True)['count']

    # Update profile
    username_ref = ft.Ref[ft.TextField]()
    email_ref = ft.Ref[ft.TextField]()

    def update_profile(e):
        uname = username_ref.current.value.strip()
        email = email_ref.current.value.strip()
        existing = query("SELECT id FROM users WHERE (username=%s OR email=%s) AND id!=%s",
                         (uname, email, session.user_id), fetchone=True)
        if existing:
            snack(page, "اسم المستخدم أو البريد مستخدم بالفعل", DANGER)
            return
        query("UPDATE users SET username=%s, email=%s WHERE id=%s",
              (uname, email, session.user_id), commit=True)
        session.username = uname
        snack(page, "تم تحديث البيانات بنجاح ✓", SUCCESS)
        navigate("profile")

    # Change password
    old_pw_ref = ft.Ref[ft.TextField]()
    new_pw_ref = ft.Ref[ft.TextField]()
    confirm_pw_ref = ft.Ref[ft.TextField]()

    def change_password(e):
        old_pw = old_pw_ref.current.value.strip()
        new_pw = new_pw_ref.current.value.strip()
        confirm_pw = confirm_pw_ref.current.value.strip()

        if new_pw != confirm_pw:
            snack(page, "كلمات المرور الجديدة غير متطابقة", DANGER)
            return
        if not check_password_hash(user['password'], old_pw):
            snack(page, "كلمة المرور القديمة غير صحيحة", DANGER)
            return

        new_hashed = generate_password_hash(new_pw)
        query("UPDATE users SET password=%s WHERE id=%s",
              (new_hashed, session.user_id), commit=True)
        snack(page, "تم تغيير كلمة المرور بنجاح ✓", SUCCESS)

    def pw_field(label, ref):
        return ft.TextField(
            ref=ref, label=label, password=True, can_reveal_password=True,
            border_color="#E0E0E0", focused_border_color=PRIMARY,
            border_radius=10, text_align=ft.TextAlign.RIGHT,
        )

    avatar_letter = (session.username or "U")[0].upper()

    return ft.Column([
        # Avatar + stats
        card(ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Text(avatar_letter, size=28, color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD),
                    width=72, height=72,
                    bgcolor=PRIMARY,
                    border_radius=36,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(width=16),
                ft.Column([
                    ft.Text(session.username, size=20, weight=ft.FontWeight.BOLD, color=TEXT),
                    ft.Text(user.get('email', ''), size=13, color=TEXT_MUTED),
                    ft.Row([
                        ft.Icon(ft.Icons.FAVORITE, size=16, color=DANGER),
                        ft.Text(f"{fav_count} منتج مفضل", size=13, color=TEXT_MUTED),
                    ], spacing=4),
                ], spacing=4),
            ]),
        ]), padding=20),

        ft.Container(height=16),

        # Edit profile
        card(ft.Column([
            ft.Text("تعديل البيانات", size=16, weight=ft.FontWeight.BOLD, color=TEXT),
            ft.Container(height=12),
            ft.TextField(
                ref=username_ref,
                label="اسم المستخدم",
                value=user.get('username', ''),
                border_color="#E0E0E0",
                focused_border_color=PRIMARY,
                border_radius=10,
                text_align=ft.TextAlign.RIGHT,
            ),
            ft.Container(height=10),
            ft.TextField(
                ref=email_ref,
                label="البريد الإلكتروني",
                value=user.get('email', ''),
                border_color="#E0E0E0",
                focused_border_color=PRIMARY,
                border_radius=10,
                text_align=ft.TextAlign.RIGHT,
            ),
            ft.Container(height=14),
            ft.ElevatedButton(
                "حفظ التغييرات",
                icon=ft.Icons.SAVE,
                on_click=update_profile,
                width=float('inf'),
                style=ft.ButtonStyle(
                    bgcolor=SUCCESS,
                    color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=10),
                )
            )
        ], spacing=0), padding=20),

        ft.Container(height=16),

        # Change password
        card(ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.KEY, color=PRIMARY, size=20),
                ft.Text("تغيير كلمة المرور", size=16, weight=ft.FontWeight.BOLD, color=TEXT),
            ], spacing=8),
            ft.Container(height=12),
            pw_field("كلمة المرور الحالية", old_pw_ref),
            ft.Container(height=10),
            pw_field("كلمة المرور الجديدة", new_pw_ref),
            ft.Container(height=10),
            pw_field("تأكيد كلمة المرور الجديدة", confirm_pw_ref),
            ft.Container(height=14),
            ft.ElevatedButton(
                "تحديث كلمة المرور",
                icon=ft.Icons.LOCK_RESET,
                on_click=change_password,
                width=float('inf'),
                style=ft.ButtonStyle(
                    bgcolor=PRIMARY,
                    color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=10),
                )
            )
        ], spacing=0), padding=20),

        ft.Container(height=20),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)