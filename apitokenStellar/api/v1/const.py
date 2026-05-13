INVEST_STATUS_PENDING = 0
INVEST_STATUS_NEXT_LAUNCH = 1
INVEST_STATUS_FINANCING_PHASE = 2
INVEST_STATUS_IN_PROGRESS = 3
INVEST_STATUS_FINISHED = 99

USERS_INVEST_TYPE_BUY_WITHOUT_VERIFIED = 1
USERS_INVEST_TYPE_BUY = 2
USERS_INVEST_TYPE_BUY_REJECTED = 3
USERS_INVEST_TYPE_BUY_CANCELED = 4
USERS_INVEST_TYPE_BUY_ERROR = 5
USERS_INVEST_TYPE_WAITING_OTHER_USER_FOR_BUY = 6
USERS_INVEST_TYPE_BUY_CARD_WITHOUT_VERIFIED = 7

USERS_INVEST_TYPE_PUT_ON_SALE = 15
USERS_INVEST_TYPE_SOLD = 16
USERS_INVEST_TYPE_REMOVE_FOR_SALE = 17
USERS_INVEST_TYPE_WAITING_OTHER_USER_FOR_SALE = 18
USERS_INVEST_TYPE_SALE_REJECTED = 19
USERS_INVEST_TYPE_SALE_CANCELLED = 20

USERS_INVEST_TYPE_PROFITS = 25
USERS_INVEST_TYPE_PROFITS_CLAIM = 26
USERS_INVEST_TYPE_PROFITS_RECEIVED = 27

USERS_INVEST_TYPE_DEPOSIT = 30  # tiene subtipos, puede ser deposito por añadir capital, referidos, final de proyecto etc
USERS_INVEST_TYPE_DEPOSIT_CLAIM = 31
USERS_INVEST_TYPE_DEPOSIT_RECEIVED = 32
USERS_INVEST_TYPE_DEPOSIT_TO_INVEST = 33
USERS_INVEST_TYPE_DEPOSIT_WITHOUT_VERIFIED = 34

USERS_INVEST_TYPE_REFUND = 40  # se devuelve parte de la inversion por que ha sido un error y es como si no se hubiera hecho
USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND = 41
USERS_INVEST_TYPE_REFUND_PARTIAL = 42  # se devuelve parte de la inversion pero sigue contando en repartos y en invertido

# SUBTIPOS DE COMPRA PARA EL TIPO USERS_INVEST_TYPE_BUY
BUY_SUBTYPE_PAYMENT_VIRTUAL_WALLET = 0
BUY_SUBTYPE_PAYMENT_TRANSFER = 1
BUY_SUBTYPE_PAYMENT_CARD = 2
BUY_SUBTYPE_PAYMENT_CRYPTO = 3
BUY_SUBTYPE_PAYMENT_PROFITS_INVEST = 4

# SUBTIPOS DE DEPOSITOS DE ENTRADA DE DINERO PARA EL TIPO USERS_INVEST_TYPE_DEPOSIT
DEPOSIT_SUBTYPE_CLOSE_PROJECT = 0
DEPOSIT_SUBTYPE_ADD_BY_TRANSFER = 1
DEPOSIT_SUBTYPE_ADD_BY_CARD = 2
DEPOSIT_SUBTYPE_ADD_BY_CRYPTO = 3
DEPOSIT_SUBTYPE_PROFITS = 4
DEPOSIT_SUBTYPE_REFERRAL = 5
DEPOSIT_SUBTYPE_SALE = 6
DEPOSIT_SUBTYPE_BUY_OTHER_USER = 7

# CATEGORIAS DE PROYECTOS
INVEST_CATEGORY_ID_TOTAL = -1
INVEST_CATEGORY_ID_HOLDING = 0
INVEST_CATEGORY_ID_EQUITY = 1
INVEST_CATEGORY_ID_DEBT = 2
INVEST_CATEGORY_ID_INTEREST = 3

