import M from "materialize-css";
import JQuery from "jquery";

export function showAlert(title, msg, isConfirm = false, functionOK: any = null) {
    //init material
    //M.AutoInit();

    //se pone esto para eliminar los listener anteriores
    const aux = document.getElementById('modal_alert')
    // eslint-disable-next-line no-self-assign
    aux.outerHTML = aux.outerHTML

    //init modals without dimissible onclick out
    const elems = document.querySelectorAll('.modal');
    M.Modal.init(elems, { dismissible: true });

    const singleModalElem = document.querySelector('#modal_alert');
    if (singleModalElem != null) {
        const instance = M.Modal.getInstance(singleModalElem);
        const modal_alert_header = document.getElementById('modal_alert_header');
        if (modal_alert_header != null) {
            modal_alert_header.innerHTML = title;
        }
        const alert_text = document.getElementById('modal_alert_text');
        if (alert_text != null) {
            alert_text.innerHTML = msg;
        }
        const modal_alert_bt_cancel = document.getElementById('modal_alert_bt_cancel');
        if (modal_alert_bt_cancel != null) {
            if (isConfirm) {
                modal_alert_bt_cancel.style.display = 'initial';
            } else {
                modal_alert_bt_cancel.style.display = 'none';
            }
        }

        if (functionOK != null) {
            //si tiene funcion ok solo se puede minimizar con el boton ok
            instance.options.dismissible = false
            const modal_alert_close = document.getElementById('modal_alert_close');
            if (modal_alert_close != null) {
                modal_alert_close.style.display = 'none';
            }

            const modal_alert_bt_ok = document.getElementById('modal_alert_bt_ok')
            if (modal_alert_bt_ok != null) {
                modal_alert_bt_ok.addEventListener('click', functionOK);
            }
        }
        instance.open();
    }
}

export function showAlertError(error, _this, functionOK: any = null) {
    if (error != null) {
        if (error.toString().includes('Cannot set properties of null') || error.toString().includes('Cannot read properties of null')) return
        if (error.toString().includes('Cannot read properties of undefined')) {
            //para el error 500 del servidor
            showAlert("Error!", _this.$t("server.Se ha producido un error inesperado"), false, functionOK);
            return;
        }

        if (error.response != null) {
            if (error.response.status === 422) {
                showAlert("Error!", _this.$t("server.Se ha producido un error inesperado"), false, functionOK);
            } else {
                if (_this != null) {
                    showAlert("Error!", _this.$t(error.response.data.detail), false, functionOK);
                } else {
                    showAlert("Error!", error.response.data.detail, false, functionOK);
                }
            }
        } else {
            showAlert("Error!", error, false, functionOK);
        }
    }
}

export function showAlertLoading(msg = '') {
    //init modals without dimissible onclick out
    const elems = document.querySelectorAll('.modal');
    M.Modal.init(elems, { dismissible: true });
    const singleModalElem = document.querySelector('#modal_loading');
    if (singleModalElem != null) {
        if (msg != '') {
            document.getElementById("msg_modal_loading").innerHTML = msg
        }
        const instance = M.Modal.getInstance(singleModalElem);
        instance.open();
    }
}
export function hideAlertLoading() {
    //init modals without dimissible onclick out
    const elems = document.querySelectorAll('.modal');
    M.Modal.init(elems, { dismissible: true });
    const singleModalElem = document.querySelector('#modal_loading');
    if (singleModalElem != null) {
        const instance = M.Modal.getInstance(singleModalElem);
        instance.close();
    }
}

