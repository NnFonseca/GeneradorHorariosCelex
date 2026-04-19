import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import re
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
 
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
 
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_celex.png")
 
 
class AppGeneradorPDF:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.estilo_celda = ParagraphStyle(
            "celda", parent=self.styles["Normal"], fontSize=8, alignment=TA_CENTER
        )
        self.estilo_titulo = ParagraphStyle(
            "titulo", parent=self.styles["Normal"], fontSize=14,
            fontName="Helvetica-Bold", alignment=TA_CENTER
        )
        self.estilo_subtitulo = ParagraphStyle(
            "subtitulo", parent=self.styles["Normal"], fontSize=11, alignment=TA_CENTER
        )
 
    def extraer_datos(self, ruta_txt):
        """Lee el TXT y agrupa la información por materia."""
        materias = {}
        try:
            with open(ruta_txt, "r", encoding="latin-1") as f:
                for linea in f:
                    if "|" not in linea or "ACTA DE IDIOMA" in linea:
                        continue
                    columnas = [col.strip() for col in linea.split("|")]
                    if len(columnas) < 29:
                        continue
 
                    clave = columnas[2]
                    uea = columnas[3]
                    grupo = columnas[4]
                    profe = f"{columnas[9]} {columnas[10]} {columnas[11]}".strip()
 
                    # FIX: strip() en ini para evitar falsos positivos con espacios
                    def fmt_h(ini, fin, sal):
                        ini = ini.strip()
                        return f"{ini} a {fin}<br/><b>{sal}</b>" if ini and ini != "0" else ""
 
                    fila = [
                        clave, uea, grupo, profe,
                        fmt_h(columnas[12], columnas[13], columnas[24]),
                        fmt_h(columnas[14], columnas[15], columnas[25]),
                        fmt_h(columnas[16], columnas[17], columnas[26]),
                        fmt_h(columnas[18], columnas[19], columnas[27]),
                        fmt_h(columnas[20], columnas[21], columnas[28]),
                    ]
 
                    if uea not in materias:
                        materias[uea] = []
                    materias[uea].append(fila)
            return materias
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer archivo: {e}")
            return {}
 
    def crear_pdf(self, nombre_uea, filas, carpeta, trimestre):
        archivo_path = os.path.join(
            carpeta, f"{re.sub(r'[\\/*?:\"<>|]', '', nombre_uea)}.pdf"
        )
        doc = SimpleDocTemplate(
            archivo_path, pagesize=landscape(letter),
            topMargin=20, bottomMargin=20, leftMargin=20, rightMargin=20
        )
 
        # Encabezado con logo y texto
        logo = (
            RLImage(LOGO_PATH, width=150, height=70)
            if os.path.exists(LOGO_PATH)
            else Paragraph("<b>LOGO</b>", self.estilo_celda)
        )
        header = Table(
            [[logo, [
                Paragraph(f"Horario {nombre_uea}", self.estilo_titulo),
                Spacer(1, 4),
                Paragraph(f"TRIM. {trimestre.upper()}", self.estilo_subtitulo),
            ]]],
            colWidths=[160, 570],
        )
        header.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LINEBELOW", (0, 0), (-1, 0), 1.5, colors.red),
        ]))
 
        # Tabla de horarios
        # FIX: colWidths ajustado para no desbordar landscape(letter) ≈ 752 pt útiles
        data = [["CLAVE UEA", "UEA", "GRUPO", "PROFESOR", "LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES"]]
        data += [[Paragraph(str(c), self.estilo_celda) for c in f] for f in filas]
 
        tabla = Table(
            data,
            colWidths=[50, 95, 45, 127, 72, 72, 72, 72, 72],
            repeatRows=1,
        )
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.red),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
        ]))
 
        doc.build([header, Spacer(1, 10), tabla])
 
 