FILE_TYPE_PROFILE = 0
FILE_TYPE_PROFILE_TOP = 1
FILE_TYPE_DNI_BACK = 2
FILE_TYPE_DNI_FRONT = 3
FILE_TYPE_DRIVE_LICENSE_BACK = 5
FILE_TYPE_DRIVE_LICENSE_FRONT = 6
FILE_TYPE_RESIDENCE_CARD_BACK = 7
FILE_TYPE_RESIDENCE_CARD_FRONT = 8
FILE_TYPE_PASSPORT_EU_BACK = 9
FILE_TYPE_PASSPORT_EU_FRONT = 10
FILE_TYPE_PASSPORT_OUTSIDE_EU_FRONT = 11

FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_BACK = 20
FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_FRONT = 21
FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_BACK = 22
FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_FRONT = 23
FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_BACK = 24
FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_FRONT = 25
FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_BACK = 26
FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_FRONT = 27

FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_BACK = 30
FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_FRONT = 31
FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_BACK = 32
FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_FRONT = 33
FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_BACK = 34
FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_FRONT = 35
FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_BACK = 36
FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_FRONT = 37

FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_BACK = 40
FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_FRONT = 41
FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_BACK = 42
FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_FRONT = 43
FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_BACK = 44
FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_FRONT = 45
FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_BACK = 46
FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_FRONT = 47

FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_BACK = 50
FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_FRONT = 51
FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_BACK = 52
FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_FRONT = 53
FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_BACK = 54
FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_FRONT = 55
FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_BACK = 56
FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_FRONT = 57

FILE_TYPE_CERTIFICATE_OF_INCORPORATION = 58
FILE_TYPE_ARTICLES_OF_ASSOCIATION = 59
FILE_TYPE_DEEPS_OF_INCORPORATION = 60
FILE_TYPE_PROOF_IBAN = 61

FILE_TYPE_SELFIE = 4

SIGNATURE_CONTRACT_STATUS_READY = 'ready'
SIGNATURE_CONTRACT_STATUS_COMPLETE = 'completed'
SIGNATURE_CONTRACT_STATUS_FIAT_SENT = 'fiat_trans_sent'
SIGNATURE_CONTRACT_STATUS_TOKEN_PAYOUT = 'token_payout'
SIGNATURE_CONTRACT_STATUS_REVERT = 'revert'

DEPLOY_STATUS_PENDING = 0
DEPLOY_STATUS_MARK_DEPLOYED = 1
DEPLOY_STATUS_DEPLOYED = 2

BUY_BY_TRANSFER_PROJECT = 0
BUY_BY_TRANSFER_OTHER_USER = 1

BANK_TRANSFER_BUY_PROJECT_PREFIX = 'BPT'
BANK_TRANSFER_BUY_OTHER_USER_PREFIX = 'BMP'

ALPHAINCHAIN_SLUG = 'invest-proyecto-lunarxy-club-1-yw8sz'
CLUB_SLUG = 'proyecto-lunarxy-club-XY-Member'
CLUB_TIER_1_PRICE = 99
CLUB_TIER_2_PRICE = 495
CLUB_TIER_3_PRICE = 9900
CLUB_MINT_PK = "0x4d63536bc2b681fec0ff43964a6a9db4bd6710188833c35e93b6881853c0007b"
CLUB_WITHDRAW_PK = "0x7dfedf325bd6d545108c4ef23bf0f3c6dc19e3f908cb039fc5948066566e8320"
CLUB_FOUNDER_MINT_PK = "0xaf9337372d79ed5301e68bc2345ec0f799600b673c1f9e5a66511cf540cd19c3"

TAXES = 21
REFERRAL1_FEE = 10
REFERRAL2_FEE = 5
REFERRAL3_FEE = 15