let interval = undefined
export function countDown(myDate: string) {
    // ejemplo de llamada countDown("2022-06-15T08:00:00Z")
    // se resetean los intervalos
    window.clearInterval(interval);

    if (myDate == undefined || myDate == "") {
        const div_date_fin = document.getElementById("date_fin")
        if (div_date_fin != null) {
            div_date_fin.style.display = "block";
        }
        return;
    }

    // Establecer la fecha en la que estamos contando hacia atrás
    const countDownDate = new Date(myDate).getTime();

    const div_days = document.getElementById("div_days");
    const div_hours = document.getElementById("div_hours");
    const div_minutes = document.getElementById("div_minutes");
    const div_seconds = document.getElementById("div_seconds");

    // Obtener la fecha y la hora de hoy
    const now = new Date().getTime();

    // Encontrar la distancia entre ahora y la fecha de la cuenta atras
    const distancia = countDownDate - now;

    // Cálculos de tiempo para días horas minutos y segundos
    const days = Math.floor(distancia / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distancia % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distancia % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distancia % (1000 * 60)) / 1000);

    // Muestra el resultado en un elemento
    if (div_days != null) div_days.innerHTML = days.toString();
    if (div_hours != null) div_hours.innerHTML = hours.toString();
    if (div_minutes != null) div_minutes.innerHTML = minutes.toString();
    if (div_seconds != null) div_seconds.innerHTML = seconds.toString();

    // Si la cuenta regresiva ha terminado, escribe un texto
    if (distancia < 0) {
        if (div_days != null) div_days.innerHTML = "0";
        if (div_hours != null) div_hours.innerHTML = "0";
        if (div_minutes != null) div_minutes.innerHTML = "0";
        if (div_seconds != null) div_seconds.innerHTML = "0";
        if (document.getElementById("count_back") != null) {
            document.getElementById("count_back").style.display = "none";
            document.getElementById("date_fin").style.display = "block";
        }
    } else {
        if (document.getElementById("count_back") != null) {
            document.getElementById("count_back").style.display = "block";
            // Actualizar la cuenta atras cada 1 segundo
            interval = setInterval(countDown, 1000, myDate);
        }
    }
}

export function sortTable(myTable: string, n: number) {
    let rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    const table = document.getElementById(myTable) as HTMLTableElement;
    if (table != null) {
        switching = true;
        //Set the sorting direction to ascending:
        dir = "asc";
        /*Make a loop that will continue until
        no switching has been done:*/
        while (switching) {
            //start by saying: no switching is done:
            switching = false;
            rows = table.rows;
            /*Loop through all table rows (except the
            first, which contains table headers):*/
            for (i = 1; i < (rows.length - 1); i++) {
                //start by saying there should be no switching:
                shouldSwitch = false;
                /*Get the two elements you want to compare,
                one from current row and one from the next:*/
                x = rows[i].getElementsByTagName("TD")[n];
                y = rows[i + 1].getElementsByTagName("TD")[n];
                /*check if the two rows should switch place,
                based on the direction, asc or desc:*/
                if (dir == "asc") {
                    if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                        //if so, mark as a switch and break the loop:
                        shouldSwitch = true;
                        break;
                    }
                } else if (dir == "desc") {
                    if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                        //if so, mark as a switch and break the loop:
                        shouldSwitch = true;
                        break;
                    }
                }
            }
            if (shouldSwitch) {
                /*If a switch has been marked, make the switch
                and mark that a switch has been done:*/
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
                //Each time a switch is done, increase this count by 1:
                switchcount++;
            } else {
                /*If no switching has been done AND the direction is "asc",
                set the direction to "desc" and run the while loop again.*/
                if (switchcount == 0 && dir == "asc") {
                    dir = "desc";
                    switching = true;
                }
            }
        }
    }
}


export function printStars(number, drawPlaceholder) {
    const numMaxStars = 6;
    let counter = 0;
    const roundedNumber = Math.floor(number)

    drawPlaceholder.innerHTML = "";
    for (let i = 0; i < roundedNumber; i++) {
        drawPlaceholder?.insertAdjacentHTML('beforeend', '<i class="material-icons">star</i>');
        counter++;
    }
    if (Math.floor(number) !== number) {
        drawPlaceholder?.insertAdjacentHTML('beforeend', '<i class="material-icons">star_half</i>');
        counter++;
    }
    if (counter < numMaxStars) {
        for (let i = 0; i < (numMaxStars - counter); i++) {
            drawPlaceholder?.insertAdjacentHTML('beforeend', '<i class="material-icons">star_border</i>');
        }
    }
}


export function getMonthName(month) {
    if (navigator.language == 'es-ES' || navigator.language == 'es') {
        if (month == 0 || month == -12) return 'Enero'
        if (month == 1 || month == -11) return 'Febrero'
        if (month == 2 || month == -10) return 'Marzo'
        if (month == 3 || month == -9) return 'Abril'
        if (month == 4 || month == -8) return 'Mayo'
        if (month == 5 || month == -7) return 'Junio'
        if (month == 6 || month == -6) return 'Julio'
        if (month == 7 || month == -5) return 'Agosto'
        if (month == 8 || month == -4) return 'Septiembre'
        if (month == 9 || month == -3) return 'Octubre'
        if (month == 10 || month == -2) return 'Noviembre'
        if (month == 11 || month == -1) return 'Diciembre'
    }

    if (month == 0 || month == -12) return 'January'
    if (month == 1 || month == -11) return 'February'
    if (month == 2 || month == -10) return 'March'
    if (month == 3 || month == -9) return 'April'
    if (month == 4 || month == -8) return 'May'
    if (month == 5 || month == -7) return 'Jun'
    if (month == 6 || month == -6) return 'July'
    if (month == 7 || month == -5) return 'August'
    if (month == 8 || month == -4) return 'September'
    if (month == 9 || month == -3) return 'October'
    if (month == 10 || month == -2) return 'November'
    if (month == 11 || month == -1) return 'December'
}
export function formatDateFromServer(date_in, hours = true) {
    // entra 2022-11-05T11:17:59 en UTC del servidor y
    // sale 2022-11-05 12:17:59 en horario de locale actual
    let f = null;
    if (date_in != undefined && date_in != "") {
        if (!date_in.includes("T")) return date_in
        const date = new Date(date_in + ".000Z")
        f =
            [
                date.getFullYear(),
                (date.getMonth() + 1).toString().padStart(2, '0'),
                (date.getDate()).toString().padStart(2, '0'),
            ].join('-') +
            ' ' +
            [
                (date.getHours()).toString().padStart(2, '0'),
                (date.getMinutes()).toString().padStart(2, '0'),
                //(date.getSeconds()).toString().padStart(2, '0'),
            ].join(':')

        if (!hours) {
            f = f.split(' ')[0]
        }
    }
    return f
}

export function parseDateToUTC(my_date) {
    //entra una fecha en formato 2023-12-15T15:02 y sale 023-12-15T14:02 si estamos en UTC +1
    const fechaLocal = new Date(my_date);
    // Crear un objeto Date en formato UTC
    let aux = new Date(Date.UTC(fechaLocal.getUTCFullYear(), fechaLocal.getUTCMonth(), fechaLocal.getUTCDate(),
        fechaLocal.getUTCHours(), fechaLocal.getUTCMinutes())).toISOString().split('.')[0];
    aux = aux.replace('T', ' ')
    return aux
}

export function isValidDate(date_in) {
    //entra YYYY-MM-DD
    if (date_in != undefined && date_in != "") {
        const regex = /^\d{4}-\d{2}-\d{2}$/;
        if (date_in.match(regex) === null) {
            return false;
        }
        const date = new Date(date_in);
        const timestamp = date.getTime();
        if (typeof timestamp !== 'number' || Number.isNaN(timestamp)) {
            return false;
        }
        return date.toISOString().startsWith(date_in);
    }
    return false;
}

export function compareDates(fechaString) {
    // Convertir la fecha en formato de cadena a objeto Date
    const fechaEntrada = new Date(fechaString);
    // Obtener la fecha actual del sistema
    const fechaSistema = new Date();

    // Comparar las fechas
    if (fechaEntrada.getTime() === fechaSistema.getTime()) {
        return 0; // Fecha de entrada es igual a la fecha del sistema
    } else if (fechaEntrada > fechaSistema) {
        return 1; // Fecha de entrada es mayor que la fecha del sistema
    } else {
        return -1; // Fecha de entrada es menor que la fecha del sistema
    }
}

export function formatNumber(num, decimals = 2) {
    if (num === '00000000') return num;
    if (isNaN(num)) return 0

    // Se utiliza Intl.NumberFormat para evitar vulnerabilidades de ReDoS y simplificar el formateo.
    // Usamos 'es-ES' que corresponde al formato anterior (puntos para miles, coma para decimales)
    return new Intl.NumberFormat('es-ES', {
        minimumFractionDigits: 0,
        maximumFractionDigits: Math.max(0, decimals),
    }).format(num);
}

export function formatNumberWithDecimalsToServer(num) {
    if (num.includes(".") && !num.includes(",")) {
        //si incluye punto y no incluye coma entonces sustituimos el punto por la coma
        return num.replace(/\./g, ',')
    } else {
        //quitamos el . de miles
        return num.replace(/\./g, '')
    }
}

