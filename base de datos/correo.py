import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuracion SMTP por variables de entorno -- nunca hardcodees credenciales
# de correo en el codigo. Ejemplo para Gmail: SMTP_HOST=smtp.gmail.com,
# SMTP_PORT=587, SMTP_USER=tu_correo@gmail.com, SMTP_PASSWORD=contraseña de aplicacion.
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", SMTP_USER)
EMAIL_FROM_NOMBRE = os.environ.get("EMAIL_FROM_NOMBRE", "Panama Express")

# Solo estos 3 estados generan una notificacion por correo, tal como se pidio:
# cuando llega a bodega, cuando esta en camino, y cuando llega al casillero.
PLANTILLAS_ESTADO = {
    "recibido en bodega": {
        "asunto": "Tu paquete {tracking} llego a nuestra bodega en Miami",
        "titulo": "Paquete recibido en bodega",
        "cuerpo": (
            "Recibimos tu paquete <b>{tracking}</b> en la bodega de Miami. "
            "En cuanto salga hacia Panama te avisamos."
        ),
    },
    "en transito": {
        "asunto": "Tu paquete {tracking} ya va en camino",
        "titulo": "Paquete en transito",
        "cuerpo": (
            "Tu paquete <b>{tracking}</b> ya salio de la bodega y va en "
            "camino a Panama. Te avisamos cuando llegue a tu casillero."
        ),
    },
    "listo para retiro": {
        "asunto": "Tu paquete {tracking} ya esta listo para retirar",
        "titulo": "Paquete listo para retiro",
        "cuerpo": (
            "Tu paquete <b>{tracking}</b> llego a tu casillero y ya esta "
            "listo para que lo retires."
        ),
    },
}

ESTADOS_NOTIFICABLES = set(PLANTILLAS_ESTADO.keys())


def _config_incompleta():
    return not (SMTP_USER and SMTP_PASSWORD and EMAIL_FROM)


def _construir_html(cliente_nombre, tracking, plantilla):
    return f"""
    <div style="font-family: Arial, sans-serif; background:#12151A; padding:24px;">
      <div style="max-width:480px; margin:0 auto; background:#1A1F26; border:1px solid #2A313B; border-radius:4px; padding:28px; color:#EDEFF2;">
        <p style="font-size:11px; letter-spacing:0.1em; text-transform:uppercase; color:#F2A93B; margin:0 0 12px;">Panama Express</p>
        <h2 style="margin:0 0 16px; font-size:20px;">{plantilla['titulo']}</h2>
        <p style="margin:0 0 8px; color:#8891A0;">Hola {cliente_nombre},</p>
        <p style="line-height:1.6; color:#EDEFF2;">{plantilla['cuerpo'].format(tracking=tracking)}</p>
        <p style="margin-top:24px; font-family:monospace; font-size:12px; color:#565F6C;">Tracking: {tracking}</p>
      </div>
    </div>
    """


def notificar_cambio_estado(cliente_nombre, cliente_correo, tracking, estado):
    """
    Envia un correo al cliente si `estado` es uno de los que se notifican
    (recibido en bodega, en transito, listo para retiro).

    Devuelve (enviado: bool, mensaje: str). Nunca lanza una excepcion hacia
    afuera -- un fallo de correo no debe tumbar el ETL ni la edicion manual
    de un paquete, solo se reporta como mensaje.
    """
    if estado not in ESTADOS_NOTIFICABLES:
        return False, f"El estado '{estado}' no genera notificacion por correo"

    if not cliente_correo:
        return False, "El cliente no tiene un correo registrado"

    if _config_incompleta():
        return False, "Configuracion SMTP incompleta (definir SMTP_USER / SMTP_PASSWORD)"

    plantilla = PLANTILLAS_ESTADO[estado]

    mensaje = MIMEMultipart("alternative")
    mensaje["Subject"] = plantilla["asunto"].format(tracking=tracking)
    mensaje["From"] = f"{EMAIL_FROM_NOMBRE} <{EMAIL_FROM}>"
    mensaje["To"] = cliente_correo

    texto_plano = (
        f"Hola {cliente_nombre}, tu paquete {tracking} cambio de estado a: {estado}."
    )
    html = _construir_html(cliente_nombre, tracking, plantilla)

    mensaje.attach(MIMEText(texto_plano, "plain"))
    mensaje.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as servidor:
            servidor.starttls()
            servidor.login(SMTP_USER, SMTP_PASSWORD)
            servidor.sendmail(EMAIL_FROM, [cliente_correo], mensaje.as_string())
        return True, f"Correo enviado a {cliente_correo}"
    except Exception as e:
        return False, f"No se pudo enviar el correo: {e}"
