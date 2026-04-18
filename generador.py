import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re
import shutil
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import cm
 
 
# ─── Ruta al logo (debe estar en la misma carpeta que este script) ────────────
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_celex.png")
 
 
class AppGeneradorPDF:
    def __init__(self):
        self.styles = getSampleStyleSheet()
 
        # Estilo para celdas de la tabla
        self.estilo_celda = ParagraphStyle(
            "celda",
            parent=self.styles["Normal"],
            fontSize=8,
            alignment=TA_CENTER,
        )
 
        # Estilo para el título principal del encabezado
        self.estilo_titulo = ParagraphStyle(
            "titulo",
            parent=self.styles["Normal"],
            fontSize=14,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
            spaceAfter=2,
        )
 
        # Estilo para el subtítulo (trimestre)
        self.estilo_subtitulo = ParagraphStyle(
            "subtitulo",
            parent=self.styles["Normal"],
            fontSize=11,
            fontName="Helvetica",
            alignment=TA_CENTER,
        )
 
    # ─── Utilidades ──────────────────────────────────────────────────────────
 
    def limpiar_nombre(self, texto):
        """Limpia caracteres inválidos para nombres de archivo en Windows."""
        return re.sub(r'[\\/*?:"<>|]', "", texto.strip())
 
    # ─── Lectura del TXT ─────────────────────────────────────────────────────
 
    def extraer_datos(self, ruta_txt):
        """Lee el TXT y agrupa la información por materia (UEA)."""
        materias = {}
        try:
            with open(ruta_txt, "r", encoding="latin-1") as f:
                for linea in f:
                    if "|" not in linea or "ACTA DE IDIOMA" in linea:
                        continue
 
                    columnas = linea.split("|")
                    if len(columnas) < 29:
                        continue
 
                    clave  = columnas[2].strip()
                    uea    = columnas[3].strip()
                    grupo  = columnas[4].strip()
                    profe  = f"{columnas[9]} {columnas[10]} {columnas[11]}".strip()
 
                    def obtener_horario(h_ini, h_fin, salon):
                        if h_ini.strip() and h_ini != "0":
                            return f"{h_ini} a {h_fin}<br/><b>{salon}</b>"
                        return ""
 
                    dias = {
                        "LUN": obtener_horario(columnas[12], columnas[13], columnas[24]),
                        "MAR": obtener_horario(columnas[14], columnas[15], columnas[25]),
                        "MIE": obtener_horario(columnas[16], columnas[17], columnas[26]),
                        "JUE": obtener_horario(columnas[18], columnas[19], columnas[27]),
                        "VIE": obtener_horario(columnas[20], columnas[21], columnas[28]),
                    }
 
                    if uea not in materias:
                        materias[uea] = []
 
                    materias[uea].append(
                        [clave, uea, grupo, profe,
                         dias["LUN"], dias["MAR"], dias["MIE"], dias["JUE"], dias["VIE"]]
                    )
 
            return materias
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")
            return {}
 
    # ─── Construcción del encabezado ─────────────────────────────────────────
 
    def construir_encabezado(self, nombre_uea, trimestre, page_width, margins):
        """
        Devuelve una Table de una sola fila:
          - Columna izquierda : logo CELEX
          - Columna derecha   : título y trimestre centrados
        """
        usable_width = page_width - margins["left"] - margins["right"]
        logo_col_w   = 130   # puntos reservados para el logo
        title_col_w  = usable_width - logo_col_w
 
        # Logo ─────────────────────────────────────────────────────────────────
        if os.path.exists(LOGO_PATH):
            logo = RLImage(LOGO_PATH, width=200, height=90)
        else:
            # Si no se encuentra el logo, colocamos un texto de respaldo
            logo = Paragraph("<b>[logo_celex.png no encontrado]</b>", self.estilo_celda)
 
        # Texto del encabezado ─────────────────────────────────────────────────
        titulo    = Paragraph(f"Horario {nombre_uea}", self.estilo_titulo)
        subtitulo = Paragraph(f"TRIM. {trimestre.strip().upper()}", self.estilo_subtitulo)
 
        # Tabla 1×2 ────────────────────────────────────────────────────────────
        header_table = Table(
            [[logo, [titulo, Spacer(1, 4), subtitulo]]],
            colWidths=[logo_col_w, title_col_w],
        )
        header_table.setStyle(TableStyle([
            ("VALIGN",  (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN",   (0, 0), (0,  0),  "LEFT"),
            ("ALIGN",   (1, 0), (1,  0),  "CENTER"),
            ("LEFTPADDING",  (0, 0), (0, 0), 0),
            ("RIGHTPADDING", (0, 0), (0, 0), 6),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
            # Línea separadora inferior
            ("LINEBELOW", (0, 0), (-1, 0), 1.5, colors.red),
        ]))
        return header_table
 
    # ─── Generación del PDF ──────────────────────────────────────────────────
 
    def crear_pdf(self, nombre_uea, filas, carpeta, trimestre):
        """Genera el PDF con encabezado y tabla de horarios."""
        archivo_path = os.path.join(carpeta, f"{self.limpiar_nombre(nombre_uea)}.pdf")
 
        margins = {"top": 20, "bottom": 20, "left": 20, "right": 20}
        page_w, page_h = landscape(letter)   # 792 × 612 puntos
 
        doc = SimpleDocTemplate(
            archivo_path,
            pagesize=landscape(letter),
            topMargin=margins["top"],
            bottomMargin=margins["bottom"],
            leftMargin=margins["left"],
            rightMargin=margins["right"],
        )
 
        elementos = []
 
        # ── Encabezado ────────────────────────────────────────────────────────
        elementos.append(self.construir_encabezado(nombre_uea, trimestre, page_w, margins))
        elementos.append(Spacer(1, 10))
 
        # ── Tabla de horarios ─────────────────────────────────────────────────
        header_cols = ["CLAVE UEA", "UEA", "GRUPO", "PROFESOR",
                       "LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES"]
 
        data_tabla = [header_cols]
        for f in filas:
            fila_fmt = [Paragraph(str(celda), self.estilo_celda) for celda in f]
            data_tabla.append(fila_fmt)
 
        anchos = [50, 90, 45, 130, 75, 75, 75, 75, 75]
        tabla  = Table(data_tabla, colWidths=anchos, repeatRows=1)
        tabla.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), colors.red),
            ("TEXTCOLOR",    (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("GRID",         (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1),
             [colors.white, colors.Color(0.95, 0.95, 0.95)]),
        ]))
 
        elementos.append(tabla)
        doc.build(elementos)
 
 
