from datetime import datetime
from typing import List

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig


def get_parameters_email():
    # https://sabuhish.github.io/fastapi-mail/example/
    color = ''
    mail_name = ''
    mail_password = ''
    mail_server = ''
    mail_from = ''
    web = ''
    social_instagram = ''
    social_facebook = ''
    social_telegram = ''
    social_twitter = ''
    social_discord = ''
    social_youtube = ''
    social_spotify = ''
    social_whatsapp = ''
    web_admin = ''
    email_admin = ''

    return {
        'color': color,
        'mail_name': mail_name,
        'mail_password': mail_password,
        'mail_server': mail_server,
        'mail_from': mail_from,
        'web': web,
        'web_admin': web_admin,
        'email_admin': email_admin,
        'social_instagram': social_instagram,
        'social_facebook': social_facebook,
        'social_telegram': social_telegram,
        'social_twitter': social_twitter,
        'social_discord': social_discord,
        'social_youtube': social_youtube,
        'social_whatsapp': social_whatsapp,
        'social_spotify': social_spotify
    }


async def send_email(params_email: dict, subject: str, template: str, emails: List[str]):
    try:
        conf = ConnectionConfig(
            MAIL_USERNAME=params_email['mail_name'],
            MAIL_PASSWORD=params_email['mail_password'],
            MAIL_SERVER=params_email['mail_server'],
            MAIL_FROM=params_email['mail_from'],
            MAIL_FROM_NAME=params_email['mail_name'],
            MAIL_PORT=587,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
            MAIL_SSL_TLS=False,
            MAIL_STARTTLS=True
        )
        # if config.IS_DEVELOPMENT_ENVIROMENT:
        #     emails = [""]

        message = MessageSchema(
            subject=subject,
            recipients=emails,
            body=template,
            html=template,
            subtype="html"
        )
        fm = FastMail(conf)
        print(f"Se manda email a: {emails}")
        print(f"asunto del email: {subject}")
        await fm.send_message(message)
    except Exception as e:
        print(e)


def get_header_email(params_email: dict):
    return """
            <html>
                <body>
                <center>
                <table border="0" width="100%" style="max-width:800px;">
                <tr>
                <td style="color:#666666;font-family:Arial,sans-serif;font-size:16px;line-height:22px;padding-bottom:22px">
                    <p><img width="100%" src='""" + params_email['web'] + """earastellar/email_header.jpg'></p><br>
    """


def get_footer_email(params_email: dict, language: str):
    txt = """
            <br>
            <p style="text-align: center;"> """

    txt += """
            </p>
            <p style="text-align: center;font-size: 0.8rem;">""" + params_email['mail_name'] + """ © """ + str(datetime.today().year) + """</p>
            <hr style="border: 1px solid # 757575;">
            """

    if language == 'es':
        txt += """
                <p style="font-size: 0.8rem;">
                    Este email ha sido generado de manera automática, por favor no responda. Si tienes alguna duda contacta con nosotros. 
                    Visita nuestras Preguntas Frecuentes para resolver tus dudas.
                </p>
                """
    else:
        txt += """
                <p style="font-size: 0.8rem;">
                    This e-mail has been generated automatically, please do not reply. If you have any questions please contact us.
                    Visit our Frequently Asked Questions to solve your doubts.
                </p>
                <p><img width="100%" src='""" + params_email['web'] + """earastellar/email_header.jpg'></p><br><br>
            </td></tr></table>
            </center>
            </body>
            </html>
            """
    return txt


def format_number(number):
    # entra un float y sale un string formateado con . para los miles y , para los decimales
    number = float(number.replace(",", ".")) if isinstance(number, str) else number
    return "{:,.2f}".format(number).replace(",", "_").replace(".", ",").replace("_", ".")