class VentanaPrincipal(ctk.CTk):
 
    def __init__(self):
        super().__init__()
        self.title("CELEX UAM-A — Generador de Horarios")
        self.geometry("600x520")
        self.app_logic = AppGeneradorPDF()
        self.datos_agrupados = {}
        self.checks_materias = {}
 
        # Título
        ctk.CTkLabel(self, text="Generador de Horarios", font=("Arial", 20, "bold")).pack(pady=20)
 
        # Fila de trimestre
        frame_top = ctk.CTkFrame(self)
        frame_top.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(frame_top, text="Trimestre:").pack(side="left", padx=10)
        self.entry_trim = ctk.CTkEntry(frame_top, placeholder_text="ej. 26P", width=100)
        self.entry_trim.insert(0, "26P")
        self.entry_trim.pack(side="left", padx=10)
 
        # Botón cargar
        ctk.CTkButton(self, text="1. Cargar Archivo TXT", command=self.cargar_archivo).pack(pady=10)
 
        # Botón toggle (alineado a la derecha)
        self.btn_toggle = ctk.CTkButton(
            self,
            text="Marcar / Desmarcar Todas",
            command=self.toggle_todas,
            height=28,
            fg_color="gray",
            hover_color="#555555",
        )
        self.btn_toggle.pack(pady=(5, 0), padx=20, anchor="e")
 
        # FIX: scroll_frame creado UNA SOLA VEZ (antes estaba duplicado)
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Selecciona Materias")
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)
 
        # Barra de progreso
        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(pady=10, padx=20, fill="x")
        self.progress.set(0)
 
        # Botones de acción
        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack(pady=20)
        ctk.CTkButton(
            frame_btns, text="Generar PDFs", fg_color="red", command=self.generar_pdfs
        ).pack(side="left", padx=10)
         # ctk.CTkButton(
         #   frame_btns, text="Exportar Excel", fg_color="green", command=self.exportar_excel
       # ).pack(side="left", padx=10)
 
    def cargar_archivo(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if archivo:
            self.datos_agrupados = self.app_logic.extraer_datos(archivo)
            for widget in self.scroll_frame.winfo_children():
                widget.destroy()
            self.checks_materias = {}
            for materia in sorted(self.datos_agrupados.keys()):
                var = ctk.BooleanVar(value=True)
                cb = ctk.CTkCheckBox(self.scroll_frame, text=materia, variable=var)
                cb.pack(anchor="w", padx=10, pady=2)
                self.checks_materias[materia] = var
            messagebox.showinfo("Cargado", f"Se encontraron {len(self.datos_agrupados)} materias.")
 
    def obtener_seleccionadas(self):
        return [m for m, v in self.checks_materias.items() if v.get()]
 
    def generar_pdfs(self):
        seleccion = self.obtener_seleccionadas()
        if not seleccion:
            return messagebox.showwarning("Aviso", "Selecciona al menos una materia.")
        carpeta = filedialog.askdirectory()
        if not carpeta:
            return
 
        total = len(seleccion)
        for i, materia in enumerate(seleccion):
            self.app_logic.crear_pdf(
                materia, self.datos_agrupados[materia], carpeta, self.entry_trim.get()
            )
            self.progress.set((i + 1) / total)
            self.update_idletasks()
 
        messagebox.showinfo("Éxito", f"PDFs generados en: {carpeta}")
        self.progress.set(0)
 
    def toggle_todas(self):
        if not self.checks_materias:
            return
        todas_marcadas = all(var.get() for var in self.checks_materias.values())
        nuevo_estado = not todas_marcadas
        for var in self.checks_materias.values():
            var.set(nuevo_estado)
 
    def exportar_excel(self):
        seleccion = self.obtener_seleccionadas()
        if not seleccion:
            return messagebox.showwarning("Aviso", "Selecciona al menos una materia.")
        ruta_save = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")]
        )
        if not ruta_save:
            return
 
        todas_filas = []
        for materia in seleccion:
            todas_filas.extend(self.datos_agrupados[materia])
 
        df = pd.DataFrame(
            todas_filas,
            columns=["CLAVE", "UEA", "GRUPO", "PROFESOR", "LUN", "MAR", "MIE", "JUE", "VIE"],
        )
 
        # FIX: fillna("") antes de limpiar HTML para evitar errores con celdas vacías
        for col in ["LUN", "MAR", "MIE", "JUE", "VIE"]:
            df[col] = (
                df[col]
                .fillna("")
                .str.replace("<br/><b>", " - ", regex=False)
                .str.replace("</b>", "", regex=False)
            )
 
        df.to_excel(ruta_save, index=False)
        messagebox.showinfo("Excel", "Datos exportados correctamente.")
 
 
if __name__ == "__main__":
    app = VentanaPrincipal()
    app.mainloop()
    