# ─── Interfaz Gráfica ────────────────────────────────────────────────────────
 
def procesar(entrada_trimestre):
    trimestre = entrada_trimestre.get().strip()
    if not trimestre:
        messagebox.showwarning("Aviso", "Por favor ingresa el trimestre (ej. 26P).")
        return
 
    app = AppGeneradorPDF()
 
    archivo = filedialog.askopenfilename(
        title="Selecciona el archivo TXT",
        filetypes=[("Archivos de texto", "*.txt")],
    )
    if not archivo:
        return
 
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta donde guardar los PDFs")
    if not carpeta:
        return
 
    # Copiar logo a la carpeta del script si existe en uploads (primera ejecución)
    logo_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_celex.png")
    if not os.path.exists(logo_src):
        messagebox.showwarning(
            "Logo no encontrado",
            f"No se encontró 'logo_celex.png' junto al script.\n"
            f"Coloca el archivo en:\n{os.path.dirname(os.path.abspath(__file__))}",
        )
 
    datos_agrupados = app.extraer_datos(archivo)
    if not datos_agrupados:
        return
 
    for materia, clases in datos_agrupados.items():
        app.crear_pdf(materia, clases, carpeta, trimestre)
 
    messagebox.showinfo(
        "Éxito",
        f"Se generaron {len(datos_agrupados)} archivos PDF correctamente.\n"
        f"Trimestre: {trimestre.upper()}",
    )
 
 
# ─── Ventana principal ───────────────────────────────────────────────────────
 
ventana = tk.Tk()
ventana.title("CELEX UAM-A — Generador de Horarios v6.1")
ventana.geometry("800x600")
ventana.resizable(False, False)
 
# Título
tk.Label(
    ventana,
    text="Generador de Horarios CELEX UAM-A",
    font=("Arial", 12, "bold"),
    pady=16,
).pack()
 
# Campo trimestre
frame_trim = tk.Frame(ventana)
frame_trim.pack(pady=4)
 
tk.Label(frame_trim, text="Trimestre:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 8))
 
entrada_trimestre = tk.Entry(frame_trim, width=10, font=("Arial", 10))
entrada_trimestre.insert(0, "26P")   # valor por defecto orientativo
entrada_trimestre.pack(side=tk.LEFT)
 
tk.Label(frame_trim, text="(ej. 26P, 25O)", font=("Arial", 8), fg="gray").pack(side=tk.LEFT, padx=(6, 0))
 
# Botón principal
tk.Button(
    ventana,
    text="Cargar TXT y Generar PDFs por Materia",
    command=lambda: procesar(entrada_trimestre),
    bg="#d32f2f",
    fg="white",
    font=("Arial", 10, "bold"),
    padx=10,
    pady=10,
).pack(pady=16)
 
ventana.mainloop()