async def send_email_user_recovery_pass(language: str,  email: str, new_pass: str):
    params_email = get_parameters_email()

    if language == 'es':
        subject = params_email['mail_name'] + " - Recupera tu contraseña ahora"
        template = get_header_email(params_email)
        template += """
                    <p>Hola,</p>
                    <p>Acabas de intentar recuperar tu contraseña.</p>
                    <p>Hemos creado una contraseña temporal que dura 24 horas.</p>
                    <p>Por favor, ve a la sección de "Mi cuenta" y cambia la contraseña. Si no la cambias en 24 horas, la contraseña temporal no funcionará y tendrás que volver a solicitar la recuperación de tu contraseña.</p>
                    <p style="text-align: center;">Contraseña:</p>
                    <p style="text-align: center;">""" + new_pass + """</p>
                    <br>
                    <p style="text-align: center;">       
                        <a href='""" + params_email['web'] + """login' target="_blank" style="
                        background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                        cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                        box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                        text-decoration: none;padding: 10px 20px;">Acceder con la nueva contraseña</a>      
                    </p>
                    <br>
                    <p>Agradecemos la confianza depositada en nosotros.</p>
                    <p>Equipo de """ + params_email['mail_name'] + """.</p>
                    """
        template += get_footer_email(params_email, language)
    else:
        subject = params_email['mail_name'] + " - Recover your password now"
        template = get_header_email(params_email)
        template += """
                    <p>Hello,</p>
                    <p>You have just attempted to recover your password.</p>
                    <p>We have created a temporary password that is valid for 24 hours.</p>
                    <p>Please go to "My Account" section and change your password. If you don't change it within 24 hours, the temporary password will expire, and you will need to request password recovery again.</p>
                    <p style="text-align: center;">Password:</p>
                    <p style="text-align: center;">""" + new_pass + """</p>
                    <br>
                    <p style="text-align: center;">       
                        <a href='""" + params_email['web'] + """login' target="_blank" style="
                        background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                        cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                        box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                        text-decoration: none;padding: 10px 20px;">Access with the new password</a>      
                    </p>
                    <br>
                    <p>Thank you for your trust and confidence in us.</p>
                    <p>""" + params_email['mail_name'] + """'s team.</p>
                    """
        template += get_footer_email(params_email, language)

    await send_email(params_email, subject, template, [email])


async def send_email_kyc_ok(language: str,  email: str):
    params_email = get_parameters_email()

    if language == 'es':
        subject = params_email['mail_name'] + " - Proceso de identificación aceptado"
        template = get_header_email(params_email)
        template += """
                    <p>Hola,</p>
                    <p>Muchas gracias por realizar el proceso de identificación en nuestro ecosistema. Ya hemos verificado los datos y la documentación adjunta, por lo que ya puedes empezar a invertir en nuestros proyectos.</p>
                    <br>
                    <p style="text-align: center;">       
                        <a href='""" + params_email['web'] + """userDetail' target="_blank" style="
                        background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                        cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                        box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                        text-decoration: none;padding: 10px 20px;">Dashboard</a>      
                    </p>
                    <br>
                    <p>Agradecemos la confianza depositada en nosotros.</p>
                    <p>Equipo de """ + params_email['mail_name'] + """.</p>
                    """
        template += get_footer_email(params_email, language)
    else:
        subject = params_email['mail_name'] + " - Identification process accepted"
        template = get_header_email(params_email)
        template += """
                    <p>Hello,</p>
                    <p>Thank you very much for completing the identification process in our ecosystem. We have now verified the data and attached documentation, so you can start investing in our projects.</p>
                    <br>
                    <p style="text-align: center;">       
                        <a href='""" + params_email['web'] + """userDetail' target="_blank" style="
                        background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                        cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                        box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                        text-decoration: none;padding: 10px 20px;">Dashboard</a>      
                    </p>
                    <br>
                    <p>Thank you for your trust and confidence in us.</p>
                    <p>""" + params_email['mail_name'] + """'s team.</p>
                    """
        template += get_footer_email(params_email, language)

    await send_email(params_email, subject, template, [email])


