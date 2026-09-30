import asyncio
import io
import json
from datetime import date

import flet as ft
from src.installer import setup_environment


def parse_range(range_str: str, total_pages: int) -> list[int]:
    """Parse 1-based page ranges such as '1-3, 5' into zero-based indices."""
    pages: set[int] = set()
    for raw_part in range_str.replace(" ", "").split(","):
        if not raw_part:
            continue
        if "-" in raw_part:
            bounds = raw_part.split("-", 1)
            if len(bounds) != 2 or not bounds[0].isdigit() or not bounds[1].isdigit():
                raise ValueError(f"頁碼範圍格式錯誤：{raw_part}")
            start, end = int(bounds[0]), int(bounds[1])
            if start > end:
                raise ValueError(f"頁碼範圍起始頁不可大於結束頁：{raw_part}")
            pages.update(p - 1 for p in range(start, end + 1) if 1 <= p <= total_pages)
        elif raw_part.isdigit():
            page_number = int(raw_part)
            if 1 <= page_number <= total_pages:
                pages.add(page_number - 1)
        else:
            raise ValueError(f"頁碼格式錯誤：{raw_part}")
    if not pages:
        raise ValueError("輸入範圍沒有包含任何有效頁碼")
    return sorted(pages)


async def main(page: ft.Page):
    await setup_environment()
    from src.pdf_engine import PDFEngine

    page.title = "Smart PDF Toolkit"
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.theme_mode = ft.ThemeMode.LIGHT

    # In web/Pyodide, the selected file has no usable local path. Keep its bytes.
    selected_files: list[dict] = []
    current_status = ft.Text("尚未選擇檔案", color=ft.Colors.GREY_600)
    uploaded_files_display = ft.Text("尚無已選取檔案")
    file_picker = ft.FilePicker()
    preferences = ft.SharedPreferences()
    usage_key = "daily_pdf_usage"
    daily_count = 0
    usage_status = ft.Text("今日剩餘次數：5/5")
    operation_buttons = []
    ui_mounted = False
    status_kind = "neutral"
    language = "zh-TW"
    translations = {
        "語言": "Language",
        "繁體中文": "Traditional Chinese",
        "尚未選擇檔案": "No file selected",
        "尚無已選取檔案": "No files selected",
        "今日剩餘次數：": "Remaining today: ",
        "請先選取 PDF 檔案": "Please select a PDF file first",
        "今日操作次數已用完": "Daily operation limit reached",
        "每日最多可執行 5 次 PDF 處理操作。": "You can process PDFs up to 5 times per day.",
        "確定": "OK",
        "已選取檔案：": "Selected files:\n",
        "下載處理後的 PDF": "Download processed PDF",
        "處理完成，已開始下載：": "Done. Download started: ",
        "選取 PDF 檔案": "Select PDF files",
        "已取消選擇檔案": "File selection cancelled",
        "瀏覽器未提供 ": "The browser did not provide file data for ",
        " 的檔案內容，請重新選取": ". Please select it again.",
        " 頁": " pages",
        "頁數未知（可能已加密或檔案損毀）": "Page count unknown (encrypted or damaged file)",
        "已成功載入 ": "Successfully loaded ",
        " 個 PDF 檔案": " PDF file(s)",
        "載入失敗：": "Load failed: ",
        "已清空所有已選取檔案": "Cleared all selected files",
        "拆分頁碼 (例: 1-3, 5)": "Pages to split (e.g. 1-3, 5)",
        "留空則全選": "Leave blank to select all",
        "輸出檔名": "Output filename",
        "拆分失敗：": "Split failed: ",
        "合併功能請至少選擇 2 個 PDF 檔案": "Select at least 2 PDF files to merge",
        "合併失敗：": "Merge failed: ",
        "合併已選取檔案": "Merge selected files",
        "執行頁面拆分": "Split pages",
        "多檔合併": "Merge PDFs",
        "檔案拆分/提取": "Split / extract pages",
        "旋轉角度": "Rotation angle",
        "順時針 90°": "Clockwise 90°",
        "逆時針 90° (270°)": "Counterclockwise 90° (270°)",
        "左 (pt)": "Left (pt)",
        "下 (pt)": "Bottom (pt)",
        "右 (pt)": "Right (pt)",
        "上 (pt)": "Top (pt)",
        "旋轉失敗：": "Rotation failed: ",
        "裁切失敗：": "Crop failed: ",
        "套用旋轉": "Apply rotation",
        "套用邊距裁切": "Apply margin crop",
        "頁面旋轉": "Rotate pages",
        "頁面邊距裁切 (MediaBox/CropBox)": "Page margin crop (MediaBox/CropBox)",
        "提取內容預覽": "Extracted text preview",
        "文字提取完成": "Text extraction complete",
        "文字提取失敗：": "Text extraction failed: ",
        "提取 PDF 全文內容": "Extract all PDF text",
        "設定加密密碼": "Set encryption password",
        "輸入解密密碼": "Enter decryption password",
        "請輸入加密密碼": "Enter an encryption password",
        "加密失敗：": "Encryption failed: ",
        "密碼錯誤，解密失敗": "Incorrect password; decryption failed",
        "解密失敗：": "Decryption failed: ",
        "執行加密": "Encrypt PDF",
        "執行解密": "Decrypt PDF",
        "檔案加密": "PDF encryption",
        "檔案解密": "PDF decryption",
        "文件標題 (/Title)": "Document title (/Title)",
        "作者 (/Author)": "Author (/Author)",
        "浮水印文字": "Watermark text",
        "Metadata 修改失敗：": "Metadata update failed: ",
        "浮水印處理失敗：": "Watermark failed: ",
        "寫入 Metadata": "Write metadata",
        "添加浮水印": "Add watermark",
        "修改詮釋資料 (Metadata)": "Edit metadata",
        "動態浮水印": "Watermark",
        "選取 PDF 檔案 (可多選)": "Choose PDF files (multiple)",
        "清空已選檔案": "Clear selected files",
        "拆分/合併": "Split / merge",
        "旋轉/裁切": "Rotate / crop",
        "內容提取": "Extract text",
        "加密/解密": "Encrypt / decrypt",
        "元數據/水印": "Metadata / watermark",
        "深色模式": "Dark mode",
        "字體大小": "Font size",
        "中": "Medium",
        "大": "Large",
        "小": "Small",
        "頁碼範圍格式錯誤：": "Invalid page range: ",
        "頁碼範圍起始頁不可大於結束頁：": "Page range start cannot exceed end: ",
        "頁碼格式錯誤：": "Invalid page number: ",
        "輸入範圍沒有包含任何有效頁碼": "The range contains no valid pages",
    }

    def localize_text(value):
        if not isinstance(value, str):
            return value
        pairs = list(translations.items()) if language == "en" else [(target, source) for source, target in translations.items()]
        for source, target in pairs:
            if value == source:
                return target
        for source, target in sorted(pairs, key=lambda pair: len(pair[0]), reverse=True):
            if len(source) > 1:
                value = value.replace(source, target)
        return value

    def update_ui_state():
        remaining = max(0, 5 - daily_count)
        usage_status.value = f"{localize_text('今日剩餘次數：')}{remaining}/5"
        for button in operation_buttons:
            button.disabled = remaining == 0
        if ui_mounted:
            page.update()

    def show_alert(message: str, is_error: bool = False):
        nonlocal status_kind
        current_status.value = localize_text(message)
        status_kind = "error" if is_error else "success"
        dark = page.theme_mode == ft.ThemeMode.DARK
        if status_kind == "error":
            current_status.color = ft.Colors.RED_300 if dark else ft.Colors.RED_700
        else:
            current_status.color = ft.Colors.GREEN_300 if dark else ft.Colors.GREEN_700
        page.update()

    def selected_stream(index: int = 0) -> io.BytesIO:
        if not selected_files:
            raise ValueError("請先選取 PDF 檔案")
        return io.BytesIO(selected_files[index]["data"])

    async def refresh_daily_usage() -> int:
        nonlocal daily_count
        today = date.today().isoformat()
        stored = await preferences.get(usage_key)
        try:
            record = json.loads(stored) if isinstance(stored, str) else {}
            if record.get("date") == today:
                daily_count = int(record.get("count", 0))
            else:
                daily_count = 0
                await preferences.set(usage_key, json.dumps({"date": today, "count": 0}))
        except (TypeError, ValueError, json.JSONDecodeError):
            daily_count = 0
            await preferences.set(usage_key, json.dumps({"date": today, "count": 0}))
        daily_count = max(0, min(daily_count, 5))
        update_ui_state()
        return 5 - daily_count

    async def check_daily_limit() -> bool:
        remaining = await refresh_daily_usage()
        if remaining > 0:
            return True
        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text(localize_text("今日操作次數已用完")),
                content=ft.Text(localize_text("每日最多可執行 5 次 PDF 處理操作。")),
                actions=[
                    ft.TextButton(
                        content=localize_text("確定"),
                        on_click=lambda _: page.pop_dialog(),
                    )
                ],
            )
        )
        return False

    async def record_successful_operation():
        nonlocal daily_count
        await refresh_daily_usage()
        daily_count = min(daily_count + 1, 5)
        today = date.today().isoformat()
        await preferences.set(
            usage_key,
            json.dumps({"date": today, "count": daily_count}),
        )
        update_ui_state()

    async def watch_day_change():
        observed_day = date.today()
        while True:
            await asyncio.sleep(60)
            current_day = date.today()
            if current_day != observed_day:
                observed_day = current_day
                await refresh_daily_usage()

    await refresh_daily_usage()

    def refresh_uploaded_files():
        if selected_files:
            title = "Selected files:\n" if language == "en" else "已選取檔案：\n"
            file_rows = []
            for item in selected_files:
                if item["pages"] is None:
                    page_label = localize_text(item["page_label"])
                elif language == "en":
                    page_label = f"{item['pages']} pages"
                else:
                    page_label = f"{item['pages']} 頁"
                file_rows.append(f"• {item['name']} — {page_label}")
            uploaded_files_display.value = title + "\n".join(file_rows)
        else:
            uploaded_files_display.value = localize_text("尚無已選取檔案")

    def pdf_filename(value: str, fallback: str) -> str:
        name = (value or "").replace("\\", "/").split("/")[-1].strip()
        if not name:
            name = fallback
        if not name.lower().endswith(".pdf"):
            name += ".pdf"
        return name

    async def download_pdf(output: io.BytesIO, filename: str):
        await file_picker.save_file(
            dialog_title=localize_text("下載處理後的 PDF"),
            file_name=filename,
            src_bytes=output.getvalue(),
        )
        show_alert(f"處理完成，已開始下載：{filename}")

    async def trigger_picker(e):
        nonlocal selected_files
        try:
            picked = await file_picker.pick_files(
                dialog_title=localize_text("選取 PDF 檔案"),
                allow_multiple=True,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["pdf"],
                with_data=True,
            )
            if not picked:
                show_alert("已取消選擇檔案", True)
                return

            loaded = []
            for file in picked:
                data = file.bytes
                if data is None:
                    raise ValueError(f"瀏覽器未提供 {file.name} 的檔案內容，請重新選取")
                try:
                    page_count = PDFEngine.page_count(io.BytesIO(data))
                    page_label = f"{page_count} 頁"
                except Exception:
                    page_count = None
                    page_label = "頁數未知（可能已加密或檔案損毀）"
                loaded.append({"name": file.name, "data": data, "pages": page_count, "page_label": page_label})

            selected_files = loaded
            refresh_uploaded_files()
            show_alert(f"已成功載入 {len(loaded)} 個 PDF 檔案")
        except Exception as err:
            show_alert(f"載入失敗：{err}", True)

    def clear_selected_files(e):
        nonlocal selected_files
        selected_files = []
        refresh_uploaded_files()
        show_alert("已清空所有已選取檔案")

    # 1. 合併與拆分
    split_range_input = ft.TextField(label="拆分頁碼 (例: 1-3, 5)", hint_text="留空則全選", width=250)
    split_output_name = ft.TextField(label="輸出檔名", value="split_output.pdf", width=250)

    async def do_split(e):
        try:
            if not await check_daily_limit():
                return
            source = selected_stream()
            total = PDFEngine.page_count(source)
            indices = parse_range(split_range_input.value, total) if split_range_input.value else list(range(total))
            output = io.BytesIO()
            PDFEngine.split_pdf(selected_stream(), indices, output)
            await record_successful_operation()
            await download_pdf(output, pdf_filename(split_output_name.value, "split_output.pdf"))
        except Exception as err:
            show_alert(f"拆分失敗：{err}", True)

    async def do_merge(e):
        try:
            if not await check_daily_limit():
                return
            if len(selected_files) < 2:
                raise ValueError("合併功能請至少選擇 2 個 PDF 檔案")
            output = io.BytesIO()
            PDFEngine.merge_pdfs([io.BytesIO(item["data"]) for item in selected_files], output)
            await record_successful_operation()
            await download_pdf(output, "merged_output.pdf")
        except Exception as err:
            show_alert(f"合併失敗：{err}", True)

    merge_button = ft.Button(content="合併已選取檔案", icon=ft.Icons.CALL_MERGE, on_click=do_merge)
    split_button = ft.Button(content="執行頁面拆分", icon=ft.Icons.CALL_SPLIT, on_click=do_split)
    tab_merge_split = ft.Container(
        content=ft.Column([
            ft.Text("多檔合併", weight=ft.FontWeight.BOLD, size=16),
            merge_button,
            ft.Divider(),
            ft.Text("檔案拆分/提取", weight=ft.FontWeight.BOLD, size=16),
            ft.Row([split_range_input, split_output_name]),
            split_button,
        ], spacing=15),
        padding=15,
        visible=True,
    )

    # 2. 旋轉與裁剪
    rotate_angle = ft.Dropdown(
        label="旋轉角度",
        options=[
            ft.DropdownOption(key="90", text="順時針 90°"),
            ft.DropdownOption(key="180", text="180°"),
            ft.DropdownOption(key="270", text="逆時針 90° (270°)"),
        ],
        value="90",
        width=180,
    )
    crop_l = ft.TextField(label="左 (pt)", value="20", width=80)
    crop_b = ft.TextField(label="下 (pt)", value="20", width=80)
    crop_r = ft.TextField(label="右 (pt)", value="20", width=80)
    crop_t = ft.TextField(label="上 (pt)", value="20", width=80)

    async def do_rotate(e):
        try:
            if not await check_daily_limit():
                return
            selected_stream()
            angle = int(rotate_angle.value)
            output = io.BytesIO()
            PDFEngine.rotate_pages(selected_stream(), output, angle=angle)
            await record_successful_operation()
            await download_pdf(output, "rotated_output.pdf")
        except Exception as err:
            show_alert(f"旋轉失敗：{err}", True)

    async def do_crop(e):
        try:
            if not await check_daily_limit():
                return
            selected_stream()
            margins = {
                "left": float(crop_l.value),
                "bottom": float(crop_b.value),
                "right": float(crop_r.value),
                "top": float(crop_t.value),
            }
            output = io.BytesIO()
            PDFEngine.crop_pages(selected_stream(), output, **margins)
            await record_successful_operation()
            await download_pdf(output, "cropped_output.pdf")
        except Exception as err:
            show_alert(f"裁切失敗：{err}", True)

    rotate_button = ft.Button(content="套用旋轉", icon=ft.Icons.ROTATE_RIGHT, on_click=do_rotate)
    crop_button = ft.Button(content="套用邊距裁切", icon=ft.Icons.CROP, on_click=do_crop)
    tab_rotate_crop = ft.Container(
        content=ft.Column([
            ft.Text("頁面旋轉", weight=ft.FontWeight.BOLD, size=16),
            ft.Row([rotate_angle, rotate_button]),
            ft.Divider(),
            ft.Text("頁面邊距裁切 (MediaBox/CropBox)", weight=ft.FontWeight.BOLD, size=16),
            ft.Row([crop_l, crop_b, crop_r, crop_t]),
            crop_button,
        ], spacing=15),
        padding=15,
        visible=False,
    )

    # 3. 內容提取
    text_preview = ft.TextField(label="提取內容預覽", multiline=True, min_lines=8, max_lines=12, read_only=True)

    async def do_extract(e):
        try:
            if not await check_daily_limit():
                return
            selected_stream()
            text_preview.value = PDFEngine.extract_text(selected_stream())
            await record_successful_operation()
            page.update()
            show_alert("文字提取完成")
        except Exception as err:
            show_alert(f"文字提取失敗：{err}", True)

    extract_button = ft.Button(content="提取 PDF 全文內容", icon=ft.Icons.TEXT_SNIPPET, on_click=do_extract)
    tab_extract = ft.Container(
        content=ft.Column([
            extract_button,
            text_preview,
        ], spacing=15),
        padding=15,
        visible=False,
    )

    # 4. 加密與解密
    enc_pass = ft.TextField(label="設定加密密碼", password=True, can_reveal_password=True, width=250)
    dec_pass = ft.TextField(label="輸入解密密碼", password=True, can_reveal_password=True, width=250)

    async def do_encrypt(e):
        try:
            if not await check_daily_limit():
                return
            selected_stream()
            if not enc_pass.value:
                raise ValueError("請輸入加密密碼")
            output = io.BytesIO()
            PDFEngine.encrypt_pdf(selected_stream(), output, enc_pass.value)
            await record_successful_operation()
            await download_pdf(output, "encrypted_output.pdf")
        except Exception as err:
            show_alert(f"加密失敗：{err}", True)

    async def do_decrypt(e):
        try:
            if not await check_daily_limit():
                return
            selected_stream()
            output = io.BytesIO()
            success = PDFEngine.decrypt_pdf(selected_stream(), output, dec_pass.value or "")
            if not success:
                raise ValueError("密碼錯誤，解密失敗")
            await record_successful_operation()
            await download_pdf(output, "decrypted_output.pdf")
        except Exception as err:
            show_alert(f"解密失敗：{err}", True)

    encrypt_button = ft.Button(content="執行加密", icon=ft.Icons.LOCK, on_click=do_encrypt)
    decrypt_button = ft.Button(content="執行解密", icon=ft.Icons.LOCK_OPEN, on_click=do_decrypt)
    tab_security = ft.Container(
        content=ft.Column([
            ft.Text("檔案加密", weight=ft.FontWeight.BOLD, size=16),
            ft.Row([enc_pass, encrypt_button]),
            ft.Divider(),
            ft.Text("檔案解密", weight=ft.FontWeight.BOLD, size=16),
            ft.Row([dec_pass, decrypt_button]),
        ], spacing=15),
        padding=15,
        visible=False,
    )

    # 5. Metadata 與浮水印
    meta_title = ft.TextField(label="文件標題 (/Title)", width=240)
    meta_author = ft.TextField(label="作者 (/Author)", width=240)
    wm_text = ft.TextField(label="浮水印文字", value="CONFIDENTIAL", width=240)

    async def do_metadata(e):
        try:
            if not await check_daily_limit():
                return
            selected_stream()
            output = io.BytesIO()
            PDFEngine.update_metadata(
                selected_stream(), output,
                {"/Title": meta_title.value, "/Author": meta_author.value},
            )
            await record_successful_operation()
            await download_pdf(output, "metadata_output.pdf")
        except Exception as err:
            show_alert(f"Metadata 修改失敗：{err}", True)

    async def do_watermark(e):
        try:
            if not await check_daily_limit():
                return
            selected_stream()
            output = io.BytesIO()
            PDFEngine.add_watermark(selected_stream(), output, watermark_text=wm_text.value or "CONFIDENTIAL")
            await record_successful_operation()
            await download_pdf(output, "watermarked_output.pdf")
        except Exception as err:
            show_alert(f"浮水印處理失敗：{err}", True)

    metadata_button = ft.Button(content="寫入 Metadata", icon=ft.Icons.DATA_OBJECT, on_click=do_metadata)
    watermark_button = ft.Button(content="添加浮水印", icon=ft.Icons.BRANDING_WATERMARK, on_click=do_watermark)
    tab_meta_wm = ft.Container(
        content=ft.Column([
            ft.Text("修改詮釋資料 (Metadata)", weight=ft.FontWeight.BOLD, size=16),
            ft.Row([meta_title, meta_author]),
            metadata_button,
            ft.Divider(),
            ft.Text("動態浮水印", weight=ft.FontWeight.BOLD, size=16),
            ft.Row([wm_text, watermark_button]),
        ], spacing=15),
        padding=15,
        visible=False,
    )

    operation_buttons.extend([
        merge_button,
        split_button,
        rotate_button,
        crop_button,
        extract_button,
        encrypt_button,
        decrypt_button,
        metadata_button,
        watermark_button,
    ])
    update_ui_state()

    # Top file chooser, five navigation buttons, and operation panels.
    file_banner = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Button(
                            content="選取 PDF 檔案 (可多選)",
                            icon=ft.Icons.FILE_OPEN,
                            on_click=trigger_picker,
                        ),
                        ft.Button(
                            content="清空已選檔案",
                            icon=ft.Icons.DELETE,
                            on_click=clear_selected_files,
                        ),
                    ],
                    wrap=True,
                    spacing=10,
                ),
                uploaded_files_display,
                ft.Row([current_status, usage_status], wrap=True, spacing=12),
            ],
            spacing=8,
        ),
        padding=12,
        bgcolor=ft.Colors.GREY_100,
        border_radius=8,
    )

    views = [tab_merge_split, tab_rotate_crop, tab_extract, tab_security, tab_meta_wm]

    def switch_tab(idx: int):
        for i, view in enumerate(views):
            view.visible = i == idx
        page.update()

    nav_row = ft.Row([
        ft.Button(content="拆分/合併", icon=ft.Icons.CALL_SPLIT, on_click=lambda _: switch_tab(0)),
        ft.Button(content="旋轉/裁切", icon=ft.Icons.CROP_ROTATE, on_click=lambda _: switch_tab(1)),
        ft.Button(content="內容提取", icon=ft.Icons.TEXT_SNIPPET, on_click=lambda _: switch_tab(2)),
        ft.Button(content="加密/解密", icon=ft.Icons.SECURITY, on_click=lambda _: switch_tab(3)),
        ft.Button(content="元數據/水印", icon=ft.Icons.MORE_HORIZ, on_click=lambda _: switch_tab(4)),
    ], wrap=True, spacing=10)

    def on_theme_change(e):
        dark = bool(e.control.value)
        page.theme_mode = ft.ThemeMode.DARK if dark else ft.ThemeMode.LIGHT
        file_banner.bgcolor = ft.Colors.GREY_900 if dark else ft.Colors.GREY_100
        if status_kind == "error":
            current_status.color = ft.Colors.RED_300 if dark else ft.Colors.RED_700
        elif status_kind == "success":
            current_status.color = ft.Colors.GREEN_300 if dark else ft.Colors.GREEN_700
        else:
            current_status.color = ft.Colors.GREY_300 if dark else ft.Colors.GREY_600
        page.update()

    font_scale_by_name = {"small": 0.85, "medium": 1.0, "large": 1.2}
    font_base_sizes = {}

    def walk_controls(controls):
        stack = list(controls)
        seen = set()
        while stack:
            control = stack.pop()
            if control is None or id(control) in seen:
                continue
            seen.add(id(control))
            yield control
            nested = getattr(control, "controls", None)
            if isinstance(nested, (list, tuple)):
                stack.extend(nested)
            child = getattr(control, "content", None)
            if child is not None and not isinstance(child, (str, int, float)):
                stack.append(child)

    def apply_language():
        for control in walk_controls(page.controls):
            if isinstance(control, ft.Text):
                control.value = localize_text(control.value)
            elif isinstance(control, ft.TextField):
                control.label = localize_text(control.label)
                control.hint_text = localize_text(control.hint_text)
                control.helper = localize_text(control.helper)
                control.error = localize_text(control.error)
            elif isinstance(control, ft.Button):
                control.content = localize_text(control.content)
            elif isinstance(control, ft.Switch):
                control.label = localize_text(control.label)
            elif isinstance(control, ft.Dropdown):
                control.label = localize_text(control.label)
                for option in control.options or []:
                    option.text = localize_text(option.text)

    def on_language_change(e):
        nonlocal language
        language = e.control.value
        apply_language()
        refresh_uploaded_files()
        update_ui_state()

    def on_font_size_change(e=None):
        selected_size = e.control.value if e is not None else font_size_dropdown.value
        factor = font_scale_by_name.get(selected_size, 1.0)
        for control in walk_controls(page.controls):
            control_id = id(control)
            if isinstance(control, ft.Text):
                key = (control_id, "text")
                base = font_base_sizes.setdefault(key, control.size or 14)
                control.size = base * factor
            elif isinstance(control, ft.TextField):
                key = (control_id, "field_text")
                base = font_base_sizes.setdefault(key, control.text_size or 14)
                control.text_size = base * factor
                key = (control_id, "field_label")
                label_size = getattr(control.label_style, "size", None) if control.label_style else None
                base_label = font_base_sizes.setdefault(key, label_size or 14)
                control.label_style = ft.TextStyle(size=base_label * factor)
            elif isinstance(control, ft.Dropdown):
                key = (control_id, "dropdown_text")
                base = font_base_sizes.setdefault(key, control.text_size or 14)
                control.text_size = base * factor
                key = (control_id, "dropdown_label")
                label_size = getattr(control.label_style, "size", None) if control.label_style else None
                base_label = font_base_sizes.setdefault(key, label_size or 14)
                control.label_style = ft.TextStyle(size=base_label * factor)
            elif isinstance(control, ft.Switch):
                key = (control_id, "switch_label")
                label_style = control.label_text_style
                base = font_base_sizes.setdefault(
                    key,
                    getattr(label_style, "size", None) or 14,
                )
                control.label_text_style = ft.TextStyle(size=base * factor)
            elif isinstance(control, ft.Button):
                key = (control_id, "button_text")
                style = control.style
                text_style = getattr(style, "text_style", None) if style else None
                base = font_base_sizes.setdefault(key, getattr(text_style, "size", None) or 14)
                control.style = ft.ButtonStyle(text_style=ft.TextStyle(size=base * factor))
        page.update()

    dark_mode_switch = ft.Switch(
        label="深色模式",
        value=False,
        on_change=on_theme_change,
    )
    font_size_dropdown = ft.Dropdown(
        label="字體大小",
        value="medium",
        options=[
            ft.DropdownOption(key="medium", text="中"),
            ft.DropdownOption(key="large", text="大"),
            ft.DropdownOption(key="small", text="小"),
        ],
        on_select=on_font_size_change,
    )
    language_dropdown = ft.Dropdown(
        label="語言",
        value="zh-TW",
        options=[
            ft.DropdownOption(key="zh-TW", text="繁體中文"),
            ft.DropdownOption(key="en", text="English"),
        ],
        on_select=on_language_change,
    )
    appearance_controls = ft.Row(
        [language_dropdown, dark_mode_switch, font_size_dropdown],
        wrap=True,
        spacing=12,
    )

    page.add(
        ft.Row(
            [
                ft.Text("📄 Smart PDF Toolkit", size=24, weight=ft.FontWeight.BOLD),
                appearance_controls,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            wrap=True,
        ),
        file_banner,
        ft.Container(content=nav_row, margin=10),
        ft.Column(views),
        ft.Text("© 2026 Chia-Yi Chu. All rights reserved."),
        ft.Text("Developer email: nou.tools.dev@gmail.com"),
    )
    ui_mounted = True
    apply_language()
    refresh_uploaded_files()
    update_ui_state()
    asyncio.create_task(watch_day_change())
    on_font_size_change()


if __name__ == "__main__":
    ft.run(main)
