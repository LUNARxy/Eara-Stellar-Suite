<template>
  <Menu/>
  <div class="content_menu">

    <form id="form" @submit.prevent="save">
      <div class="row">

        <div class="col s12 padding-0 mb-3 text-center">
          <h4 class="col s12 text-center">{{ $t('views.Nuevo usuario') }}</h4>
          <div v-if="loading" class="progress mt-5 mb-5">
            <div class="indeterminate"></div>
          </div>
        </div>


        <div class="col s12">
          <div class="col s12 p-0 m-0">



            <div id="tab_personal_data" class="col s12 padding-0 padding-0" style="display: block">
              <div class="card padding-7 pt-2 pb-2 mt-0">
                <fieldset class="w100" >
                  <div class="row">
                    <div class="col s12 text-center">
                      <h5>{{ $t('views.Datos personales') }}</h5>
                    </div>
                  </div>
                  <div class="row">
                    <div class="input-field col s12 m6">
                      <input id="email" v-model="data_item.email" type="email"  maxlength="100" required>
                      <label for="email" class="active"><span class="required">*</span> {{ $t('views.Email') }}</label>
                    </div>
                    <div class="input-field col s12 m6">
                      <input id="password" v-model="data_item.password" type="password"  maxlength="200" minlength="8" required>
                      <label for="password" class="active"><span class="required">*</span> {{ $t('views.Contraseña') }}</label>
                    </div>
                    <div class="input-field col s12 m6">
                      <label for="user_type" class="active active_select">{{ $t('views.Tipo de usuario') }}</label>
                      <select class="browser-default" id="user_type" v-model="data_item.user_type" @change="changeUserType">
                        <option value="0">{{ $t('views.Persona física') }}</option>
                        <option value="1">{{ $t('views.Persona jurídica (empresa)') }}</option>
                      </select>
                    </div>
                  </div>

                  <div id="show_data_legal_person" style="display: none">
                    <div class="col s12 text-center">
                      <h5 class="mb-5">{{ $t('views.Datos de la persona jurídica (empresa)') }}</h5>
                    </div>
                    <div class="row">
                      <div class="input-field col s12 m8">
                        <input id="company_name" v-model="data_item.company_name" type="text"  maxlength="200">
                        <label for="company_name" class="active">{{ $t('views.Nombre de la empresa') }}</label>
                      </div>
                      <div class="input-field col s12 m4">
                        <input id="register_number" v-model="data_item.register_number" type="text"  maxlength="100">
                        <label for="register_number" class="active">{{ $t('views.Nº de registro') }}</label>
                      </div>
                      <div class="input-field col s12 m4">
                        <input id="nif" v-model="data_item.nif" type="text"  maxlength="100">
                        <label for="nif" class="active">{{ $t('views.NIF') }}</label>
                      </div>
                      <div class="input-field col s12 m8">
                        <label for="legal_form" class="active active_select">{{ $t('views.Forma jurídica') }}</label>
                        <select class="browser-default" id="legal_form" v-model="data_item.legal_form">
                          <option value="" disabled selected></option>
                          <option value="0">{{ $t('views.Autónomo') }}</option>
                          <option value="1">{{ $t('views.Sociedad Limitada') }}</option>
                          <option value="2">{{ $t('views.Sociedad Anónima') }}</option>
                          <option value="3">{{ $t('views.Cooperativa') }}</option>
                          <option value="4">{{ $t('views.Sociedad civil') }}</option>
                          <option value="5">{{ $t('views.Comunidad de bienes') }}</option>
                          <option value="6">{{ $t('views.Otras') }}</option>
                        </select>
                      </div>
                    </div>
                    <div class="row">

                      <div class="input-field col s12 m6">
                        <input id="activity" v-model="data_item.activity" type="text"  maxlength="100">
                        <label for="activity" class="active">{{ $t('views.Actividad de la empresa') }}</label>
                      </div>

                      <div class="input-field col s12 m6">
                        <input id="holders" v-model="data_item.holders" type="text" @change="changeHolders" maxlength="1">
                        <label for="holders" class="active">{{ $t('views.Beneficiarios') }}</label>
                      </div>

                      <div class="input-field col s12 m9">
                        <input id="company_address" name="company_address" v-model="data_item.company_address" type="text"  maxlength="200">
                        <label for="company_address" class="active">{{ $t('views.Dirección') }}</label>
                      </div>
                      <div class="input-field col s12 m3">
                        <input id="company_postal_code" v-model="data_item.company_postal_code" type="text"  maxlength="100">
                        <label for="company_postal_code" class="active">{{ $t('views.Código postal') }}</label>
                      </div>
                      <div class="input-field col s12 m4">
                        <input id="company_city" v-model="data_item.company_city" type="text"  maxlength="100">
                        <label for="company_city" class="active">{{ $t('views.Ciudad') }}</label>
                      </div>
                      <div class="input-field col s12 m4">
                        <input id="company_province" v-model="data_item.company_province" type="text"  maxlength="100">
                        <label for="company_province" class="active">{{ $t('views.Provincia') }}</label>
                      </div>
                      <div class="input-field col s12 m4">
                        <label for="company_country" class="active active_select">{{ $t('views.Elige un país') }}</label>
                        <select class="browser-default" id="company_country" v-model="data_item.company_country">
                          <option value="" disabled selected></option>
                          <option value="AF">Afganistán</option><option value="AL">Albania</option><option value="DE">Alemania</option><option value="AD">Andorra</option><option value="AO">Angola</option><option value="AI">Anguila</option><option value="AQ">Antártida</option><option value="AG">Antigua y Barbuda</option><option value="SA">Arabia Saudí</option><option value="DZ">Argelia</option><option value="AR">Argentina</option><option value="AM">Armenia</option><option value="AW">Aruba</option><option value="AU">Australia</option><option value="AT">Austria</option><option value="AZ">Azerbaiyán</option><option value="BS">Bahamas</option><option value="BD">Bangladés</option><option value="BB">Barbados</option><option value="BH">Baréin</option><option value="BE">Bélgica</option><option value="BZ">Belice</option><option value="BJ">Benín</option><option value="BM">Bermudas</option><option value="BY">Bielorrusia</option><option value="BO">Bolivia</option><option value="BA">Bosnia y Herzegovina</option><option value="BW">Botsuana</option><option value="BR">Brasil</option><option value="BN">Brunéi</option><option value="BG">Bulgaria</option><option value="BF">Burkina Faso</option><option value="BI">Burundi</option><option value="BT">Bután</option><option value="CV">Cabo Verde</option><option value="KH">Camboya</option><option value="CM">Camerún</option><option value="CA">Canadá</option><option value="BQ">Caribe neerlandés</option><option value="QA">Catar</option><option value="TD">Chad</option><option value="CZ">Chequia</option><option value="CL">Chile</option><option value="CN">China</option><option value="CY">Chipre</option><option value="VA">Ciudad del Vaticano</option><option value="CO">Colombia</option><option value="KM">Comoras</option><option value="CG">Congo</option><option value="KP">Corea del Norte</option><option value="KR">Corea del Sur</option><option value="CR">Costa Rica</option><option value="CI">Côted’Ivoire</option><option value="HR">Croacia</option><option value="CU">Cuba</option><option value="CW">Curazao</option><option value="DK">Dinamarca</option><option value="DM">Dominica</option><option value="EC">Ecuador</option><option value="EG">Egipto</option><option value="SV">El Salvador</option><option value="AE">Emiratos Árabes Unidos</option><option value="ER">Eritrea</option><option value="SK">Eslovaquia</option><option value="SI">Eslovenia</option><option value="ES">España</option><option value="US">Estados Unidos</option><option value="EE">Estonia</option><option value="SZ">Esuatini</option><option value="ET">Etiopía</option><option value="PH">Filipinas</option><option value="FI">Finlandia</option><option value="FJ">Fiyi</option><option value="FR">Francia</option><option value="GA">Gabón</option><option value="GM">Gambia</option><option value="GE">Georgia</option><option value="GH">Ghana</option><option value="GI">Gibraltar</option><option value="GD">Granada</option><option value="GR">Grecia</option><option value="GL">Groenlandia</option><option value="GP">Guadalupe</option><option value="GU">Guam</option><option value="GT">Guatemala</option><option value="GF">Guayana Francesa</option><option value="GG">Guernesey</option><option value="GN">Guinea</option><option value="GQ">Guinea Ecuatorial</option><option value="GW">Guinea-Bisáu</option><option value="GY">Guyana</option><option value="HT">Haití</option><option value="HN">Honduras</option><option value="HU">Hungría</option><option value="IN">India</option><option value="ID">Indonesia</option><option value="IQ">Irak</option><option value="IR">Irán</option><option value="IE">Irlanda</option><option value="BV">Isla Bouvet</option><option value="IM">isla de Man</option><option value="CX">isla de Navidad</option><option value="NF">IslaNorfolk</option><option value="IS">Islandia</option><option value="AX">islas Aland</option><option value="KY">islas Caimán</option><option value="CC">islas Cocos</option><option value="CK">islas Cook</option><option value="FO">islas Feroe</option><option value="GS">islas Georgia del Sury Sandwich del Sur</option><option value="HM">islas HeardyMcDonald</option><option value="FK">islas Malvinas</option><option value="MP">islas Marianas del Norte</option><option value="MH">islas Marshall</option><option value="PN">islas Pitcairn</option><option value="SB">islas Salomón</option><option value="TC">islas Turcas y Caicos</option><option value="VG">islas Vírgenes Británicas</option><option value="VI">islas Vírgenes de EE.UU.</option><option value="IL">Israel</option><option value="IT">Italia</option><option value="JM">Jamaica</option><option value="JP">Japón</option><option value="JE">Jersey</option><option value="JO">Jordania</option><option value="KZ">Kazajistán</option><option value="KE">Kenia</option><option value="KG">Kirguistán</option><option value="KI">Kiribati</option><option value="KW">Kuwait</option><option value="LA">Laos</option><option value="LS">Lesoto</option><option value="LV">Letonia</option><option value="LB">Líbano</option><option value="LR">Liberia</option><option value="LY">Libia</option><option value="LI">Liechtenstein</option><option value="LT">Lituania</option><option value="LU">Luxemburgo</option><option value="MK">Macedonia del Norte</option><option value="MG">Madagascar</option><option value="MY">Malasia</option><option value="MW">Malaui</option><option value="MV">Maldivas</option><option value="ML">Mali</option><option value="MT">Malta</option><option value="MA">Marruecos</option><option value="MQ">Martinica</option><option value="MU">Mauricio</option><option value="MR">Mauritania</option><option value="YT">Mayotte</option><option value="MX">México</option><option value="FM">Micronesia</option><option value="MD">Moldavia</option><option value="MC">Mónaco</option><option value="MN">Mongolia</option><option value="ME">Montenegro</option><option value="MS">Montserrat</option><option value="MZ">Mozambique</option><option value="MM">Myanmar(Birmania)</option><option value="NA">Namibia</option><option value="NR">Nauru</option><option value="NP">Nepal</option><option value="NI">Nicaragua</option><option value="NE">Níger</option><option value="NG">Nigeria</option><option value="NU">Niue</option><option value="NO">Noruega</option><option value="NC">Nueva Caledonia</option><option value="NZ">Nueva Zelanda</option><option value="OM">Omán</option><option value="NL">PaísesBajos</option><option value="PK">Pakistán</option><option value="PW">Palaos</option><option value="PA">Panamá</option><option value="PG">Papúa Nueva Guinea</option><option value="PY">Paraguay</option><option value="PE">Perú</option><option value="PF">Polinesia Francesa</option><option value="PL">Polonia</option><option value="PT">Portugal</option><option value="PR">PuertoRico</option><option value="GB">Reino Unido</option><option value="CF">República Centro africana</option><option value="CD">República Democrática del Congo</option><option value="DO">República Dominicana</option><option value="RE">Reunión</option><option value="RW">Ruanda</option><option value="RO">Rumanía</option><option value="RU">Rusia</option><option value="EH">Sáhara Occidental</option><option value="WS">Samoa</option><option value="AS">Samoa Americana</option><option value="BL">San Bartolomé</option><option value="KN">San Cristóbal y Nieves</option><option value="SM">San Marino</option><option value="MF">San Martín</option><option value="PM">San Pedro y Miquelón</option><option value="VC">San Vicente y las Granadinas</option><option value="SH">Santa Elena</option><option value="LC">Santa Lucía</option><option value="ST">Santo Tomé y Príncipe</option><option value="SN">Senegal</option><option value="RS">Serbia</option><option value="SC">Seychelles</option><option value="SL">Sierra Leona</option><option value="SG">Singapur</option><option value="SX">SintMaarten</option><option value="SY">Siria</option><option value="SO">Somalia</option><option value="LK">SriLanka</option><option value="ZA">Sudáfrica</option><option value="SD">Sudán</option><option value="SS">SudándelSur</option><option value="SE">Suecia</option><option value="CH">Suiza</option><option value="SR">Surinam</option><option value="SJ">Svalbardy Jan Mayen</option><option value="TH">Tailandia</option><option value="TW">Taiwán</option><option value="TZ">Tanzania</option><option value="TJ">Tayikistán</option><option value="IO">Territorio Británico del Océano Índico</option><option value="TF">Territorios Australes Franceses</option><option value="PS">Territorios Palestinos</option><option value="TL">Timor-Leste</option><option value="TG">Togo</option><option value="TK">Tokelau</option><option value="TO">Tonga</option><option value="TT">Trinidad y Tobago</option><option value="TN">Túnez</option><option value="TM">Turkmenistán</option><option value="TR">Turquía</option><option value="TV">Tuvalu</option><option value="UA">Ucrania</option><option value="UG">Uganda</option><option value="UY">Uruguay</option><option value="UZ">Uzbekistán</option><option value="VU">Vanuatu</option><option value="VE">Venezuela</option><option value="VN">Vietnam</option><option value="WF">Wallis y Futuna</option><option value="YE">Yemen</option><option value="DJ">Yibuti</option><option value="ZM">Zambia</option><option value="ZW">Zimbabue</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  <div id="show_data_legal_person_title" style="display: none">
                    <div class="col s12 text-center">
                      <h5 class="mb-5">{{ $t('views.Datos sobre el representante/administrador o directivo') }}</h5>
                    </div>
                  </div>

                  <div id="show_data_physical_person_title" style="display: none">
                    <div class="col s12 text-center">
                      <h5 class="mb-5">{{ $t('views.Datos de la persona física') }}</h5>
                    </div>
                  </div>
                  <div id="show_data_person" style="display: none">
                    <div class="row">
                      <div class="input-field col s12 m6">
                        <input id="name" v-model="data_item.name" type="text"  maxlength="100">
                        <label for="name" class="active">{{ $t('views.Nombre') }}</label>
                      </div>
                      <div class="input-field col s12 m6">
                        <input id="surname" v-model="data_item.surname" type="text"  maxlength="100">
                        <label for="surname" class="active">{{ $t('views.Apellidos') }}</label>
                      </div>
                    </div>
                    <div class="row">
                      <div class="input-field col s12 m4">
                        <input id="dni" v-model="data_item.dni" type="text"  maxlength="100">
                        <label for="dni" class="active">{{ $t('views.DNI') }}</label>
                      </div>
                      <div class="input-field col s12 m4">
                        <input id="phone" v-model="data_item.phone" type="text" minlength="6" maxlength="30">
                        <label for="phone" class="active">{{ $t('views.Teléfono') }}</label>
                      </div>
                      <div class="input-field col s12 m4">
                        <input id="date_birthday" v-model="data_item.date_birthday" type="date"  maxlength="10" placeholder="2000-01-31" @blur="isValidDate('date_end')">
                        <label for="date_birthday" class="active">{{ $t('views.Fecha de nacimiento') }}</label>
                      </div>
                    </div>
                    <div class="row">
                      <div class="input-field col s12 m9">
                        <input id="address" v-model="data_item.address" type="text"  maxlength="200">
                        <label for="address" class="active">{{ $t('views.Dirección') }}</label>
                      </div>
                      <div class="input-field col s12 m3">
                        <input id="postal_code" v-model="data_item.postal_code" type="text"  maxlength="100">
                        <label for="postal_code" class="active">{{ $t('views.Código postal') }}</label>
                      </div>
                      <div class="input-field col s12 m6">
                        <input id="city" v-model="data_item.city" type="text"  maxlength="100">
                        <label for="city" class="active">{{ $t('views.Ciudad') }}</label>
                      </div>
                      <div class="input-field col s12 m6">
                        <input id="province" v-model="data_item.province" type="text"  maxlength="100">
                        <label for="province" class="active">{{ $t('views.Provincia') }}</label>
                      </div>
                    </div>

                    <div class="row">
                      <div class="input-field col s12 m6">
                        <label for="country" class="active active_select">{{ $t('views.Elige un país') }}</label>
                        <select class="browser-default" id="country" v-model="data_item.country">
                          <option value="" disabled selected></option>
                          <option value="AF">Afganistán</option><option value="AL">Albania</option><option value="DE">Alemania</option><option value="AD">Andorra</option><option value="AO">Angola</option><option value="AI">Anguila</option><option value="AQ">Antártida</option><option value="AG">Antigua y Barbuda</option><option value="SA">Arabia Saudí</option><option value="DZ">Argelia</option><option value="AR">Argentina</option><option value="AM">Armenia</option><option value="AW">Aruba</option><option value="AU">Australia</option><option value="AT">Austria</option><option value="AZ">Azerbaiyán</option><option value="BS">Bahamas</option><option value="BD">Bangladés</option><option value="BB">Barbados</option><option value="BH">Baréin</option><option value="BE">Bélgica</option><option value="BZ">Belice</option><option value="BJ">Benín</option><option value="BM">Bermudas</option><option value="BY">Bielorrusia</option><option value="BO">Bolivia</option><option value="BA">Bosnia y Herzegovina</option><option value="BW">Botsuana</option><option value="BR">Brasil</option><option value="BN">Brunéi</option><option value="BG">Bulgaria</option><option value="BF">Burkina Faso</option><option value="BI">Burundi</option><option value="BT">Bután</option><option value="CV">Cabo Verde</option><option value="KH">Camboya</option><option value="CM">Camerún</option><option value="CA">Canadá</option><option value="BQ">Caribe neerlandés</option><option value="QA">Catar</option><option value="TD">Chad</option><option value="CZ">Chequia</option><option value="CL">Chile</option><option value="CN">China</option><option value="CY">Chipre</option><option value="VA">Ciudad del Vaticano</option><option value="CO">Colombia</option><option value="KM">Comoras</option><option value="CG">Congo</option><option value="KP">Corea del Norte</option><option value="KR">Corea del Sur</option><option value="CR">Costa Rica</option><option value="CI">Côted’Ivoire</option><option value="HR">Croacia</option><option value="CU">Cuba</option><option value="CW">Curazao</option><option value="DK">Dinamarca</option><option value="DM">Dominica</option><option value="EC">Ecuador</option><option value="EG">Egipto</option><option value="SV">El Salvador</option><option value="AE">Emiratos Árabes Unidos</option><option value="ER">Eritrea</option><option value="SK">Eslovaquia</option><option value="SI">Eslovenia</option><option value="ES">España</option><option value="US">Estados Unidos</option><option value="EE">Estonia</option><option value="SZ">Esuatini</option><option value="ET">Etiopía</option><option value="PH">Filipinas</option><option value="FI">Finlandia</option><option value="FJ">Fiyi</option><option value="FR">Francia</option><option value="GA">Gabón</option><option value="GM">Gambia</option><option value="GE">Georgia</option><option value="GH">Ghana</option><option value="GI">Gibraltar</option><option value="GD">Granada</option><option value="GR">Grecia</option><option value="GL">Groenlandia</option><option value="GP">Guadalupe</option><option value="GU">Guam</option><option value="GT">Guatemala</option><option value="GF">Guayana Francesa</option><option value="GG">Guernesey</option><option value="GN">Guinea</option><option value="GQ">Guinea Ecuatorial</option><option value="GW">Guinea-Bisáu</option><option value="GY">Guyana</option><option value="HT">Haití</option><option value="HN">Honduras</option><option value="HU">Hungría</option><option value="IN">India</option><option value="ID">Indonesia</option><option value="IQ">Irak</option><option value="IR">Irán</option><option value="IE">Irlanda</option><option value="BV">Isla Bouvet</option><option value="IM">isla de Man</option><option value="CX">isla de Navidad</option><option value="NF">IslaNorfolk</option><option value="IS">Islandia</option><option value="AX">islas Aland</option><option value="KY">islas Caimán</option><option value="CC">islas Cocos</option><option value="CK">islas Cook</option><option value="FO">islas Feroe</option><option value="GS">islas Georgia del Sury Sandwich del Sur</option><option value="HM">islas HeardyMcDonald</option><option value="FK">islas Malvinas</option><option value="MP">islas Marianas del Norte</option><option value="MH">islas Marshall</option><option value="PN">islas Pitcairn</option><option value="SB">islas Salomón</option><option value="TC">islas Turcas y Caicos</option><option value="VG">islas Vírgenes Británicas</option><option value="VI">islas Vírgenes de EE.UU.</option><option value="IL">Israel</option><option value="IT">Italia</option><option value="JM">Jamaica</option><option value="JP">Japón</option><option value="JE">Jersey</option><option value="JO">Jordania</option><option value="KZ">Kazajistán</option><option value="KE">Kenia</option><option value="KG">Kirguistán</option><option value="KI">Kiribati</option><option value="KW">Kuwait</option><option value="LA">Laos</option><option value="LS">Lesoto</option><option value="LV">Letonia</option><option value="LB">Líbano</option><option value="LR">Liberia</option><option value="LY">Libia</option><option value="LI">Liechtenstein</option><option value="LT">Lituania</option><option value="LU">Luxemburgo</option><option value="MK">Macedonia del Norte</option><option value="MG">Madagascar</option><option value="MY">Malasia</option><option value="MW">Malaui</option><option value="MV">Maldivas</option><option value="ML">Mali</option><option value="MT">Malta</option><option value="MA">Marruecos</option><option value="MQ">Martinica</option><option value="MU">Mauricio</option><option value="MR">Mauritania</option><option value="YT">Mayotte</option><option value="MX">México</option><option value="FM">Micronesia</option><option value="MD">Moldavia</option><option value="MC">Mónaco</option><option value="MN">Mongolia</option><option value="ME">Montenegro</option><option value="MS">Montserrat</option><option value="MZ">Mozambique</option><option value="MM">Myanmar(Birmania)</option><option value="NA">Namibia</option><option value="NR">Nauru</option><option value="NP">Nepal</option><option value="NI">Nicaragua</option><option value="NE">Níger</option><option value="NG">Nigeria</option><option value="NU">Niue</option><option value="NO">Noruega</option><option value="NC">Nueva Caledonia</option><option value="NZ">Nueva Zelanda</option><option value="OM">Omán</option><option value="NL">PaísesBajos</option><option value="PK">Pakistán</option><option value="PW">Palaos</option><option value="PA">Panamá</option><option value="PG">Papúa Nueva Guinea</option><option value="PY">Paraguay</option><option value="PE">Perú</option><option value="PF">Polinesia Francesa</option><option value="PL">Polonia</option><option value="PT">Portugal</option><option value="PR">PuertoRico</option><option value="GB">Reino Unido</option><option value="CF">República Centro africana</option><option value="CD">República Democrática del Congo</option><option value="DO">República Dominicana</option><option value="RE">Reunión</option><option value="RW">Ruanda</option><option value="RO">Rumanía</option><option value="RU">Rusia</option><option value="EH">Sáhara Occidental</option><option value="WS">Samoa</option><option value="AS">Samoa Americana</option><option value="BL">San Bartolomé</option><option value="KN">San Cristóbal y Nieves</option><option value="SM">San Marino</option><option value="MF">San Martín</option><option value="PM">San Pedro y Miquelón</option><option value="VC">San Vicente y las Granadinas</option><option value="SH">Santa Elena</option><option value="LC">Santa Lucía</option><option value="ST">Santo Tomé y Príncipe</option><option value="SN">Senegal</option><option value="RS">Serbia</option><option value="SC">Seychelles</option><option value="SL">Sierra Leona</option><option value="SG">Singapur</option><option value="SX">SintMaarten</option><option value="SY">Siria</option><option value="SO">Somalia</option><option value="LK">SriLanka</option><option value="ZA">Sudáfrica</option><option value="SD">Sudán</option><option value="SS">SudándelSur</option><option value="SE">Suecia</option><option value="CH">Suiza</option><option value="SR">Surinam</option><option value="SJ">Svalbardy Jan Mayen</option><option value="TH">Tailandia</option><option value="TW">Taiwán</option><option value="TZ">Tanzania</option><option value="TJ">Tayikistán</option><option value="IO">Territorio Británico del Océano Índico</option><option value="TF">Territorios Australes Franceses</option><option value="PS">Territorios Palestinos</option><option value="TL">Timor-Leste</option><option value="TG">Togo</option><option value="TK">Tokelau</option><option value="TO">Tonga</option><option value="TT">Trinidad y Tobago</option><option value="TN">Túnez</option><option value="TM">Turkmenistán</option><option value="TR">Turquía</option><option value="TV">Tuvalu</option><option value="UA">Ucrania</option><option value="UG">Uganda</option><option value="UY">Uruguay</option><option value="UZ">Uzbekistán</option><option value="VU">Vanuatu</option><option value="VE">Venezuela</option><option value="VN">Vietnam</option><option value="WF">Wallis y Futuna</option><option value="YE">Yemen</option><option value="DJ">Yibuti</option><option value="ZM">Zambia</option><option value="ZW">Zimbabue</option>
                        </select>
                      </div>
                      <div class="input-field col s12 m6">
                        <label for="nationality" class="active active_select">{{ $t('views.Nacionalidad') }}</label>
                        <select class="browser-default" id="nationality" v-model="data_item.nationality">
                          <option value="" disabled selected></option>
                          <option value="AF">Afganistán</option><option value="AL">Albania</option><option value="DE">Alemania</option><option value="AD">Andorra</option><option value="AO">Angola</option><option value="AI">Anguila</option><option value="AQ">Antártida</option><option value="AG">Antigua y Barbuda</option><option value="SA">Arabia Saudí</option><option value="DZ">Argelia</option><option value="AR">Argentina</option><option value="AM">Armenia</option><option value="AW">Aruba</option><option value="AU">Australia</option><option value="AT">Austria</option><option value="AZ">Azerbaiyán</option><option value="BS">Bahamas</option><option value="BD">Bangladés</option><option value="BB">Barbados</option><option value="BH">Baréin</option><option value="BE">Bélgica</option><option value="BZ">Belice</option><option value="BJ">Benín</option><option value="BM">Bermudas</option><option value="BY">Bielorrusia</option><option value="BO">Bolivia</option><option value="BA">Bosnia y Herzegovina</option><option value="BW">Botsuana</option><option value="BR">Brasil</option><option value="BN">Brunéi</option><option value="BG">Bulgaria</option><option value="BF">Burkina Faso</option><option value="BI">Burundi</option><option value="BT">Bután</option><option value="CV">Cabo Verde</option><option value="KH">Camboya</option><option value="CM">Camerún</option><option value="CA">Canadá</option><option value="BQ">Caribe neerlandés</option><option value="QA">Catar</option><option value="TD">Chad</option><option value="CZ">Chequia</option><option value="CL">Chile</option><option value="CN">China</option><option value="CY">Chipre</option><option value="VA">Ciudad del Vaticano</option><option value="CO">Colombia</option><option value="KM">Comoras</option><option value="CG">Congo</option><option value="KP">Corea del Norte</option><option value="KR">Corea del Sur</option><option value="CR">Costa Rica</option><option value="CI">Côted’Ivoire</option><option value="HR">Croacia</option><option value="CU">Cuba</option><option value="CW">Curazao</option><option value="DK">Dinamarca</option><option value="DM">Dominica</option><option value="EC">Ecuador</option><option value="EG">Egipto</option><option value="SV">El Salvador</option><option value="AE">Emiratos Árabes Unidos</option><option value="ER">Eritrea</option><option value="SK">Eslovaquia</option><option value="SI">Eslovenia</option><option value="ES">España</option><option value="US">Estados Unidos</option><option value="EE">Estonia</option><option value="SZ">Esuatini</option><option value="ET">Etiopía</option><option value="PH">Filipinas</option><option value="FI">Finlandia</option><option value="FJ">Fiyi</option><option value="FR">Francia</option><option value="GA">Gabón</option><option value="GM">Gambia</option><option value="GE">Georgia</option><option value="GH">Ghana</option><option value="GI">Gibraltar</option><option value="GD">Granada</option><option value="GR">Grecia</option><option value="GL">Groenlandia</option><option value="GP">Guadalupe</option><option value="GU">Guam</option><option value="GT">Guatemala</option><option value="GF">Guayana Francesa</option><option value="GG">Guernesey</option><option value="GN">Guinea</option><option value="GQ">Guinea Ecuatorial</option><option value="GW">Guinea-Bisáu</option><option value="GY">Guyana</option><option value="HT">Haití</option><option value="HN">Honduras</option><option value="HU">Hungría</option><option value="IN">India</option><option value="ID">Indonesia</option><option value="IQ">Irak</option><option value="IR">Irán</option><option value="IE">Irlanda</option><option value="BV">Isla Bouvet</option><option value="IM">isla de Man</option><option value="CX">isla de Navidad</option><option value="NF">IslaNorfolk</option><option value="IS">Islandia</option><option value="AX">islas Aland</option><option value="KY">islas Caimán</option><option value="CC">islas Cocos</option><option value="CK">islas Cook</option><option value="FO">islas Feroe</option><option value="GS">islas Georgia del Sury Sandwich del Sur</option><option value="HM">islas HeardyMcDonald</option><option value="FK">islas Malvinas</option><option value="MP">islas Marianas del Norte</option><option value="MH">islas Marshall</option><option value="PN">islas Pitcairn</option><option value="SB">islas Salomón</option><option value="TC">islas Turcas y Caicos</option><option value="VG">islas Vírgenes Británicas</option><option value="VI">islas Vírgenes de EE.UU.</option><option value="IL">Israel</option><option value="IT">Italia</option><option value="JM">Jamaica</option><option value="JP">Japón</option><option value="JE">Jersey</option><option value="JO">Jordania</option><option value="KZ">Kazajistán</option><option value="KE">Kenia</option><option value="KG">Kirguistán</option><option value="KI">Kiribati</option><option value="KW">Kuwait</option><option value="LA">Laos</option><option value="LS">Lesoto</option><option value="LV">Letonia</option><option value="LB">Líbano</option><option value="LR">Liberia</option><option value="LY">Libia</option><option value="LI">Liechtenstein</option><option value="LT">Lituania</option><option value="LU">Luxemburgo</option><option value="MK">Macedonia del Norte</option><option value="MG">Madagascar</option><option value="MY">Malasia</option><option value="MW">Malaui</option><option value="MV">Maldivas</option><option value="ML">Mali</option><option value="MT">Malta</option><option value="MA">Marruecos</option><option value="MQ">Martinica</option><option value="MU">Mauricio</option><option value="MR">Mauritania</option><option value="YT">Mayotte</option><option value="MX">México</option><option value="FM">Micronesia</option><option value="MD">Moldavia</option><option value="MC">Mónaco</option><option value="MN">Mongolia</option><option value="ME">Montenegro</option><option value="MS">Montserrat</option><option value="MZ">Mozambique</option><option value="MM">Myanmar(Birmania)</option><option value="NA">Namibia</option><option value="NR">Nauru</option><option value="NP">Nepal</option><option value="NI">Nicaragua</option><option value="NE">Níger</option><option value="NG">Nigeria</option><option value="NU">Niue</option><option value="NO">Noruega</option><option value="NC">Nueva Caledonia</option><option value="NZ">Nueva Zelanda</option><option value="OM">Omán</option><option value="NL">PaísesBajos</option><option value="PK">Pakistán</option><option value="PW">Palaos</option><option value="PA">Panamá</option><option value="PG">Papúa Nueva Guinea</option><option value="PY">Paraguay</option><option value="PE">Perú</option><option value="PF">Polinesia Francesa</option><option value="PL">Polonia</option><option value="PT">Portugal</option><option value="PR">PuertoRico</option><option value="GB">Reino Unido</option><option value="CF">República Centro africana</option><option value="CD">República Democrática del Congo</option><option value="DO">República Dominicana</option><option value="RE">Reunión</option><option value="RW">Ruanda</option><option value="RO">Rumanía</option><option value="RU">Rusia</option><option value="EH">Sáhara Occidental</option><option value="WS">Samoa</option><option value="AS">Samoa Americana</option><option value="BL">San Bartolomé</option><option value="KN">San Cristóbal y Nieves</option><option value="SM">San Marino</option><option value="MF">San Martín</option><option value="PM">San Pedro y Miquelón</option><option value="VC">San Vicente y las Granadinas</option><option value="SH">Santa Elena</option><option value="LC">Santa Lucía</option><option value="ST">Santo Tomé y Príncipe</option><option value="SN">Senegal</option><option value="RS">Serbia</option><option value="SC">Seychelles</option><option value="SL">Sierra Leona</option><option value="SG">Singapur</option><option value="SX">SintMaarten</option><option value="SY">Siria</option><option value="SO">Somalia</option><option value="LK">SriLanka</option><option value="ZA">Sudáfrica</option><option value="SD">Sudán</option><option value="SS">SudándelSur</option><option value="SE">Suecia</option><option value="CH">Suiza</option><option value="SR">Surinam</option><option value="SJ">Svalbardy Jan Mayen</option><option value="TH">Tailandia</option><option value="TW">Taiwán</option><option value="TZ">Tanzania</option><option value="TJ">Tayikistán</option><option value="IO">Territorio Británico del Océano Índico</option><option value="TF">Territorios Australes Franceses</option><option value="PS">Territorios Palestinos</option><option value="TL">Timor-Leste</option><option value="TG">Togo</option><option value="TK">Tokelau</option><option value="TO">Tonga</option><option value="TT">Trinidad y Tobago</option><option value="TN">Túnez</option><option value="TM">Turkmenistán</option><option value="TR">Turquía</option><option value="TV">Tuvalu</option><option value="UA">Ucrania</option><option value="UG">Uganda</option><option value="UY">Uruguay</option><option value="UZ">Uzbekistán</option><option value="VU">Vanuatu</option><option value="VE">Venezuela</option><option value="VN">Vietnam</option><option value="WF">Wallis y Futuna</option><option value="YE">Yemen</option><option value="DJ">Yibuti</option><option value="ZM">Zambia</option><option value="ZW">Zimbabue</option>
                        </select>
                      </div>
                    </div>

                    <div class="row">
                      <div class="input-field col s12 m6">
                        <label for="civil_status" class="active active_select">{{ $t('views.Estado civil') }}</label>
                        <select class="browser-default" id="civil_status" v-model="data_item.civil_status" @change="showHideMatrimonailRegime">
                          <option value="" disabled selected></option>
                          <option value="0">{{ $t('views.Soltero') }}</option>
                          <option value="1">{{ $t('views.Casado') }}</option>
                          <option value="2">{{ $t('views.Separado') }}</option>
                          <option value="3">{{ $t('views.Divorciado') }}</option>
                        </select>
                      </div>
                      <div id="div_economic_matrimonial_regime" class="input-field col s12 m6">
                        <label for="economic_matrimonial_regime" class="active active_select">{{ $t('views.Régimen económico matrimonial') }}</label>
                        <select class="browser-default" id="economic_matrimonial_regime" v-model="data_item.economic_matrimonial_regime">
                          <option value="0">{{ $t('views.La sociedad de gananciales') }}</option>
                          <option value="1">{{ $t('views.El régimen de participación') }}</option>
                          <option value="2">{{ $t('views.El régimen de separación de bienes') }}</option>
                        </select>
                      </div>
                    </div>

                    <div class="row">
                      <div v-if="data_item.user_type == 1" class="input-field col s12">
                        <p class="ml-2">
                          <label>
                            <input id="is_representative_owner" type="checkbox" class="filled-in" v-model="data_item.is_representative_owner"/>
                            <span style="color: #757575">{{ $t('views.Marcar si el representante es beneficiario de la empresa con mas del 25%') }}</span>
                          </label>
                        </p>
                      </div>
                    </div>
                  </div>

                </fieldset>
              </div>
            </div>
          </div>
        </div>


        <div class="input-field col s12">
          <button class="btn-primary right" type="submit" :disabled="loading">{{ $t('views.guardar') }}</button>
        </div>


      </div>
    </form>


  </div>