async def send_email_kyc_ko(language: str,  email: str):
    params_email = get_parameters_email()

    if language == 'es':
        subject = params_email['mail_name'] + " - Proceso de identificación rechazado"
        template = get_header_email(params_email)
        template += """
                    <p>Hola,</p>
                    <p>Muchas gracias por realizar el proceso de identificación en nuestro ecosistema. Hemos revisado los datos y la documentación adjunta y hemos encontrado algunos problemas. Por favor  revisa el proceso de identificación para solucionar los problemas indicados.</p>
                    <br>
                    <p style="text-align: center;">       
                        <a href='""" + params_email['web'] + """userKYC' target="_blank" style="
                        background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                        cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                        box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                        text-decoration: none;padding: 10px 20px;">Proceso de identificación </a>      
                    </p>
                    <br>
                    <p>Agradecemos la confianza depositada en nosotros.</p>
                    <p>Equipo de """ + params_email['mail_name'] + """.</p>
                    """
        template += get_footer_email(params_email, language)
    else:
        subject = params_email['mail_name'] + " - Identification process rejected"
        template = get_header_email(params_email)
        template += """
                    <p>Hello,</p>
                    <p>Thank you for completing the identification process in our ecosystem. We have reviewed the data and attached documentation and have identified some issues. Please review the identification process to address the indicated problems.</p>
                    <br>
                    <p style="text-align: center;">       
                        <a href='""" + params_email['web'] + """userKYC' target="_blank" style="
                        background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                        cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                        box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                        text-decoration: none;padding: 10px 20px;">Identification Process</a>      
                    </p>
                    <br>
                    <p>Thank you for your trust and confidence in us.</p>
                    <p>""" + params_email['mail_name'] + """'s team.</p>
                    """
        template += get_footer_email(params_email, language)

    await send_email(params_email, subject, template, [email])



async def send_email_access_white_list(language: str,  email: str, project_name: str, project_slug: str, value_to_invest: str):
    params_email = get_parameters_email()

    if language == 'es':
        template = get_header_email(params_email)
        value_to_invest = format_number(value_to_invest)

        subject = params_email['mail_name'] + " - Solicitud de acceso a Whitelist - Proyecto " + project_name
        template += """
                    <p>Hola,</p>
                    <p>Has solicitado acceder a la Whitelist del proyecto """ + project_name + """ y has indicado que estás interesado en invertir """ + value_to_invest + """€. Te notificaremos en cuanto revisemos tu solicitud indicándote la fase de venta en la que has sido aceptado.</p>
                    """
        template += """
                    <br>
                    <p style="text-align: center;">            
                    <a href='""" + params_email['web'] + """invest/""" + project_slug + """' target="_blank" style=" background-color: """ + params_email['color'] + """; border-color: """ + \
                    params_email['color'] + """; border-radius: 25px!important; cursor: pointer; border:0; font-weight: 500;letter-spacing: .02rem;font-family:'Arial,sans-serif';
                    box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                    text-decoration: none;padding: 10px 20px;">""" + project_name + """</a>
                    </p>
                    <br>
                    <p>Agradecemos la confianza depositada en nosotros.</p>
                    <p>Equipo de """ + params_email['mail_name'] + """.</p>
                    """
        template += get_footer_email(params_email, language)
    else:
        subject = params_email['mail_name'] + " - Whitelist access request - Project " + project_name
        template = get_header_email(params_email)
        template += """
                    <p>Hello,</p>
                    <p>You have requested access to the """ + project_name + """ project's Whitelist and you have indicated that you are interested in investing """ + value_to_invest + """€. We will notify you as soon as we review your request, indicating the sales phase in which you have been accepted.</p>
                    <br>
                    <p style="text-align: center;">             
                    <a href='""" + params_email['web'] + """invest/""" + project_slug + """' target="_blank" style=" background-color: """ + params_email['color'] + """; border-color: """ + \
                    params_email['color'] + """; border-radius: 25px!important; cursor: pointer; border:0; font-weight: 500;letter-spacing: .02rem;font-family:'Arial,sans-serif';
                    box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                    text-decoration: none;padding: 10px 20px;">""" + project_name + """</a>
                    </p>
                    <br>
                    <p>Thank you for your trust and confidence in us.</p>
                    <p>""" + params_email['mail_name'] + """'s team.</p>
                    """
        template += get_footer_email(params_email, language)

    await send_email(params_email, subject, template, [email])


