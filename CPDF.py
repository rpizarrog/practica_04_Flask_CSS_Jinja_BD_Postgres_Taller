# ============================================================
# CPDF.py
# Generación de cotización en formato PDF
# Práctica 04 - Taller Mecánico
# ============================================================

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import cm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)


# ============================================================
# FUNCIÓN GENERAR PDF DE COTIZACIÓN
# ============================================================

def f_generar_pdf_cotizacion(
    solicitud,
    subtotal,
    iva,
    total
):

    # ========================================================
    # 1. CREAR PDF EN MEMORIA
    # ========================================================

    buffer = BytesIO()


    # ========================================================
    # 2. CONFIGURAR DOCUMENTO
    # ========================================================

    documento = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )


    # ========================================================
    # 3. ESTILOS
    # ========================================================

    estilos = getSampleStyleSheet()


    estilo_titulo = ParagraphStyle(
        "Titulo",
        parent=estilos["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=5
    )


    estilo_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=estilos["Heading2"],
        alignment=TA_CENTER,
        fontSize=13,
        leading=16,
        spaceAfter=15
    )


    estilo_seccion = ParagraphStyle(
        "Seccion",
        parent=estilos["Heading3"],
        fontSize=12,
        leading=15,
        spaceBefore=8,
        spaceAfter=8
    )


    estilo_normal = ParagraphStyle(
        "NormalCotizacion",
        parent=estilos["BodyText"],
        fontSize=10,
        leading=15
    )


    estilo_total = ParagraphStyle(
        "Total",
        parent=estilos["Heading2"],
        alignment=TA_RIGHT,
        fontSize=15,
        leading=18,
        spaceBefore=8
    )


    estilo_aviso = ParagraphStyle(
        "Aviso",
        parent=estilos["BodyText"],
        fontSize=9,
        leading=13
    )


    estilo_pie = ParagraphStyle(
        "Pie",
        parent=estilos["BodyText"],
        alignment=TA_CENTER,
        fontSize=8
    )


    # ========================================================
    # 4. ELEMENTOS DEL DOCUMENTO
    # ========================================================

    elementos = []


    # ========================================================
    # ENCABEZADO
    # ========================================================

    elementos.append(
        Paragraph(
            "TALLER MECÁNICO",
            estilo_titulo
        )
    )

    elementos.append(
        Paragraph(
            "COTIZACIÓN PRELIMINAR DE SERVICIO",
            estilo_subtitulo
        )
    )

    elementos.append(
        HRFlowable(
            width="100%",
            thickness=1
        )
    )

    elementos.append(
        Spacer(1, 12)
    )


    # ========================================================
    # DATOS DE LA SOLICITUD
    # ========================================================

    elementos.append(
        Paragraph(
            "Datos de la solicitud",
            estilo_seccion
        )
    )


    fecha = ""

    if solicitud[1]:
        fecha = solicitud[1].strftime("%d/%m/%Y")


    datos_solicitud = [

        [
            "Número de solicitud:",
            str(solicitud[0])
        ],

        [
            "Fecha:",
            fecha
        ],

        [
            "Estado:",
            str(solicitud[16])
        ]

    ]


    tabla_solicitud = Table(
        datos_solicitud,
        colWidths=[
            5 * cm,
            11 * cm
        ]
    )


    tabla_solicitud.setStyle(
        TableStyle([

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            )

        ])
    )


    elementos.append(tabla_solicitud)

    elementos.append(
        Spacer(1, 12)
    )


    # ========================================================
    # DATOS DEL CLIENTE
    # ========================================================

    elementos.append(
        Paragraph(
            "Datos del cliente",
            estilo_seccion
        )
    )


    nombre_cliente = (
        f"{solicitud[2]} "
        f"{solicitud[3]} "
        f"{solicitud[4] or ''}"
    )


    datos_cliente = [

        [
            "Nombre:",
            nombre_cliente
        ],

        [
            "Correo electrónico:",
            str(solicitud[5])
        ],

        [
            "Teléfono:",
            str(solicitud[6])
        ]

    ]


    tabla_cliente = Table(
        datos_cliente,
        colWidths=[
            5 * cm,
            11 * cm
        ]
    )


    tabla_cliente.setStyle(
        TableStyle([

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            )

        ])
    )


    elementos.append(tabla_cliente)

    elementos.append(
        Spacer(1, 12)
    )


    # ========================================================
    # DATOS DEL VEHÍCULO
    # ========================================================

    elementos.append(
        Paragraph(
            "Datos del vehículo",
            estilo_seccion
        )
    )


    datos_vehiculo = [

        [
            "Marca:",
            str(solicitud[7])
        ],

        [
            "Modelo:",
            str(solicitud[8])
        ],

        [
            "Año:",
            str(solicitud[9])
        ],

        [
            "Kilometraje:",
            f"{solicitud[10]} km"
        ]

    ]


    tabla_vehiculo = Table(
        datos_vehiculo,
        colWidths=[
            5 * cm,
            11 * cm
        ]
    )


    tabla_vehiculo.setStyle(
        TableStyle([

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            )

        ])
    )


    elementos.append(tabla_vehiculo)

    elementos.append(
        Spacer(1, 12)
    )


    # ========================================================
    # SERVICIO SOLICITADO
    # ========================================================

    elementos.append(
        Paragraph(
            "Servicio solicitado",
            estilo_seccion
        )
    )


    elementos.append(
        Paragraph(
            f"<b>Servicio:</b> {solicitud[12]}",
            estilo_normal
        )
    )


    elementos.append(
        Spacer(1, 5)
    )


    elementos.append(
        Paragraph(
            f"<b>Descripción:</b> {solicitud[13]}",
            estilo_normal
        )
    )


    elementos.append(
        Spacer(1, 5)
    )


    elementos.append(
        Paragraph(
            f"<b>Problema reportado:</b> {solicitud[15]}",
            estilo_normal
        )
    )


    elementos.append(
        Spacer(1, 18)
    )


    # ========================================================
    # IMPORTE DE LA COTIZACIÓN
    # ========================================================

    elementos.append(
        Paragraph(
            "Importe de la cotización",
            estilo_seccion
        )
    )


    datos_importe = [

        [
            "Servicio / diagnóstico base",
            f"${subtotal:,.2f}"
        ],

        [
            "Subtotal",
            f"${subtotal:,.2f}"
        ],

        [
            "IVA (16%)",
            f"${iva:,.2f}"
        ]

    ]


    tabla_importe = Table(
        datos_importe,
        colWidths=[
            11 * cm,
            5 * cm
        ]
    )


    tabla_importe.setStyle(
        TableStyle([

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "ALIGN",
                (1, 0),
                (1, -1),
                "RIGHT"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "LINEBELOW",
                (0, -1),
                (-1, -1),
                1,
                colors.grey
            )

        ])
    )


    elementos.append(tabla_importe)


    elementos.append(
        Spacer(1, 12)
    )


    elementos.append(
        Paragraph(
            f"<b>TOTAL ESTIMADO: ${total:,.2f}</b>",
            estilo_total
        )
    )


    elementos.append(
        Spacer(1, 20)
    )


    # ========================================================
    # AVISO IMPORTANTE
    # ========================================================

    elementos.append(
        Paragraph(
            "IMPORTANTE",
            estilo_seccion
        )
    )


    elementos.append(
        Paragraph(
            "La presente cotización es de carácter "
            "<b>preliminar</b> y corresponde al servicio "
            "inicialmente solicitado.",
            estilo_aviso
        )
    )


    elementos.append(
        Spacer(1, 6)
    )


    elementos.append(
        Paragraph(
            "El precio final puede variar debido a "
            "<b>gastos derivados del diagnóstico especializado</b>, "
            "entre los que pueden incluirse:",
            estilo_aviso
        )
    )


    elementos.append(
        Spacer(1, 8)
    )


    lista_gastos = [
        "Refacciones o componentes que requieran sustitución.",
        "Mano de obra adicional.",
        "Pruebas y diagnósticos especializados.",
        "Uso de equipo especializado de diagnóstico.",
        "Líquidos, lubricantes y materiales adicionales.",
        "Reparaciones adicionales detectadas durante la revisión.",
        "Servicios externos especializados que pudieran ser necesarios."
    ]


    for gasto in lista_gastos:

        elementos.append(
            Paragraph(
                f"• {gasto}",
                estilo_aviso
            )
        )

        elementos.append(
            Spacer(1, 3)
        )


    elementos.append(
        Spacer(1, 6)
    )


    elementos.append(
        Paragraph(
            "<b>Cualquier trabajo o gasto adicional será "
            "informado al cliente y deberá ser autorizado "
            "antes de realizarse.</b>",
            estilo_aviso
        )
    )


    elementos.append(
        Spacer(1, 20)
    )


    # ========================================================
    # PIE DEL DOCUMENTO
    # ========================================================

    elementos.append(
        HRFlowable(
            width="100%",
            thickness=0.5
        )
    )


    elementos.append(
        Spacer(1, 8)
    )


    elementos.append(
        Paragraph(
            "Taller Mecánico | "
            "Sistema Web de Solicitudes de Servicio",
            estilo_pie
        )
    )


    # ========================================================
    # CONSTRUIR EL PDF
    # ========================================================

    documento.build(elementos)


    # Regresar el apuntador al inicio del archivo en memoria
    buffer.seek(0)


    # Devolver PDF
    return buffer