</template>


<script lang="ts">

import { Options, Vue } from 'vue-class-component';
import M from "materialize-css";
import UserServices from "@/services/UserServices";
import {showAlertError, isValidDate, formatNumber, showAlert} from "@/functions";
import Editor from "@tinymce/tinymce-vue";
import JQuery from 'jquery';
import Menu from "@/components/Menu.vue";

@Options({
  components: {
    Menu,
    Editor
  },
})
export default class UserFormView extends Vue {

  loading = false

  // eslint-disable-next-line
  data_item: any = {}

  mounted () {
    M.AutoInit();
  }

  save() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    this.loading = true
    //si tiene id de noticia entonces es actualizar sino es uno nuevo
    UserServices.saveUser(this.data_item)
        // eslint-disable-next-line no-unused-vars
        .then(response => {
          showAlert("",self.$t('views.Datos guardados correctamente'), false, function() {
            self.$router.push('/UsersList')
          })
        })
        .catch(function (error) {
          self.loading = false
          showAlertError(error, self)
        });
  }

  changeUserType(){
    if (this.data_item.user_type == 0){
      JQuery('#show_data_legal_person').hide()
      JQuery('#show_data_legal_person_title').hide()
      JQuery('#show_data_person').show()
      JQuery('#show_data_physical_person_title').show()
    } else if (this.data_item.user_type == 1){
      JQuery('#show_data_legal_person').show()
      JQuery('#show_data_legal_person_title').show()
      JQuery('#show_data_person').show()
      JQuery('#show_data_physical_person_title').hide()
    }
  }


  showHideMatrimonailRegime(){
    if (this.data_item.civil_status !== undefined && this.data_item.civil_status != 0){
      document.getElementById('div_economic_matrimonial_regime').style.display=''
    } else {
      document.getElementById('div_economic_matrimonial_regime').style.display='none'
    }
  }

  isValidDate(value){
    let date_in = JQuery('#' + value).val()
    if (date_in != undefined && date_in != "") {
      if (!isValidDate(date_in)) {
        showAlertError("El formato de la fecha no es correcto", this)
      }
    }
  }

  changeHolders () {
    if (this.data_item.holders > 3) {
      this.data_item.holders = 3
    }
    if (this.data_item.holders < 1) {
      this.data_item.holders = 0
    }
  }

}
</script>