async def send_email_access_white_list_ok(language: str,  email: str, project_name: str, project_slug: str, phase: str):
    try:
        params_email = get_parameters_email()

        if language == 'es':
            subject = params_email['mail_name'] + " - Solicitud de acceso a fase " + phase + " aceptada - Proyecto " + project_name
            template = get_header_email(params_email)
            template += """
                        <p>Hola,</p>
                        <p>has solicitado acceder a la Whitelist del proyecto """ + project_name + """.</p>
                        <p>Hemos revisado tu solicitud y has sido aceptado para comprar tokens en la fase """ + phase + """. Para ello, solo tienes que pulsar en el siguiente enlace.</p>
                        <br>
                        <p style="text-align: center;">             
                        <a href='""" + params_email['web'] + """invest/""" + project_slug + """' target="_blank" style=" background-color: """ + params_email['color'] + """; border-color: """ + \
                        params_email['color'] + """; border-radius: 25px!important; cursor: pointer; border:0; font-weight: 500;letter-spacing: .02rem;font-family:'Arial,sans-serif';
                        box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                        text-decoration: none;padding: 10px 20px;">""" + project_name + """</a>
                        </p>
                        <br>
                        <p>Agradecemos la confianza depositada en nosotros.</p>
                        <p>Equipo de """ + params_email['mail_name'] + """.</p>
                        """
            template += get_footer_email(params_email, language)
        else:
            subject = params_email['mail_name'] + " - Request for access to " + phase + " phase accepted - Project " + project_name
            template = get_header_email(params_email)
            template += """
                        <p>Hello,</p>
                        <p>You have requested access to the Whitelist of the """ + project_name + """ project.</p>
                        <p>We have reviewed your request, and we are pleased to inform you that you have been accepted to purchase tokens in the """ + phase + """ phase. To proceed, simply click on the following link.</p>
                        <br>
                        <p style="text-align: center;">             
                        <a href='""" + params_email['web'] + """invest/""" + project_slug + """' target="_blank" style=" background-color: """ + params_email['color'] + """; border-color: """ + \
                        params_email['color'] + """; border-radius: 25px!important; cursor: pointer; border:0; font-weight: 500;letter-spacing: .02rem;font-family:'Arial,sans-serif';
                        box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                        text-decoration: none;padding: 10px 20px;">""" + project_name + """</a>
                        </p>
                        <br>
                        <p>Thank you for your trust and confidence in us.</p>
                        <p>""" + params_email['mail_name'] + """'s team.</p>
                        """
            template += get_footer_email(params_email, language)

        await send_email(params_email, subject, template, [email])

    except Exception as e:
        print(e)


