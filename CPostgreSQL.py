# ============================================================
# CPostgreSQL.py
# Funciones de acceso a PostgreSQL
# Práctica 04 - Taller Mecánico
# ============================================================

import os
import psycopg2

from dotenv import load_dotenv


# ============================================================
# CARGAR VARIABLES DEL ARCHIVO .env
# ============================================================

load_dotenv()

# ============================================================
# TIPO DE CONEXIÓN
# ============================================================
# Valores permitidos:
# "LOCAL"  -> PostgreSQL instalado en esta computadora
# "AIVEN"  -> PostgreSQL en la nube
# ============================================================

# TIPO_CONEXION = "LOCAL"  # Pude modificarse a TIPO_CONEXION = "AIVEN" y cambairlo cuando sea local
# TIPO_CONEXION = "AIVEN"
TIPO_CONEXION = os.getenv(
    "TIPO_CONEXION",
    "LOCAL"
).upper()

# ============================================================
# CONEXIÓN A POSTGRESQL LOCAL
# Base de datos: taller
# Credenciales almacenadas en .env
# ============================================================

def f_conectar_local():

    conexion = psycopg2.connect(
        host=os.getenv("DB_LOCAL_HOST"),
        port=os.getenv("DB_LOCAL_PORT"),
        database=os.getenv("DB_LOCAL_NAME"),
        user=os.getenv("DB_LOCAL_USER"),
        password=os.getenv("DB_LOCAL_PASSWORD"),
        options="-c client_encoding=UTF8"
    )

    return conexion


# ============================================================
# CONEXIÓN A POSTGRESQL AIVEN
# Base de datos PostgreSQL en la nube
# Credenciales almacenadas en .env
# ============================================================

def f_conectar_aiven():

    conexion = psycopg2.connect(
        host=os.getenv("DB_AIVEN_HOST"),
        port=os.getenv("DB_AIVEN_PORT"),
        database=os.getenv("DB_AIVEN_NAME"),
        user=os.getenv("DB_AIVEN_USER"),
        password=os.getenv("DB_AIVEN_PASSWORD"),
        sslmode="require",
        options="-c client_encoding=UTF8"
    )

    return conexion

# ============================================================
# SELECCIONAR CONEXIÓN A POSTGRESQL localhost O Aiven en la Nube
# ============================================================

def f_conectar():

    if TIPO_CONEXION == "LOCAL":

        return f_conectar_local()

    elif TIPO_CONEXION == "AIVEN":

        return f_conectar_aiven()

    else:

        raise ValueError(
            "TIPO_CONEXION debe ser LOCAL o AIVEN"
        )

    
# ============================================================
# LISTAR SERVICIOS ACTIVOS
# ============================================================

def f_listar_servicios():

    # conexion = f_conectar_local() # old
    conexion = f_conectar()

    cursor = conexion.cursor()

    consulta = """
        SELECT
            id_servicio,
            nombre,
            descripcion,
            precio_base
        FROM servicios
        WHERE activo = TRUE
        ORDER BY id_servicio;
    """

    cursor.execute(consulta)

    servicios = cursor.fetchall()

    cursor.close()
    conexion.close()

    return servicios


# ============================================================
# REGISTRAR SOLICITUD
# ============================================================

def f_registrar_solicitud(
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
):

    # conexion = f_conectar_local() # old
    conexion = f_conectar()

    cursor = conexion.cursor()

    try:

        # ====================================================
        # 1. BUSCAR CLIENTE POR CORREO
        # ====================================================

        consulta_cliente = """
            SELECT id_cliente
            FROM clientes
            WHERE correo = %s;
        """

        cursor.execute(
            consulta_cliente,
            (correo,)
        )

        cliente = cursor.fetchone()


        # ====================================================
        # 2. SI NO EXISTE, REGISTRAR CLIENTE
        # ====================================================

        if cliente is None:

            consulta_insertar_cliente = """
                INSERT INTO clientes
                (
                    nombre,
                    apellido_paterno,
                    apellido_materno,
                    correo,
                    telefono
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_cliente;
            """

            cursor.execute(
                consulta_insertar_cliente,
                (
                    nombre,
                    apellido_paterno,
                    apellido_materno,
                    correo,
                    telefono
                )
            )

            id_cliente = cursor.fetchone()[0]

        else:

            id_cliente = cliente[0]


        # ====================================================
        # 3. REGISTRAR VEHÍCULO
        # ====================================================

        consulta_vehiculo = """
            INSERT INTO vehiculos
            (
                id_cliente,
                marca,
                modelo,
                anio,
                kilometraje
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_vehiculo;
        """

        cursor.execute(
            consulta_vehiculo,
            (
                id_cliente,
                marca,
                modelo,
                anio,
                kilometraje
            )
        )

        id_vehiculo = cursor.fetchone()[0]


        # ====================================================
        # 4. REGISTRAR SOLICITUD
        # ====================================================

        consulta_solicitud = """
            INSERT INTO solicitudes
            (
                id_cliente,
                id_vehiculo,
                id_servicio,
                descripcion_problema
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id_solicitud;
        """

        cursor.execute(
            consulta_solicitud,
            (
                id_cliente,
                id_vehiculo,
                id_servicio,
                descripcion_problema
            )
        )

        id_solicitud = cursor.fetchone()[0]


        # ====================================================
        # 5. CONFIRMAR TRANSACCIÓN
        # ====================================================

        conexion.commit()

        return (
            id_cliente,
            id_vehiculo,
            id_solicitud
        )


    except Exception as error:

        conexion.rollback()

        raise error


    finally:

        cursor.close()
        conexion.close()


