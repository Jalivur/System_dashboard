"""
Ventana de cámara del FNK0100K con OCR integrado.
- Captura fotos con rpicam-still (OV5647, Bookworm)
- OCR con Tesseract (local, sin internet)
- Guarda resultado en .txt y .md

Requisitos:
    sudo apt install tesseract-ocr tesseract-ocr-spa rpicam-apps
    pip install pytesseract pillow --break-system-packages
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES,
                              DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y)
from ui.styles import StyleManager, make_window_header, make_futuristic_button
import subprocess
import threading
import os
from datetime import datetime
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

_PHOTO_DIR  = Path(__file__).resolve().parent.parent.parent / "data" / "photos"
_SCAN_DIR   = Path(__file__).resolve().parent.parent.parent / "data" / "scans"
_MAX_PHOTOS = 20

# Ancho del inner scrollable (mismo que el resto del proyecto)
_INNER_W = DSI_WIDTH - 50


class CameraWindow(ctk.CTkToplevel):
    """Ventana de cámara con captura de fotos y escáner OCR."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Cámara / Escáner")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        _PHOTO_DIR.mkdir(parents=True, exist_ok=True)
        _SCAN_DIR.mkdir(parents=True, exist_ok=True)

        self._busy       = False
        self._active_tab = "photo"   # "photo" | "scan"

        # Canvas/inner referencias para poder cambiar de tab
        self._canvases = {}
        self._inners   = {}

        self._create_ui()
        self._refresh_photo_list()
        self._refresh_scan_list()

    # ── Estructura principal ──────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="CÁMARA / ESCÁNER OCR", on_close=self.destroy)

        # ── Selector de tab (botones) ──
        tab_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'], corner_radius=8)
        tab_bar.pack(fill="x", padx=5, pady=(0, 4))

        self._tab_photo_btn = make_futuristic_button(
            tab_bar, text="📷 Foto",
            command=lambda: self._switch_tab("photo"),
            width=14, height=7, font_size=14,
        )
        self._tab_photo_btn.pack(side="left", padx=8, pady=6)

        self._tab_scan_btn = make_futuristic_button(
            tab_bar, text="🔍 Escáner OCR",
            command=lambda: self._switch_tab("scan"),
            width=18, height=7, font_size=14,
        )
        self._tab_scan_btn.pack(side="left", padx=4, pady=6)

        # ── Contenedor de tabs ──
        self._tab_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        self._tab_container.pack(fill="both", expand=True)

        # Construir ambas tabs (solo una visible a la vez)
        self._photo_frame = self._build_scrollable_tab(self._tab_container)
        self._scan_frame  = self._build_scrollable_tab(self._tab_container)

        self._build_photo_content(self._inners["photo"])
        self._build_scan_content(self._inners["scan"])

        # Mostrar tab foto por defecto
        self._switch_tab("photo")

    def _build_scrollable_tab(self, parent) -> ctk.CTkFrame:
        """
        Crea un frame con el patrón estándar del proyecto:
        scroll_container → canvas + CTkScrollbar → inner frame
        """
        tab_name = "photo" if "photo" not in self._canvases else "scan"

        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])

        scroll_container = ctk.CTkFrame(frame, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30,
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=_INNER_W)
        inner.bind("<Configure>",
                   lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))

        self._canvases[tab_name] = canvas
        self._inners[tab_name]   = inner

        return frame

    def _switch_tab(self, tab: str):
        self._active_tab = tab

        # Mostrar/ocultar frames
        if tab == "photo":
            self._scan_frame.pack_forget()
            self._photo_frame.pack(fill="both", expand=True)
            self._tab_photo_btn.configure(
                fg_color=COLORS['primary'], border_width=2,
                border_color=COLORS['secondary'])
            self._tab_scan_btn.configure(
                fg_color=COLORS['bg_dark'], border_width=1,
                border_color=COLORS['border'])
        else:
            self._photo_frame.pack_forget()
            self._scan_frame.pack(fill="both", expand=True)
            self._tab_scan_btn.configure(
                fg_color=COLORS['primary'], border_width=2,
                border_color=COLORS['secondary'])
            self._tab_photo_btn.configure(
                fg_color=COLORS['bg_dark'], border_width=1,
                border_color=COLORS['border'])

    # ── Contenido tab FOTO ────────────────────────────────────────────────────

    def _build_photo_content(self, inner: ctk.CTkFrame):
        # Controles captura
        ctrl = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        ctrl.pack(fill="x", padx=10, pady=(6, 4))

        row = ctk.CTkFrame(ctrl, fg_color="transparent")
        row.pack(pady=10)

        self._photo_btn = make_futuristic_button(
            row, text="📷 Capturar",
            command=self._capture_photo,
            width=16, height=9, font_size=16,
        )
        self._photo_btn.pack(side="left", padx=10)

        ctk.CTkLabel(row, text="Resolución:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(16, 4))

        self._res_var = ctk.StringVar(value="1920x1080")
        ctk.CTkOptionMenu(
            row, variable=self._res_var,
            values=["640x480", "1296x972", "1920x1080", "2592x1944"],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            button_color=COLORS['primary'],
            width=140,
        ).pack(side="left")

        self._photo_status = ctk.CTkLabel(
            ctrl, text="Listo",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        )
        self._photo_status.pack(pady=(0, 8))

        # Cabecera lista fotos
        list_hdr = ctk.CTkFrame(inner, fg_color="transparent")
        list_hdr.pack(fill="x", padx=10, pady=(4, 2))

        ctk.CTkLabel(list_hdr, text=f"Fotos guardadas (máx. {_MAX_PHOTOS})",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left")

        make_futuristic_button(
            list_hdr, text="🗑 Borrar todas",
            command=self._delete_all_photos,
            width=12, height=6, font_size=11,
        ).pack(side="right")

        # Lista fotos con scroll propio
        self._photo_list_frame = self._build_inner_scroll(inner, height=300)

    # ── Contenido tab ESCÁNER ─────────────────────────────────────────────────

    def _build_scan_content(self, inner: ctk.CTkFrame):
        # Controles escáner
        ctrl = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        ctrl.pack(fill="x", padx=10, pady=(6, 4))

        row = ctk.CTkFrame(ctrl, fg_color="transparent")
        row.pack(pady=8)

        self._scan_btn = make_futuristic_button(
            row, text="🔍 Escanear documento",
            command=self._scan_document,
            width=22, height=9, font_size=16,
        )
        self._scan_btn.pack(side="left", padx=10)

        ctk.CTkLabel(row, text="Idioma:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(16, 4))

        self._lang_var = ctk.StringVar(value="spa")
        ctk.CTkOptionMenu(
            row, variable=self._lang_var,
            values=["spa", "eng", "spa+eng"],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            button_color=COLORS['primary'],
            width=110,
        ).pack(side="left")

        self._scan_status = ctk.CTkLabel(
            ctrl, text="Coloca el documento y pulsa Escanear",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        )
        self._scan_status.pack(pady=(0, 8))

        # Texto extraído
        txt_hdr = ctk.CTkFrame(inner, fg_color="transparent")
        txt_hdr.pack(fill="x", padx=10, pady=(4, 2))

        ctk.CTkLabel(txt_hdr, text="Texto extraído:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left")

        self._copy_btn = make_futuristic_button(
            txt_hdr, text="📋 Copiar",
            command=self._copy_text,
            width=10, height=5, font_size=11,
        )
        self._copy_btn.pack(side="right")
        self._copy_btn.configure(state="disabled")

        self._text_box = ctk.CTkTextbox(
            inner,
            fg_color=COLORS['bg_dark'],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            height=160,
            wrap="word",
        )
        self._text_box.pack(fill="x", padx=10, pady=4)
        self._text_box.configure(state="disabled")

        # Cabecera lista escaneos
        scan_hdr = ctk.CTkFrame(inner, fg_color="transparent")
        scan_hdr.pack(fill="x", padx=10, pady=(6, 2))

        ctk.CTkLabel(scan_hdr, text="Escaneos guardados:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left")

        make_futuristic_button(
            scan_hdr, text="🗑 Borrar todos",
            command=self._delete_all_scans,
            width=12, height=6, font_size=11,
        ).pack(side="right")

        # Lista escaneos con scroll propio
        self._scan_list_frame = self._build_inner_scroll(inner, height=200)

    # ── Scroll interno para listas ────────────────────────────────────────────

    def _build_inner_scroll(self, parent: ctk.CTkFrame, height: int) -> ctk.CTkFrame:
        """
        Crea un scroll interno para una lista de items.
        Mismo patrón que el scroll principal: container → canvas + CTkScrollbar → inner.
        Devuelve el inner frame donde añadir los items.
        """
        container = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'],
                                 corner_radius=6, height=height)
        container.pack(fill="x", padx=10, pady=(0, 6))
        container.pack_propagate(False)   # respetar height fija

        canvas = ctk.CTkCanvas(
            container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            container,
            orientation="vertical",
            command=canvas.yview,
            width=30,
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw",
                             width=_INNER_W - 40)
        inner.bind("<Configure>",
                   lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))

        return inner

    # ── Captura de foto ───────────────────────────────────────────────────────

    def _capture_photo(self):
        if self._busy:
            return
        self._busy = True
        self._photo_btn.configure(state="disabled")
        self._photo_status.configure(text="⏳ Capturando...", text_color=COLORS['text'])
        threading.Thread(target=self._do_capture, daemon=True).start()

    def _do_capture(self):
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = _PHOTO_DIR / f"foto_{ts}.jpg"
        w, h     = self._res_var.get().split("x")
        ok, msg  = self._rpicam_capture(filename, w, h)
        if ok:
            self._cleanup_old_photos()
        self.after(0, self._capture_done, msg)

    def _capture_done(self, msg: str):
        self._busy = False
        self._photo_btn.configure(state="normal")
        color = COLORS['primary'] if msg.startswith("✅") else COLORS['danger']
        self._photo_status.configure(text=msg, text_color=color)
        self._refresh_photo_list()

    # ── Escáner OCR ───────────────────────────────────────────────────────────

    def _scan_document(self):
        if self._busy:
            return
        self._busy = True
        self._scan_btn.configure(state="disabled")
        self._scan_status.configure(text="⏳ Capturando imagen...",
                                    text_color=COLORS['text'])
        self._clear_textbox()
        threading.Thread(target=self._do_scan, daemon=True).start()

    def _do_scan(self):
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_path = _PHOTO_DIR / f"scan_src_{ts}.jpg"
        lang     = self._lang_var.get()

        ok, msg = self._rpicam_capture(img_path, "2592", "1944")
        if not ok:
            self.after(0, self._scan_done, msg, None)
            return

        self.after(0, lambda: self._scan_status.configure(
            text="⏳ Procesando imagen..."))
        proc_path = _PHOTO_DIR / f"scan_proc_{ts}.jpg"
        self._preprocess_image(img_path, proc_path)

        self.after(0, lambda: self._scan_status.configure(
            text="⏳ Extrayendo texto (OCR)..."))
        text, ocr_msg = self._run_ocr(proc_path, lang)

        if text:
            txt_path = _SCAN_DIR / f"scan_{ts}.txt"
            md_path  = _SCAN_DIR / f"scan_{ts}.md"
            self._save_txt(txt_path, text, ts)
            self._save_md(md_path, text, ts)

        for p in [img_path, proc_path]:
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass

        self.after(0, self._scan_done, ocr_msg, text)

    def _scan_done(self, msg: str, text):
        self._busy = False
        self._scan_btn.configure(state="normal")
        color = COLORS['primary'] if text else COLORS['danger']
        self._scan_status.configure(text=msg, text_color=color)
        if text:
            self._set_textbox(text)
            self._copy_btn.configure(state="normal")
        self._refresh_scan_list()

    # ── rpicam-still ─────────────────────────────────────────────────────────

    def _rpicam_capture(self, filename: Path, w: str, h: str):
        cmd = ["rpicam-still", "-o", str(filename),
               "--width", w, "--height", h,
               "--timeout", "2000", "--nopreview"]
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=20)
            if r.returncode == 0 and filename.exists():
                return True, f"✅ Capturada: {filename.name}"
            err = r.stderr.decode().strip()[:80]
            return False, f"❌ Error cámara: {err or 'rpicam-still falló'}"
        except FileNotFoundError:
            return False, "❌ rpicam-still no encontrado"
        except subprocess.TimeoutExpired:
            return False, "❌ Timeout — ¿cámara conectada?"
        except Exception as e:
            return False, f"❌ {e}"

    # ── Preprocesado + OCR ────────────────────────────────────────────────────

    def _preprocess_image(self, src: Path, dst: Path):
        try:
            from PIL import Image, ImageFilter, ImageEnhance
            img = Image.open(src).convert("L")
            img = ImageEnhance.Contrast(img).enhance(2.0)
            img = img.filter(ImageFilter.SHARPEN)
            img.save(str(dst), "JPEG", quality=95)
        except Exception as e:
            logger.warning("[CameraWindow] Preprocesado falló: %s", e)
            import shutil
            shutil.copy(str(src), str(dst))

    def _run_ocr(self, img_path: Path, lang: str):
        try:
            import pytesseract
            from PIL import Image
            img  = Image.open(str(img_path))
            text = pytesseract.image_to_string(
                img, config=f"--oem 3 --psm 6 -l {lang}"
            ).strip()
            if not text:
                return None, "⚠️ No se detectó texto en la imagen"
            words = len(text.split())
            lines = len(text.splitlines())
            return text, f"✅ {lines} líneas / {words} palabras extraídas"
        except ImportError:
            return None, "❌ pytesseract no instalado: pip install pytesseract"
        except Exception as e:
            return None, f"❌ Error OCR: {e}"

    # ── Guardado ──────────────────────────────────────────────────────────────

    def _save_txt(self, path: Path, text: str, ts: str):
        try:
            path.write_text(
                f"Escaneo: {ts}\n{'─' * 40}\n\n{text}", encoding="utf-8"
            )
        except Exception as e:
            logger.error("[CameraWindow] Error TXT: %s", e)

    def _save_md(self, path: Path, text: str, ts: str):
        try:
            dt = datetime.strptime(ts, "%Y%m%d_%H%M%S").strftime("%d/%m/%Y %H:%M:%S")
            lines = [
                "# Escaneo OCR", "",
                f"**Fecha:** {dt}  ",
                f"**Idioma:** {self._lang_var.get()}  ",
                f"**Palabras:** {len(text.split())}",
                "", "---", "", "## Texto extraído", "",
            ]
            for line in text.splitlines():
                lines.append(line if line.strip() else "")
            path.write_text("\n".join(lines), encoding="utf-8")
        except Exception as e:
            logger.error("[CameraWindow] Error MD: %s", e)

    # ── TextBox helpers ───────────────────────────────────────────────────────

    def _set_textbox(self, text: str):
        self._text_box.configure(state="normal")
        self._text_box.delete("1.0", "end")
        self._text_box.insert("1.0", text)
        self._text_box.configure(state="disabled")

    def _clear_textbox(self):
        self._text_box.configure(state="normal")
        self._text_box.delete("1.0", "end")
        self._text_box.configure(state="disabled")
        self._copy_btn.configure(state="disabled")

    def _copy_text(self):
        self._text_box.configure(state="normal")
        text = self._text_box.get("1.0", "end").strip()
        self._text_box.configure(state="disabled")
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self._copy_btn.configure(text="✅ Copiado")
            self.after(2000, lambda: self._copy_btn.configure(text="📋 Copiar"))

    # ── Listas ────────────────────────────────────────────────────────────────

    def _refresh_photo_list(self):
        for w in self._photo_list_frame.winfo_children():
            w.destroy()
        photos = sorted(_PHOTO_DIR.glob("foto_*.jpg"), reverse=True)
        if not photos:
            ctk.CTkLabel(self._photo_list_frame,
                         text="No hay fotos guardadas",
                         text_color=COLORS['text_dim']).pack(pady=10)
            return
        for p in photos:
            self._list_row(self._photo_list_frame, f"📷 {p.name}",
                           p.stat().st_size // 1024,
                           on_delete=lambda ph=p: self._delete_one_photo(ph))

    def _refresh_scan_list(self):
        for w in self._scan_list_frame.winfo_children():
            w.destroy()
        txts = sorted(_SCAN_DIR.glob("scan_*.txt"), reverse=True)
        if not txts:
            ctk.CTkLabel(self._scan_list_frame,
                         text="No hay escaneos guardados",
                         text_color=COLORS['text_dim']).pack(pady=10)
            return
        for txt in txts:
            md = txt.with_suffix(".md")
            self._scan_row(self._scan_list_frame, txt, md)

    def _list_row(self, parent, label: str, size_kb: int, on_delete):
        row = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=6)
        row.pack(fill="x", pady=2, padx=4)
        ctk.CTkLabel(row, text=f"{label}  ({size_kb} KB)",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text'], anchor="w",
                     ).pack(side="left", padx=10, pady=6, expand=True, fill="x")
        make_futuristic_button(
            row, text="🗑",
            command=on_delete,
            width=4, height=5, font_size=13,
        ).pack(side="right", padx=6, pady=4)

    def _scan_row(self, parent, txt: Path, md: Path):
        row = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=6)
        row.pack(fill="x", pady=2, padx=4)
        size_kb = txt.stat().st_size // 1024
        ctk.CTkLabel(row,
                     text=f"📄 {txt.stem}  ({size_kb} KB)  [.txt + .md]",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text'], anchor="w",
                     ).pack(side="left", padx=10, pady=6, expand=True, fill="x")
        make_futuristic_button(
            row, text="🗑",
            command=lambda t=txt, m=md: self._delete_scan(t, m),
            width=4, height=5, font_size=13,
        ).pack(side="right", padx=2, pady=4)
        make_futuristic_button(
            row, text="📂",
            command=lambda t=txt: self._load_scan(t),
            width=4, height=5, font_size=13,
        ).pack(side="right", padx=2, pady=4)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _load_scan(self, txt_path: Path):
        try:
            text = txt_path.read_text(encoding="utf-8")
            self._set_textbox(text)
            self._copy_btn.configure(state="normal")
            self._switch_tab("scan")
        except Exception as e:
            logger.error("[CameraWindow] Error cargando: %s", e)

    def _delete_scan(self, txt: Path, md: Path):
        for p in [txt, md]:
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass
        self._refresh_scan_list()

    def _delete_one_photo(self, p: Path):
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass
        self._refresh_photo_list()

    def _delete_all_photos(self):
        for p in _PHOTO_DIR.glob("foto_*.jpg"):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass
        self._refresh_photo_list()

    def _delete_all_scans(self):
        for p in _SCAN_DIR.glob("scan_*"):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass
        self._refresh_scan_list()
        self._clear_textbox()

    def _cleanup_old_photos(self):
        photos = sorted(_PHOTO_DIR.glob("foto_*.jpg"))
        while len(photos) > _MAX_PHOTOS:
            photos[0].unlink(missing_ok=True)
            photos = photos[1:]