async def send_email_project_completed(language: str,  email: str, project_name: str, project_slug: str):
    params_email = get_parameters_email()
    # email cuando el proyecto pasa a ser un proyecto completado, se acaba
    # solo para los que han invertido

    if language == 'es':
        subject = params_email['mail_name'] + " - Proyecto finalizado - Proyecto " + project_name
        template = get_header_email(params_email)
        template += """
                    <p>Hola,</p>
                    <p>Nos ponemos en contacto contigo para informar sobre la finalización del proyecto """ + project_name + """.</p>
                    <br>
                    <p style="text-align: center;">             
                    <a href='""" + params_email['web'] + """invest/""" + project_slug + """' target="_blank" style=" background-color: """ + params_email['color'] + """; border-color: """ + \
                    params_email['color'] + """; border-radius: 25px!important; cursor: pointer; border:0; font-weight: 500;letter-spacing: .02rem;font-family:'Arial,sans-serif';
                    box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                    text-decoration: none;padding: 10px 20px;">""" + project_name + """</a>
                    </p>
                    <br>
                    <p>Agradecemos la confianza depositada en nosotros.</p>
                    <p>Equipo de """ + params_email['mail_name'] + """.</p>
                    """
        template += get_footer_email(params_email, language)
    else:
        subject = params_email['mail_name'] + " - Funding phase completed - Project " + project_name
        template = get_header_email(params_email)
        template += """
                    <p>Hola,</p>
                    <p>We are reaching out to inform you that the """ + project_name + """ project has been completed.</p>
                    <br>
                    <p style="text-align: center;">             
                    <a href='""" + params_email['web'] + """invest/""" + project_slug + """' target="_blank" style=" background-color: """ + params_email['color'] + """; border-color: """ + \
                    params_email['color'] + """; border-radius: 25px!important; cursor: pointer; border:0; font-weight: 500;letter-spacing: .02rem;font-family:'Arial,sans-serif';
                    box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                    text-decoration: none;padding: 10px 20px;">""" + project_name + """</a>
                    </p>
                    <br>
                    <p>Thank you for your trust and confidence in us.</p>
                    <p>""" + params_email['mail_name'] + """'s team.</p>
                    """
        template += get_footer_email(params_email, language)

    await send_email(params_email, subject, template, [email])


async def send_email_profit_distribution(language: str,  email: str, project_name: str, project_slug: str):
    params_email = get_parameters_email()
    # email cuando se reparten beneficios del proyecto
    # solo para los que han invertido y obtienen beneficio

    if language == 'es':
        subject = params_email['mail_name'] + " - Reparto de beneficios - Proyecto " + project_name
        template = get_header_email(params_email)
        template += """
                    <p>Hola,</p>
                    <p>Nos ponemos en contacto contigo para informar sobre el reparto de beneficios del proyecto """ + project_name + """.</p>
                    <br>
                    <p style="text-align: center;">       
                        <a href='""" + params_email['web'] + """portfolio' target="_blank" style="
                        background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                        cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                        box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                        text-decoration: none;padding: 10px 20px;">Portfolio</a>      
                    </p>
                    <br>
                    <p>Agradecemos la confianza depositada en nosotros.</p>
                    <p>Equipo de """ + params_email['mail_name'] + """.</p>
                    """
        template += get_footer_email(params_email, language)
    else:
        subject = params_email['mail_name'] + " - Profit Distribution - Project " + project_name
        template = get_header_email(params_email)
        template += """
                    <p>Hola,</p>
                    <p>We are reaching out to inform you about the profit distribution of the """ + project_name + """ project. Please access the portfolio section if you wish to claim the profits to your personal account.</p>
                    <br>
                    <p style="text-align: center;">       
                        <a href='""" + params_email['web'] + """portfolio' target="_blank" style="
                        background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                        cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                        box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                        text-decoration: none;padding: 10px 20px;">Portfolio</a>      
                    </p>
                    <br>
                    <p>Thank you for your trust and confidence in us.</p>
                    <p>""" + params_email['mail_name'] + """'s team.</p>
                    """
        template += get_footer_email(params_email, language)

    await send_email(params_email, subject, template, [email])


async def send_email_profit_claim(language: str,  email: str, value: str):
    params_email = get_parameters_email()
    # email cuando el usuario reclama beneficios/fondos

    if language == 'es':
        subject = params_email['mail_name'] + " - Reclamación de fondos realizada"
        template = get_header_email(params_email)
        template += """
                    <p>Hola,</p>
                    <p>Has reclamado la retirada de un total de """ + value + """€ a tu cuenta bancaria personal. Recibirás los fondos en un período entre 24 y 72 horas.</p>
                    <br>
                    <p>Agradecemos la confianza depositada en nosotros.</p>
                    <p>Equipo de """ + params_email['mail_name'] + """.</p>
                    """
        template += get_footer_email(params_email, language)
    else:
        subject = params_email['mail_name'] + " - Funds Withdrawal Claimed"
        template = get_header_email(params_email)
        template += """
                    <p>Hola,</p>
                    <p>You have claimed a withdrawal of a total of """ + value + """€  to your personal bank account. You will receive the funds within a period of 24 to 72 hours.</p>
                    <br>
                    <p>Thank you for your trust and confidence in us.</p>
                    <p>""" + params_email['mail_name'] + """'s team.</p>
                    """
        template += get_footer_email(params_email, language)

    await send_email(params_email, subject, template, [email])