# ============================================================
# LISTAR SOLICITUDES
# ============================================================

def f_listar_solicitudes():

    # conexion = f_conectar_local() # old
    conexion = f_conectar()

    cursor = conexion.cursor()

    consulta = """
        SELECT
            s.id_solicitud,
            s.fecha_solicitud,
            c.nombre,
            c.apellido_paterno,
            c.apellido_materno,
            c.correo,
            v.marca,
            v.modelo,
            v.anio,
            ser.nombre,
            ser.precio_base,
            s.estado
        FROM solicitudes s

        INNER JOIN clientes c
            ON s.id_cliente = c.id_cliente

        INNER JOIN vehiculos v
            ON s.id_vehiculo = v.id_vehiculo

        INNER JOIN servicios ser
            ON s.id_servicio = ser.id_servicio

        ORDER BY s.id_solicitud DESC;
    """

    cursor.execute(consulta)

    solicitudes = cursor.fetchall()

    cursor.close()
    conexion.close()

    return solicitudes


# ============================================================
# OBTENER UNA SOLICITUD
# ============================================================

def f_obtener_solicitud(id_solicitud):

    # conexion = f_conectar_local() # old
    conexion = f_conectar()

    cursor = conexion.cursor()

    consulta = """
        SELECT
            s.id_solicitud,
            s.fecha_solicitud,

            c.nombre,
            c.apellido_paterno,
            c.apellido_materno,
            c.correo,
            c.telefono,

            v.marca,
            v.modelo,
            v.anio,
            v.kilometraje,

            ser.id_servicio,
            ser.nombre,
            ser.descripcion,
            ser.precio_base,

            s.descripcion_problema,
            s.estado

        FROM solicitudes s

        INNER JOIN clientes c
            ON s.id_cliente = c.id_cliente

        INNER JOIN vehiculos v
            ON s.id_vehiculo = v.id_vehiculo

        INNER JOIN servicios ser
            ON s.id_servicio = ser.id_servicio

        WHERE s.id_solicitud = %s;
    """

    cursor.execute(
        consulta,
        (id_solicitud,)
    )

    solicitud = cursor.fetchone()

    cursor.close()
    conexion.close()

    return solicitud


# ============================================================
# OBTENER COTIZACIÓN POR SOLICITUD
# ============================================================

def f_obtener_cotizacion(id_solicitud):

    # conexion = f_conectar_local() # old
    conexion = f_conectar()

    cursor = conexion.cursor()

    consulta = """
        SELECT
            id_cotizacion,
            id_solicitud,
            subtotal,
            iva,
            total,
            fecha_cotizacion,
            estado
        FROM cotizaciones
        WHERE id_solicitud = %s;
    """

    cursor.execute(
        consulta,
        (id_solicitud,)
    )

    cotizacion = cursor.fetchone()

    cursor.close()
    conexion.close()

    return cotizacion


# ============================================================
# REGISTRAR COTIZACIÓN
# ============================================================

def f_registrar_cotizacion(
    id_solicitud,
    subtotal,
    iva,
    total
):

    # conexion = f_conectar_local() # old
    conexion = f_conectar()

    cursor = conexion.cursor()

    try:

        consulta = """
            INSERT INTO cotizaciones
            (
                id_solicitud,
                subtotal,
                iva,
                total,
                estado
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_cotizacion;
        """

        cursor.execute(
            consulta,
            (
                id_solicitud,
                subtotal,
                iva,
                total,
                "GENERADA"
            )
        )

        id_cotizacion = cursor.fetchone()[0]

        conexion.commit()

        return id_cotizacion


    except Exception as error:

        conexion.rollback()

        raise error


    finally:

        cursor.close()
        conexion.close()