import flet as ft

# ألوان التطبيق
PRIMARY = "#1565C0"
PRIMARY_LIGHT = "#E3F2FD"
DANGER = "#D32F2F"
SUCCESS = "#2E7D32"
WARNING = "#F57F17"
BG = "#F5F7FA"
CARD_BG = "#FFFFFF"
TEXT = "#212121"
TEXT_MUTED = "#757575"
BORDER = "#E0E0E0"

def card(content, padding=16, radius=12, shadow=True, color=CARD_BG, on_click=None):
    container = ft.Container(
        content=content,
        bgcolor=color,
        border_radius=radius,
        padding=padding,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ) if shadow else None,
    )

    if on_click:
        return ft.GestureDetector(
            on_tap=lambda e: on_click(e),
            content=container,
        )

    return container

def primary_button(text, on_click=None, icon=None, width=None, bgcolor=PRIMARY):
    return ft.ElevatedButton(
        text,
        icon=icon,
        on_click=on_click,
        width=width,
        style=ft.ButtonStyle(
            bgcolor=bgcolor,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
        ),
    )

def outlined_button(text, on_click=None, icon=None, width=None, color=PRIMARY):
    return ft.OutlinedButton(
        text,
        icon=icon,
        on_click=on_click,
        width=width,
        style=ft.ButtonStyle(
            color=color,
            side=ft.BorderSide(1, color),
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )

def text_field(label, password=False, value="", ref=None, hint="", width=None):
    return ft.TextField(
        label=label,
        password=password,
        can_reveal_password=password,
        value=value,
        ref=ref,
        hint_text=hint,
        width=width,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        border_radius=8,
        text_align=ft.TextAlign.RIGHT,
    )

def badge(text, color=PRIMARY):
    return ft.Container(
        content=ft.Text(text, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor=color,
        border_radius=20,
        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
    )

def section_title(text, icon=None):
    row_items = []
    if icon:
        row_items.append(ft.Icon(icon, color=PRIMARY, size=22))
    row_items.append(ft.Text(text, size=20, weight=ft.FontWeight.BOLD, color=TEXT))
    return ft.Row(row_items, spacing=8)

def snack(page, message, color=SUCCESS):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE, text_align=ft.TextAlign.RIGHT),
        bgcolor=color,
        duration=2500,
    )
    page.snack_bar.open = True
    page.update()

def loading_spinner():
    return ft.Container(
        content=ft.ProgressRing(width=40, height=40, color=PRIMARY),
        alignment=ft.Alignment(0, 0),
        expand=True,
    )

def empty_state(icon, message, action_text=None, on_action=None):
    items = [
        ft.Icon(icon, size=64, color=TEXT_MUTED),
        ft.Text(message, size=16, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER),
    ]
    if action_text:
        items.append(ft.ElevatedButton(action_text, on_click=on_action))
    return ft.Container(
        content=ft.Column(items, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
        alignment=ft.Alignment(0, 0),
        expand=True,
    )

def product_image(url, height=160):
    return ft.Image(
        src=url,
        height=height,
        fit="contain",
        error_content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, color=TEXT_MUTED, size=40),
    )