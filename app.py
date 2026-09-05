# ============================================================
# app.py
# PRÁCTICA 04
# Flask + Jinja + CSS + PostgreSQL
# Taller Mecánico
# ============================================================

from flask import (
    Flask,
    render_template,
    request,
    send_file,
    redirect,
    url_for
)




# ============================================================
# FUNCIONES POSTGRESQL
# ============================================================

from CPostgreSQL import (
    f_listar_servicios,
    f_registrar_solicitud,
    f_listar_solicitudes,
    f_obtener_solicitud,
    f_obtener_cotizacion,
    f_registrar_cotizacion
)


# ============================================================
# GENERACIÓN DE PDF
# ============================================================

from CPDF import f_generar_pdf_cotizacion


# ============================================================
# ENVÍO DE CORREO
# ============================================================

from CCorreo import f_enviar_cotizacion


# ============================================================
# CREAR APLICACIÓN FLASK
# ============================================================

app = Flask(__name__)


# ============================================================
# RUTA PRINCIPAL
# ============================================================

@app.route("/")
def inicio():

    servicios = f_listar_servicios()

    return render_template(
        "index.html",
        servicios=servicios
    )


# ============================================================
# REGISTRAR SOLICITUD DE COTIZACIÓN
# ============================================================

@app.route(
    "/solicitar_cotizacion",
    methods=["POST"]
)
def solicitar_cotizacion():

    # --------------------------------------------------------
    # 1. DATOS DEL CLIENTE
    # --------------------------------------------------------

    nombre = request.form["nombre"]
    apellido_paterno = request.form["apellido_paterno"]
    apellido_materno = request.form.get(
        "apellido_materno",
        ""
    )

    correo = request.form["correo"]
    telefono = request.form["telefono"]


    # --------------------------------------------------------
    # 2. DATOS DEL VEHÍCULO
    # --------------------------------------------------------

    marca = request.form["marca"]
    modelo = request.form["modelo"]
    anio = request.form["anio"]
    kilometraje = request.form["kilometraje"]


    # --------------------------------------------------------
    # 3. DATOS DEL SERVICIO
    # --------------------------------------------------------

    id_servicio = request.form["id_servicio"]

    descripcion_problema = request.form[
        "descripcion_problema"
    ]


    # --------------------------------------------------------
    # 4. REGISTRAR SOLICITUD EN POSTGRESQL
    # --------------------------------------------------------

    (
        id_cliente,
        id_vehiculo,
        id_solicitud

    ) = f_registrar_solicitud(

        nombre,
        apellido_paterno,
        apellido_materno,
        correo,
        telefono,

        marca,
        modelo,
        anio,
        kilometraje,

        id_servicio,
        descripcion_problema
    )


    # --------------------------------------------------------
    # 5. RECUPERAR LA SOLICITUD DESDE POSTGRESQL
    # --------------------------------------------------------

    solicitud = f_obtener_solicitud(
        id_solicitud
    )

    if solicitud is None:

        return (
            "No fue posible recuperar la solicitud",
            404
        )


    # --------------------------------------------------------
    # 6. MOSTRAR CONFIRMACIÓN
    # --------------------------------------------------------

    return render_template(

        "solicitud_recibida.html",

        solicitud=solicitud
    )

# ============================================================
# LISTAR SOLICITUDES
# ============================================================

@app.route("/solicitudes")
def listar_solicitudes():

    solicitudes = f_listar_solicitudes()

    return render_template(
        "solicitudes.html",
        solicitudes=solicitudes
    )


# ============================================================
# GENERAR / VISUALIZAR COTIZACIÓN
# ============================================================

@app.route("/cotizar/<int:id_solicitud>")
def cotizar(id_solicitud):

    # --------------------------------------------------------
    # 1. OBTENER SOLICITUD
    # --------------------------------------------------------

    solicitud = f_obtener_solicitud(
        id_solicitud
    )

    if solicitud is None:

        return (
            "La solicitud no existe",
            404
        )


    # --------------------------------------------------------
    # 2. VERIFICAR SI YA EXISTE COTIZACIÓN
    # --------------------------------------------------------

    cotizacion_existente = (
        f_obtener_cotizacion(
            id_solicitud
        )
    )


    # --------------------------------------------------------
    # 3. SI NO EXISTE, GENERAR Y GUARDAR
    # --------------------------------------------------------

    if cotizacion_existente is None:

        # Precio base del servicio
        subtotal = float(
            solicitud[14]
        )

        # IVA 16 %
        iva = subtotal * 0.16

        # Total
        total = subtotal + iva


        # ----------------------------------------------------
        # GUARDAR COTIZACIÓN EN POSTGRESQL
        # ----------------------------------------------------

        id_cotizacion = (
            f_registrar_cotizacion(

                id_solicitud,
                subtotal,
                iva,
                total

            )
        )


    # --------------------------------------------------------
    # 4. SI YA EXISTE, UTILIZAR VALORES GUARDADOS
    # --------------------------------------------------------

    else:

        id_cotizacion = (
            cotizacion_existente[0]
        )

        subtotal = float(
            cotizacion_existente[2]
        )

        iva = float(
            cotizacion_existente[3]
        )

        total = float(
            cotizacion_existente[4]
        )


    # --------------------------------------------------------
    # 5. MOSTRAR COTIZACIÓN
    # --------------------------------------------------------

    return render_template(

        "cotizacion.html",

        solicitud=solicitud,

        id_cotizacion=id_cotizacion,

        subtotal=subtotal,

        iva=iva,

        total=total
    )