COUNTRY_CODES = {
    "AF": "Afganistán",
    "AL": "Albania",
    "DE": "Alemania",
    "AD": "Andorra",
    "AO": "Angola",
    "AI": "Anguila",
    "AQ": "Antártida",
    "AG": "Antigua y Barbuda",
    "SA": "Arabia Saudí",
    "DZ": "Argelia",
    "AR": "Argentina",
    "AM": "Armenia",
    "AW": "Aruba",
    "AU": "Australia",
    "AT": "Austria",
    "AZ": "Azerbaiyán",
    "BS": "Bahamas",
    "BD": "Bangladés",
    "BB": "Barbados",
    "BH": "Baréin",
    "BE": "Bélgica",
    "BZ": "Belice",
    "BJ": "Benín",
    "BM": "Bermudas",
    "BY": "Bielorrusia",
    "BO": "Bolivia",
    "BA": "Bosnia y Herzegovina",
    "BW": "Botsuana",
    "BR": "Brasil",
    "BN": "Brunéi",
    "BG": "Bulgaria",
    "BF": "Burkina Faso",
    "BI": "Burundi",
    "BT": "Bután",
    "CV": "Cabo Verde",
    "KH": "Camboya",
    "CM": "Camerún",
    "CA": "Canadá",
    "BQ": "Caribe neerlandés",
    "QA": "Catar",
    "TD": "Chad",
    "CZ": "Chequia",
    "CL": "Chile",
    "CN": "China",
    "CY": "Chipre",
    "VA": "Ciudad del Vaticano",
    "CO": "Colombia",
    "KM": "Comoras",
    "CG": "Congo",
    "KP": "Corea del Norte",
    "KR": "Corea del Sur",
    "CR": "Costa Rica",
    "CI": "Côted’Ivoire",
    "HR": "Croacia",
    "CU": "Cuba",
    "CW": "Curazao",
    "DK": "Dinamarca",
    "DM": "Dominica",
    "EC": "Ecuador",
    "EG": "Egipto",
    "SV": "El Salvador",
    "AE": "Emiratos Árabes Unidos",
    "ER": "Eritrea",
    "SK": "Eslovaquia",
    "SI": "Eslovenia",
    "ES": "España",
    "US": "Estados Unidos",
    "EE": "Estonia",
    "SZ": "Esuatini",
    "ET": "Etiopía",
    "PH": "Filipinas",
    "FI": "Finlandia",
    "FJ": "Fiyi",
    "FR": "Francia",
    "GA": "Gabón",
    "GM": "Gambia",
    "GE": "Georgia",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GD": "Granada",
    "GR": "Grecia",
    "GL": "Groenlandia",
    "GP": "Guadalupe",
    "GU": "Guam",
    "GT": "Guatemala",
    "GF": "Guayana Francesa",
    "GG": "Guernesey",
    "GN": "Guinea",
    "GQ": "Guinea Ecuatorial",
    "GW": "Guinea-Bisáu",
    "GY": "Guyana",
    "HT": "Haití",
    "HN": "Honduras",
    "HU": "Hungría",
    "IN": "India",
    "ID": "Indonesia",
    "IQ": "Irak",
    "IR": "Irán",
    "IE": "Irlanda",
    "BV": "Isla Bouvet",
    "IM": "isla de Man",
    "CX": "isla de Navidad",
    "NF": "IslaNorfolk",
    "IS": "Islandia",
    "AX": "islas Aland",
    "KY": "islas Caimán",
    "CC": "islas Cocos",
    "CK": "islas Cook",
    "FO": "islas Feroe",
    "GS": "islas Georgia del Sury Sandwich del Sur",
    "HM": "islas HeardyMcDonald",
    "FK": "islas Malvinas",
    "MP": "islas Marianas del Norte",
    "MH": "islas Marshall",
    "PN": "islas Pitcairn",
    "SB": "islas Salomón",
    "TC": "islas Turcas y Caicos",
    "VG": "islas Vírgenes Británicas",
    "VI": "islas Vírgenes de EE.UU.",
    "IL": "Israel",
    "IT": "Italia",
    "JM": "Jamaica",
    "JP": "Japón",
    "JE": "Jersey",
    "JO": "Jordania",
    "KZ": "Kazajistán",
    "KE": "Kenia",
    "KG": "Kirguistán",
    "KI": "Kiribati",
    "KW": "Kuwait",
    "LA": "Laos",
    "LS": "Lesoto",
    "LV": "Letonia",
    "LB": "Líbano",
    "LR": "Liberia",
    "LY": "Libia",
    "LI": "Liechtenstein",
    "LT": "Lituania",
    "LU": "Luxemburgo",
    "MK": "Macedonia del Norte",
    "MG": "Madagascar",
    "MY": "Malasia",
    "MW": "Malaui",
    "MV": "Maldivas",
    "ML": "Mali",
    "MT": "Malta",
    "MA": "Marruecos",
    "MQ": "Martinica",
    "MU": "Mauricio",
    "MR": "Mauritania",
    "YT": "Mayotte",
    "MX": "México",
    "FM": "Micronesia",
    "MD": "Moldavia",
    "MC": "Mónaco",
    "MN": "Mongolia",
    "ME": "Montenegro",
    "MS": "Montserrat",
    "MZ": "Mozambique",
    "MM": "Myanmar(Birmania)",
    "NA": "Namibia",
    "NR": "Nauru",
    "NP": "Nepal",
    "NI": "Nicaragua",
    "NE": "Níger",
    "NG": "Nigeria",
    "NU": "Niue",
    "NO": "Noruega",
    "NC": "Nueva Caledonia",
    "NZ": "Nueva Zelanda",
    "OM": "Omán",
    "NL": "PaísesBajos",
    "PK": "Pakistán",
    "PW": "Palaos",
    "PA": "Panamá",
    "PG": "Papúa Nueva Guinea",
    "PY": "Paraguay",
    "PE": "Perú",
    "PF": "Polinesia Francesa",
    "PL": "Polonia",
    "PT": "Portugal",
    "PR": "PuertoRico",
    "GB": "Reino Unido",
    "CF": "República Centro africana",
    "CD": "República Democrática del Congo",
    "DO": "República Dominicana",
    "RE": "Reunión",
    "RW": "Ruanda",
    "RO": "Rumanía",
    "RU": "Rusia",
    "EH": "Sáhara Occidental",
    "WS": "Samoa",
    "AS": "Samoa Americana",
    "BL": "San Bartolomé",
    "KN": "San Cristóbal y Nieves",
    "SM": "San Marino",
    "MF": "San Martín",
    "PM": "San Pedro y Miquelón",
    "VC": "San Vicente y las Granadinas",
    "SH": "Santa Elena",
    "LC": "Santa Lucía",
    "ST": "Santo Tomé y Príncipe",
    "SN": "Senegal",
    "RS": "Serbia",
    "SC": "Seychelles",
    "SL": "Sierra Leona",
    "SG": "Singapur",
    "SX": "SintMaarten",
    "SY": "Siria",
    "SO": "Somalia",
    "LK": "SriLanka",
    "ZA": "Sudáfrica",
    "SD": "Sudán",
    "SS": "SudándelSur",
    "SE": "Suecia",
    "CH": "Suiza",
    "SR": "Surinam",
    "SJ": "Svalbardy Jan Mayen",
    "TH": "Tailandia",
    "TW": "Taiwán",
    "TZ": "Tanzania",
    "TJ": "Tayikistán",
    "IO": "Territorio Británico del Océano Índico",
    "TF": "Territorios Australes Franceses",
    "PS": "Territorios Palestinos",
    "TL": "Timor-Leste",
    "TG": "Togo",
    "TK": "Tokelau",
    "TO": "Tonga",
    "TT": "Trinidad y Tobago",
    "TN": "Túnez",
    "TM": "Turkmenistán",
    "TR": "Turquía",
    "TV": "Tuvalu",
    "UA": "Ucrania",
    "UG": "Uganda",
    "UY": "Uruguay",
    "UZ": "Uzbekistán",
    "VU": "Vanuatu",
    "VE": "Venezuela",
    "VN": "Vietnam",
    "WF": "Wallis y Futuna",
    "YE": "Yemen",
    "DJ": "Yibuti",
    "ZM": "Zambia",
    "ZW": "Zimbabue",
}