export function numbersOnly(evt, decimals = false) {
    evt = evt || window.event;
    const charCode = evt.which || evt.keyCode;

    // Obtenemos el valor actual del input
    const inputValue = evt.target.value;

    // Teclas permitidas sin validar (backspace, delete, tab, etc.)
    const allowedKeys = [8, 9, 27, 13, 37, 39]; // backspace, tab, escape, enter, left arrow, right arrow

    // Verifica si la tecla está en las permitidas
    if (allowedKeys.indexOf(charCode) !== -1) {
        return true;
    }

    // Si los decimales están permitidos
    if (decimals) {
        // Verifica si ya existe un separador (punto o coma)
        const hasComma = inputValue.indexOf(',') !== -1;
        const hasDot = inputValue.indexOf('.') !== -1;

        // Permitir números del 0 al 9, y evitar múltiples decimales
        if ((charCode >= 48 && charCode <= 57) || // Números (teclado normal)
            (charCode >= 96 && charCode <= 105)) { // Números (teclado numérico)
            return true;
        }

        // Permitir una coma o un punto, pero no ambos ni repetidos
        if ((charCode === 188 && !hasComma && !hasDot) || // Coma, si no hay coma ni punto
            ((charCode === 190 || charCode === 110) && !hasDot && !hasComma)) { // Punto, si no hay punto ni coma
            return true;
        }
    } else {
        // Solo permitir números
        if ((charCode >= 48 && charCode <= 57) || // Números (teclado normal)
            (charCode >= 96 && charCode <= 105)) { // Números (teclado numérico)
            return true;
        }
    }

    // Bloquea cualquier otro carácter
    evt.preventDefault();
    return false;
}


export function reInitTabs(tabs_id, tab_select_id) {
    // las tabs de material con vue no funcionan bien, hay que poner esto para reiniciarlas
    const singleModalElem = document.querySelector('#' + tabs_id);
    if (singleModalElem != null) {
        const instance = M.Tabs.getInstance(singleModalElem);
        instance.select(tab_select_id)
        //se limpian las tabs para que no queden marcadas de antes
        if (JQuery('.indicator').length > 1) {
            JQuery('.indicator').first().remove()
        }
    }
}

export function initCollapsibleMenu() {
    const coll = document.getElementsByClassName("collapsible-header");
    for (let i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function () {
            coll[i].classList.toggle("active");
            const content = coll[i].nextElementSibling as HTMLElement;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }
}

export function validateCorrectFile(actualFile, self) {
    const size = 20;
    const max_img_size = 1048576 * size; //1MB * tamano
    if (actualFile) {
        if (actualFile.size > max_img_size) {
            showAlertError(self.$t('views.El documento tiene que tener un tamaño menor de'), self)
            return false;
        }

        const lector = new FileReader();
        return new Promise((resolve) => {
            lector.onloadend = () => {
                let type = ""
                const bytes = new Uint8Array(lector.result as ArrayBuffer);
                for (let i = 0; i < bytes.length; i++) {
                    type += bytes[i].toString(16);
                }
                switch (type) {
                    case "89504e47":
                        type = "image/png";
                        break;
                    case "47494638":
                        type = "image/gif";
                        break;
                    case "ffd8ffe0":
                    case "ffd8ffe1":
                    case "ffd8ffe2":
                    case "ffd8ffe3":
                    case "ffd8ffe8":
                    case "ffd8ffdb":
                    case "ffd8ffee":
                        type = "image/jpeg";
                        break;
                    default:
                        type = "unknown"; // Or you can use the blob.type as fallback
                        break;
                }

                console.log(type)
                if (type === "unknown") {
                    showAlertError(self.$t('views.Tipo de fichero no válido, tiene que ser jpg, jpeg, gif, png'), self)
                    resolve(false);
                } else {
                    resolve(true);
                }
            };
            lector.readAsArrayBuffer(actualFile.slice(0, 4));
        });
    }
}

export function download_table_as_csv(table_id, separator = ',', filename = 'export_') {
    // Select rows from table_id
    const rows = document.querySelectorAll('table#' + table_id + ' tr');
    // Construct csv
    const csv = [];
    for (let i = 0; i < rows.length; i++) {
        const row = [], cols = rows[i].querySelectorAll('td, th');
        for (let j = 0; j < cols.length; j++) {
            // Clean innertext to remove multiple spaces and jumpline (break csv)
            const aux = cols[j] as HTMLElement
            let data = aux.innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' ');
            // Escape double-quote with double-double-quote (see https://stackoverflow.com/questions/17808511/properly-escape-a-double-quote-in-csv)
            data = data.replace(/"/g, '""');
            // Push escaped string
            row.push('"' + data + '"');
        }
        csv.push(row.join(separator));
    }
    const csv_string = csv.join('\n');
    // Download it
    //filename = filename + '_' + new Date().toLocaleDateString() + '.csv';
    const link = document.createElement('a');
    link.style.display = 'none';
    link.setAttribute('target', '_blank');
    link.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv_string));
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}


export function downloadFile(fileData, filename, id) {
    const extensionMatch = filename.match(/\.([^.]+)$/);
    if (extensionMatch && extensionMatch.length > 1) {
        const extension = extensionMatch[1].toLowerCase();
        const linkSource = constructFileURL(filename, fileData, extension)
        if (linkSource) {
            const downloadLink = document.createElement("a");
            const fileName = id + "." + extension;
            downloadLink.href = linkSource;
            downloadLink.download = fileName;
            downloadLink.click();
        }
    }
}

export function downloadPDF(base64: string, nombreArchivo: string) {
    // Convertir Base64 a bytes
    const bytes = Uint8Array.from(atob(base64), c => c.charCodeAt(0));

    // Crear un Blob con tipo MIME de PDF
    const blob = new Blob([bytes], { type: "application/pdf" });

    // Crear un enlace temporal para descargar
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = nombreArchivo;
    document.body.appendChild(link);
    link.click();

    // Limpiar
    link.remove();
    URL.revokeObjectURL(link.href);
}

function constructFileURL(filename: string, fileData: string, extension: string): string | null {
    switch (extension) {
        case 'pdf':
            return `data:application/pdf;base64,${fileData}`;
        case 'jpeg':
        case 'jpg':
            return `data:image/jpeg;base64,${fileData}`;
        case 'png':
            return `data:image/png;base64,${fileData}`;
        default:
            return null; // Tipo de archivo desconocido
    }
}


export function chartOptions(chart_xaxis) {
    return {
        chart: {
            type: 'line',
            toolbar: {
                tools: {
                    zoomin: `<svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" viewBox="0 0 24 24">
                              <path d="M0 0h24v24H0z" fill="none"></path>
                              <path d="M13 7h-2v4H7v2h4v4h2v-4h4v-2h-4V7zm-1-5C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"></path>
                          </svg>`,
                    zoomout: `<svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" viewBox="0 0 24 24">
                              <path d="M0 0h24v24H0z" fill="none"></path>
                              <path d="M7 11v2h10v-2H7zm5-9C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"></path>
                          </svg>`,
                    zoom: `<svg xmlns="http://www.w3.org/2000/svg" fill="#000000" height="34" viewBox="0 0 24 24" width="34">
                            <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"></path>
                            <path d="M0 0h24v24H0V0z" fill="none"></path>
                            <path d="M12 10h-2v2H9v-2H7V9h2V7h1v2h2v1z"></path>
                        </svg>`,
                    pan: `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" fill="#000000" height="34" viewBox="0 0 24 24" width="34">
                            <defs>
                                <path d="M0 0h24v24H0z" id="a"></path>
                            </defs>
                            <clipPath id="b">
                                <use overflow="visible" xlink:href="#a"></use>
                            </clipPath>
                            <path clip-path="url(#b)" d="M23 5.5V20c0 2.2-1.8 4-4 4h-7.3c-1.08 0-2.1-.43-2.85-1.19L1 14.83s1.26-1.23 1.3-1.25c.22-.19.49-.29.79-.29.22 0 .42.06.6.16.04.01 4.31 2.46 4.31 2.46V4c0-.83.67-1.5 1.5-1.5S11 3.17 11 4v7h1V1.5c0-.83.67-1.5 1.5-1.5S15 .67 15 1.5V11h1V2.5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5V11h1V5.5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5z"></path>
                        </svg>`,
                    reset: `<svg fill="#000000" height="34" viewBox="0 0 24 24" width="34" xmlns="http://www.w3.org/2000/svg">
                            <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"></path>
                            <path d="M0 0h24v24H0z" fill="none"></path>
                        </svg>`,
                    download: `<svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" viewBox="0 0 24 24"><path fill="none" d="M0 0h24v24H0V0z"></path><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"></path></svg>`
                },
                autoSelected: 'zoom'
            },
        },
        stroke: {
            curve: 'stepline',
        },
        dataLabels: {
            enabled: true,
            style: {
                colors: ['#4f2d7f', '#6c6a6a', '#8ee83a']
            }
        },
        xaxis: {
            type: 'datetime',
            categories: chart_xaxis
        },
        legend: {
            position: 'top',
        },
        colors: ['#4f2d7f', '#6c6a6a', '#8ee83a'],
        tooltip: {
            x: {
                format: 'dd/MM/yy HH:mm'
            },
        }
    }
}

export function chartOptionsDonut() {
    return {
        chart: {
            type: 'donut',
        },
        legend: {
            show: true,
            //width: '30%'
        },
        fill: {
            type: 'gradient',
        },
        plotOptions: {
            pie: {
                donut: {
                    size: "55%",
                    labels: {
                        show: true,
                        total: {
                            showAlways: true,
                            show: true,
                            formatter: function (w) {
                                const total = w.globals.seriesTotals.reduce((a, b) => a + b, 0);
                                return formatNumber(total); // Formatea el total con 2 decimales
                            }
                        }
                    }
                }
            }
        },
    }
}

