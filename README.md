Generador de Horarios CELEX - UAM Azcapotzalco
Esta es una aplicación de escritorio desarrollada en Python diseñada para automatizar la creación de horarios en formato PDF para la Unidad Azcapotzalco de la UAM. El programa toma como entrada un archivo de texto con el listado de cursos abiertos y genera archivos individuales y estilizados para cada materia (UEA).

 Características
Procesamiento Inteligente: Lee y organiza automáticamente los datos de los cursos abiertos basándose en el formato oficial de la UAM.

Diseño Profesional: Genera PDFs que imitan fielmente el diseño visual solicitado, con encabezados en rojo institucional y texto centrado.

Identidad Visual: Incluye el logotipo oficial de CELEX en el encabezado de cada documento.

Personalización: Permite al usuario ingresar manualmente el trimestre (ej. 26P) a través de una interfaz gráfica intuitiva.

Automatización de Archivos: Separa automáticamente los horarios, creando un archivo PDF independiente por cada materia detectada (ej. Inglés I.pdf, Alemán II.pdf).

 Tecnologías Utilizadas
Python 3.x

Tkinter: Para la interfaz gráfica de usuario (GUI).

ReportLab: Motor de generación de PDFs para un control preciso del diseño y tablas.

PyInstaller: Para la creación del archivo ejecutable (.exe).

> .[!NOTE].
>Requisitos
>Si deseas ejecutar el código fuente, necesitarás instalar las dependencias:

Bash
pip install reportlab
💻 Uso
Ejecuta la aplicación (.exe o script .py).

Ingresa el Trimestre correspondiente en el campo de texto.

Haz clic en el botón de carga.

Selecciona el archivo .txt de los cursos abiertos.

Elige la carpeta donde deseas guardar los archivos.

¡Listo! El programa abrirá automáticamente la carpeta con tus horarios generados.

📦 Cómo generar el ejecutable
Para crear el instalable incluyendo los recursos visuales, utiliza el siguiente comando:

Bash
pyinstaller --noconsole --onefile --add-data "logo_celex.png;." tu_script.py
Notas de Desarrollo
El mapeo de columnas está configurado específicamente para el orden de datos de la Unidad Azcapotzalco.

Se implementó una función de limpieza para asegurar que los nombres de las materias sean compatibles con el sistema de archivos de Windows.
