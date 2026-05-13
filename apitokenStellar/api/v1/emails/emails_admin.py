from api.v1.emails.emails import get_parameters_email, get_header_email, get_footer_email, send_email, format_number


async def admin_send_email_new_user( email: str):
    params_email = get_parameters_email()

    subject = "Registro realizado en la plataforma"
    template = get_header_email(params_email)
    template += """
                <p>El usuario """ + email + """ acaba de registrarse en la plataforma.</p>                   
                <br>
                <p>Agradecemos la confianza depositada en nosotros.</p>
                <p>Equipo de """ + params_email['mail_name'] + """.</p>
                """
    template += get_footer_email(params_email, 'es')

    await send_email(params_email, subject, template, [params_email['email_admin']])


async def admin_send_email_user_modify_kyc( email: str, user_id: int):
    params_email = get_parameters_email()

    subject = "Proceso de identificación (KYC) realizado - Pendiente de verificación "
    template = get_header_email(params_email)
    template += """
                <p>El usuario """ + email + """ acaba de realizar el proceso de identificación y está pendiente de verificación.</p>              
                <br>
                <p style="text-align: center;">             
                    <a href='""" + params_email['web'] + """UserDetail/""" + str(user_id) + """' target="_blank" style="
                    background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                    cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                    box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                    text-decoration: none;padding: 10px 20px;">Ver información usuario</a>
                </p>     
                <br>
                <p>Agradecemos la confianza depositada en nosotros.</p>
                <p>Equipo de """ + params_email['mail_name'] + """.</p>
                """
    template += get_footer_email(params_email, 'es')

    await send_email(params_email, subject, template, [params_email['email_admin']])


async def admin_send_email_user_whitelist( email: str, invest_id: int, project_name: str, value_to_invest: str):
    params_email = get_parameters_email()
    value_to_invest = format_number(value_to_invest)

    subject = "Solicitud de acceso a Whitelist - Proyecto " + project_name
    template = get_header_email(params_email)
    template += """
                <p>El usuario """ + email + """ acaba de solicitar acceso para acceder a la Whitelist del proyecto 
                """ + project_name + """ y ha indicado que está interesado en invertir """ + value_to_invest + """€.</p>        
                <br>
                <p style="text-align: center;">             
                    <a href='""" + params_email['web'] + """InvestProjects/""" + str(invest_id) + """' target="_blank" style="
                    background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                    cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                    box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                    text-decoration: none;padding: 10px 20px;">Ver usuarios en Whitelist</a>
                </p>                  
                <br>
                <p>Agradecemos la confianza depositada en nosotros.</p>
                <p>Equipo de """ + params_email['mail_name'] + """.</p>
                """
    template += get_footer_email(params_email, 'es')

    await send_email(params_email, subject, template, [params_email['email_admin']])


async def admin_send_email_user_buy_transfer( email: str, invest_id: int, project_name: str, num_tokens: str):
    params_email = get_parameters_email()
    num_tokens = format_number(num_tokens)

    subject = "Proceso de compra de tokens con transferencia bancaria iniciado - Proyecto " + project_name
    template = get_header_email(params_email)
    template += """
                <p>El usuario """ + email + """ acaba de realizar el proceso de compra de """ + num_tokens + """ tokens del proyecto """ + project_name + """ 
                con transferencia bancaria. Revisa que coincide el importe de los tokens seleccionados con el importe del justificante de pago.</p>        
                <br>
                <p style="text-align: center;">             
                    <a href='""" + params_email['web'] + """InvestProjects/""" + str(invest_id) + """' target="_blank" style="
                    background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                    cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                    box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                    text-decoration: none;padding: 10px 20px;">Ver transacción</a>
                </p>                  
                <br>
                <p>Agradecemos la confianza depositada en nosotros.</p>
                <p>Equipo de """ + params_email['mail_name'] + """.</p>
                """
    template += get_footer_email(params_email, 'es')

    await send_email(params_email, subject, template, [params_email['email_admin']])


async def admin_send_email_user_buy_crypto( email: str, invest_id: int, project_name: str, num_tokens: str):
    params_email = get_parameters_email()
    num_tokens = format_number(num_tokens)

    subject = "Proceso de compra de tokens con pago crypto realizada - Proyecto " + project_name
    template = get_header_email(params_email)
    template += """
                <p>El usuario """ + email + """ acaba de realizar el proceso de compra de """ + num_tokens + """ tokens del proyecto """ + project_name + """ 
                con pago crypto. Esta transacción es automática, por lo que se ha validado en el mismo momento.</p>        
                <br>
                <p style="text-align: center;">             
                    <a href='""" + params_email['web'] + """InvestProjects/""" + str(invest_id) + """' target="_blank" style="
                    background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                    cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                    box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                    text-decoration: none;padding: 10px 20px;">Ver transacción</a>
                </p>                  
                <br>
                <p>Agradecemos la confianza depositada en nosotros.</p>
                <p>Equipo de """ + params_email['mail_name'] + """.</p>
                """
    template += get_footer_email(params_email, 'es')

    await send_email(params_email, subject, template, [params_email['email_admin']])


