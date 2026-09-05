# ============================================================
# CLASE / MÓDULO PARA ENVÍO DE CORREOS
# Práctica 04 - Taller Mecánico
# ============================================================

import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv


# ============================================================
# CARGAR VARIABLES DEL ARCHIVO .env
# ============================================================

load_dotenv()


# ============================================================
# FUNCIÓN: ENVIAR COTIZACIÓN POR CORREO
# ============================================================

def f_enviar_cotizacion(
    correo_destino,
    pdf,
    id_solicitud,
    nombre_cliente,
    nombre_servicio,
    total
):

    # --------------------------------------------------------
    # 1. OBTENER CREDENCIALES DESDE .env
    # --------------------------------------------------------

    correo_emisor = os.getenv("CORREO_EMISOR")
    clave_aplicacion = os.getenv("CORREO_PASSWORD")


    # --------------------------------------------------------
    # 2. VALIDAR VARIABLES DE ENTORNO
    # --------------------------------------------------------

    if not correo_emisor:
        raise ValueError(
            "No se encontró CORREO_EMISOR en el archivo .env"
        )

    if not clave_aplicacion:
        raise ValueError(
            "No se encontró CORREO_PASSWORD en el archivo .env"
        )

    if not correo_destino:
        raise ValueError(
            "No se proporcionó un correo de destino"
        )


    # --------------------------------------------------------
    # 3. CREAR EL MENSAJE
    # --------------------------------------------------------

    mensaje = EmailMessage()

    mensaje["From"] = correo_emisor

    mensaje["To"] = correo_destino

    mensaje["Subject"] = (
        f"Cotización de servicio #{id_solicitud} "
        "- Taller Mecánico"
    )


    # --------------------------------------------------------
    # 4. CUERPO DEL CORREO
    # --------------------------------------------------------

    mensaje.set_content(
        f"""
        Estimado(a) {nombre_cliente}:

        Adjuntamos la cotización correspondiente a su
        solicitud de servicio número {id_solicitud}.

        Servicio solicitado:
        {nombre_servicio}

        Total estimado:
        ${total:,.2f}

        La cotización adjunta es de carácter preliminar
        y está sujeta a la revisión física del vehículo.

        Saludos cordiales.

        Taller Mecánico
        """
    )


    # --------------------------------------------------------
    # 5. ADJUNTAR EL PDF
    # --------------------------------------------------------

    mensaje.add_attachment(
        pdf.getvalue(),
        maintype="application",
        subtype="pdf",
        filename=f"cotizacion_{id_solicitud}.pdf"
    )


    # --------------------------------------------------------
    # 6. CONECTARSE AL SERVIDOR SMTP DE GMAIL
    # --------------------------------------------------------

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as servidor:

        servidor.login(
            correo_emisor,
            clave_aplicacion
        )

        servidor.send_message(
            mensaje
        )


    # --------------------------------------------------------
    # 7. REGRESAR CONFIRMACIÓN
    # --------------------------------------------------------

    return True