# ============================================================
# GENERAR PDF DE LA COTIZACIÓN
# ============================================================

@app.route(
    "/cotizacion/pdf/<int:id_solicitud>"
)
def generar_pdf_cotizacion(id_solicitud):

    # --------------------------------------------------------
    # 1. OBTENER SOLICITUD
    # --------------------------------------------------------

    solicitud = f_obtener_solicitud(
        id_solicitud
    )

    if solicitud is None:

        return (
            "La solicitud no existe",
            404
        )


    # --------------------------------------------------------
    # 2. OBTENER COTIZACIÓN GUARDADA
    # --------------------------------------------------------

    cotizacion = f_obtener_cotizacion(
        id_solicitud
    )

    if cotizacion is None:

        return (
            "La solicitud todavía no tiene "
            "una cotización registrada.",
            404
        )


    # --------------------------------------------------------
    # 3. RECUPERAR IMPORTES DE POSTGRESQL
    # --------------------------------------------------------

    subtotal = float(
        cotizacion[2]
    )

    iva = float(
        cotizacion[3]
    )

    total = float(
        cotizacion[4]
    )


    # --------------------------------------------------------
    # 4. GENERAR PDF
    # --------------------------------------------------------

    pdf = f_generar_pdf_cotizacion(

        solicitud,
        subtotal,
        iva,
        total
    )


    # --------------------------------------------------------
    # 5. DESCARGAR PDF
    # --------------------------------------------------------

    return send_file(

        pdf,

        mimetype="application/pdf",

        as_attachment=True,

        download_name=(
            f"cotizacion_{id_solicitud}.pdf"
        )
    )


# ============================================================
# ENVIAR COTIZACIÓN POR CORREO
# ============================================================

@app.route(
    "/cotizacion/correo/<int:id_solicitud>",
    methods=["POST"]
)
def enviar_cotizacion_correo(
    id_solicitud):

    # --------------------------------------------------------
    # 1. OBTENER SOLICITUD
    # --------------------------------------------------------

    solicitud = f_obtener_solicitud(
        id_solicitud
    )

    if solicitud is None:

        return (
            "La solicitud no existe",
            404
        )


    # --------------------------------------------------------
    # 2. OBTENER COTIZACIÓN GUARDADA
    # --------------------------------------------------------

    cotizacion = f_obtener_cotizacion(
        id_solicitud
    )

    if cotizacion is None:

        return (
            "La solicitud todavía no tiene "
            "una cotización registrada.",
            404
        )


    # --------------------------------------------------------
    # 3. RECUPERAR IMPORTES
    # --------------------------------------------------------

    subtotal = float(
        cotizacion[2]
    )

    iva = float(
        cotizacion[3]
    )

    total = float(
        cotizacion[4]
    )


    # --------------------------------------------------------
    # 4. GENERAR PDF
    # --------------------------------------------------------

    pdf = f_generar_pdf_cotizacion(

        solicitud,
        subtotal,
        iva,
        total
    )


    # --------------------------------------------------------
    # 5. DATOS PARA EL CORREO
    # --------------------------------------------------------

    correo_cliente = solicitud[5]

    nombre_cliente = solicitud[2]

    nombre_servicio = solicitud[12]


    # --------------------------------------------------------
    # 6. ENVIAR CORREO
    # --------------------------------------------------------

    f_enviar_cotizacion(
        correo_cliente,
        pdf,
        id_solicitud,
        nombre_cliente,
        nombre_servicio,
        total
    )


    # --------------------------------------------------------
    # 7. REGRESAR A LA COTIZACIÓN
    # Indicamos mediante la URL que el correo fue enviado
    # --------------------------------------------------------

    return redirect(
        url_for(
            "cotizar",
            id_solicitud=id_solicitud,
            correo_enviado="si"
        )
    )

# ============================================================
# EJECUTAR APLICACIÓN
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )