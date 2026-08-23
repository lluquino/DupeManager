"""DupeManager — Email Notifications"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


async def send_email(
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
) -> dict:
    """
    Envía email vía SMTP.
    """
    if not all([smtp_host, username, password, to_email]):
        return {"success": False, "error": "Configuración de email incompleta"}
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = username
        msg["To"] = to_email
        
        # Versión texto plano
        msg.attach(MIMEText(body, "plain", "utf-8"))
        
        # Versión HTML (si se proporciona)
        if html_body:
            msg.attach(MIMEText(html_body, "html", "utf-8"))
        
        # Conectar y enviar
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        
        return {
            "success": True,
            "message": f"Email enviado a {to_email}",
        }
    except smtplib.SMTPAuthenticationError:
        return {"success": False, "error": "Error de autenticación SMTP"}
    except smtplib.SMTPConnectError:
        return {"success": False, "error": "Error de conexión SMTP"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def send_duplicate_email(
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
    to_email: str,
    duplicates_found: int,
    details: str = "",
) -> dict:
    """
    Envía email de notificación de duplicados.
    """
    subject = f"DupeManager: {duplicates_found} duplicados nuevos detectados"
    
    body = f"""DupeManager - Nuevos Duplicados Detectados

Se detectaron {duplicates_found} duplicados nuevos en tu servidor de Jellyfin.

{details}

---
Entra en DupeManager para revisar y gestionar los duplicados.
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0; }}
        .footer {{ text-align: center; padding: 10px; color: #64748b; font-size: 12px; }}
        .badge {{ background: #eab308; color: black; padding: 5px 10px; border-radius: 5px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 DupeManager</h1>
            <p>Nuevos duplicados detectados</p>
        </div>
        <div class="content">
            <p>Se detectaron <span class="badge">{duplicates_found}</span> duplicados nuevos.</p>
            {f'<p>{details}</p>' if details else ''}
            <p>Entra en DupeManager para revisar y gestionar los duplicados.</p>
        </div>
        <div class="footer">
            <p>DupeManager - Gestor de duplicados de Jellyfin</p>
        </div>
    </div>
</body>
</html>
"""
    
    return await send_email(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        username=username,
        password=password,
        to_email=to_email,
        subject=subject,
        body=body,
        html_body=html_body,
    )