async def send_email_buy_fiat_without_verified_ok(language: str,  email: str, project_name: str, token_number: str, token_value: str, symbol_fiat: str):
    params_email = get_parameters_email()
    token_value = format_number(token_value)
    # compra realizada con exito

    if language == 'es':
        template = get_header_email(params_email)

        subject = params_email['mail_name'] + " - Compra de tokens realizada con éxito - Proyecto " + project_name
        template += """
                    <p>Hola,</p>
                    <p>Has comprado """ + token_number + """ tokens con un valor de """ + token_value + """ """ + symbol_fiat + """ del proyecto """ + project_name + """.</p>
                    <p>Puedes ver los detalles de tu inversión en la sección de portfolio. Cuando termine la fase de financiación recibirás una notificación.</p>
                    <br>
                    <p style="text-align: center;">       
                        <a href='""" + params_email['web'] + """portfolio' target="_blank" style="
                        background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                        cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                        box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                        text-decoration: none;padding: 10px 20px;">Portfolio</a>      
                    </p>
                    """
        template += """
                    <br>
                    <p>Agradecemos la confianza depositada en nosotros.</p>
                    <p>Equipo de """ + params_email['mail_name'] + """.</p>
                    """
        template += get_footer_email(params_email, language)
    else:
        subject = params_email['mail_name'] + " - Token Purchase Successful - Project " + project_name
        template = get_header_email(params_email)
        template += """
                    <p>Hello,</p>
                    <p>You have successfully purchased """ + token_number + """ tokens with a value of """ + token_value + """ """ + symbol_fiat + """ from the """ + project_name + """ project.</p>
                    <p>You can view the details of your investment in the portfolio section. You will receive a notification when the funding phase is completed.</p>
                    <br>
                    <p style="text-align: center;">       
                        <a href='""" + params_email['web'] + """portfolio' target="_blank" style="
                        background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                        cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                        box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                        text-decoration: none;padding: 10px 20px;">Portfolio</a>      
                    </p>
                    <br>
                    <p>Thank you for your trust and confidence in us.</p>
                    <p>""" + params_email['mail_name'] + """'s team.</p>
                    """
        template += get_footer_email(params_email, language)

    await send_email(params_email, subject, template, [email])


async def send_email_deploy_contract( email: str, project_name: str):
    params_email = get_parameters_email()

    subject = params_email['mail_name'] + " -  Petición para desplegar proyecto - Proyecto " + project_name
    template = get_header_email(params_email)
    template += f"""
                <p>Hola,</p>
                <p>Un cliente ha solicitado desplegar el contrato del proyecto {project_name}</p>
                <p>Para desplegar el contrato del proyecto {project_name} abre sessión ssh en el servidor.</p>
                <p>Una vez dentro del servidor ve al directorio: <b>cd /var/www/api.desa.lunarxy.com</b></p>
                <p>Y ejecuta el comando:</p> 
                <p><b>venv/bin/python -m  blockchain.deploy_token_automation<b></p>

                """
    template += get_footer_email(params_email, "es")

    await send_email(params_email, subject, template, [email])


async def send_email_NO_deploy_contract( email: str, project_name: str):
    params_email = get_parameters_email()

    subject = params_email['mail_name'] + " -  Petición para NO desplegar proyecto - Proyecto " + project_name
    template = get_header_email(params_email)
    template += f"""
                <p>Hola,</p>
                <p>Un cliente ha solicitado NO desplegar el contrato del proyecto {project_name}</p>
                <p>Así que si has ido a deplegar es posible que el proceso no haya hecho nada. Es normal.</p>

                """
    template += get_footer_email(params_email, "es")

    await send_email(params_email, subject, template, [email])