async def admin_send_email_ticket( email: str, ticket_id: str):
    params_email = get_parameters_email()

    subject = "Soporte - Ticket " + ticket_id
    template = get_header_email(params_email)
    template += """
                <p>Hemos recibido un nuevo mensaje del usuario """ + email + """ en soporte. Para verlo, pulsa el siguiente enlace.</p>        
                <br>
                <p style="text-align: center;">             
                    <a href='""" + params_email['web'] + """userTicketsList' target="_blank" style="
                    background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                    cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                    box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                    text-decoration: none;padding: 10px 20px;">Soporte</a>
                </p>                  
                <br>
                <p>Agradecemos la confianza depositada en nosotros.</p>
                <p>Equipo de """ + params_email['mail_name'] + """.</p>
                """
    template += get_footer_email(params_email, 'es')

    await send_email(params_email, subject, template, [params_email['email_admin']])


async def admin_send_email_project_on_funding_before( project_id: int, project_name: str, phase_name: str):
    params_email = get_parameters_email()

    subject = "Próximo lanzamiento de la fase " + phase_name + " de financiación - Proyecto " + project_name
    template = get_header_email(params_email)
    template += """
                <p>El proyecto """ + project_name + """ iniciará la fase """ + phase_name + """ de financiación en menos de una hora.</p>        
                <br>
                <p style="text-align: center;">             
                    <a href='""" + params_email['web'] + """InvestProjects/""" + str(project_id) + """' target="_blank" style="
                    background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                    cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                    box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                    text-decoration: none;padding: 10px 20px;">Ver proyecto</a>
                </p>                  
                <br>
                <p>Agradecemos la confianza depositada en nosotros.</p>
                <p>Equipo de """ + params_email['mail_name'] + """.</p>
                """
    template += get_footer_email(params_email, 'es')

    await send_email(params_email, subject, template, [params_email['email_admin']])


async def admin_send_email_project_on_funding( project_id: int, project_name: str, phase_name: str):
    params_email = get_parameters_email()

    subject = "Lanzamiento fase " + phase_name + " de financiación - Proyecto " + project_name
    template = get_header_email(params_email)
    template += """
                <p>El proyecto """ + project_name + """ acaba de iniciar la fase """ + phase_name + """ de financiación.</p>        
                <br>
                <p style="text-align: center;">             
                    <a href='""" + params_email['web'] + """InvestProjects/""" + str(project_id) + """' target="_blank" style="
                    background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                    cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                    box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                    text-decoration: none;padding: 10px 20px;">Ver proyecto</a>
                </p>                  
                <br>
                <p>Agradecemos la confianza depositada en nosotros.</p>
                <p>Equipo de """ + params_email['mail_name'] + """.</p>
                """
    template += get_footer_email(params_email, 'es')

    await send_email(params_email, subject, template, [params_email['email_admin']])


async def admin_send_email_project_in_course( project_id: int, project_name: str, phase_name: str):
    params_email = get_parameters_email()

    subject = "Fase " + phase_name + " de financiación completada - Proyecto " + project_name
    template = get_header_email(params_email)
    template += """
                <p>El proyecto """ + project_name + """ acaba de cerrar la fase """ + phase_name + """ de financiación.</p>        
                <br>
                <p style="text-align: center;">             
                    <a href='""" + params_email['web'] + """InvestProjects/""" + str(project_id) + """' target="_blank" style="
                    background-color: """ + params_email['color'] + """; border-color: """ + params_email['color'] + """; border-radius: 25px!important; 
                    cursor: pointer; border:0; font-weight: 500; letter-spacing: .02rem;font-family:'Arial,sans-serif';
                    box-shadow: 0 4px 8px -4px rgba(94,86,105,.42)!important;font-size: 100%;line-height: 1.15;margin: 0;color: #fff; 
                    text-decoration: none;padding: 10px 20px;">Ver proyecto</a>
                </p>                  
                <br>
                <p>Agradecemos la confianza depositada en nosotros.</p>
                <p>Equipo de """ + params_email['mail_name'] + """.</p>
                """
    template += get_footer_email(params_email, 'es')

    await send_email(params_email, subject, template, [params_email['email_admin']])
