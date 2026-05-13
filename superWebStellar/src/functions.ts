import M from "materialize-css";
import JQuery from "jquery";
import InvestServices from "@/services/InvestServices";
import UserServices from "@/services/UserServices";
import store from "@/store";
import { Locales } from "@/locales/locales";


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
        if (error.toString().includes('Cannot read properties of undefined') || error.toString().includes('AxiosError: Network Error')) {
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


export function showAlertProgress(_this) {
    const elems = document.querySelectorAll('.modal');
    M.Modal.init(elems, { dismissible: false });


    const singleModalElem = document.querySelector('#modal_progress');
    if (singleModalElem != null) {
        const instance = M.Modal.getInstance(singleModalElem);

        instance.open();
    }
}

export function closeAlertProgress(_this) {
    const elems = document.querySelectorAll('.modal');
    M.Modal.init(elems, { dismissible: true });


    const singleModalElem = document.querySelector('#modal_progress');
    if (singleModalElem != null) {
        const instance = M.Modal.getInstance(singleModalElem);

        instance.close();
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

export function showAlertKYC() {
    const elems = document.querySelectorAll('.modal');
    M.Modal.init(elems, { dismissible: false });
    const singleModalElem = document.querySelector('#modal_alert_kyc');
    if (singleModalElem != null) {
        const instance = M.Modal.getInstance(singleModalElem);
        instance.open();
    }
}


export function checkKYCValid(self) {
    //se comprueba siempre que el KYC se valido
    UserServices.getIfKYCValid()
        .then(response => {
            store.commit('KYC_VALID', response.data.kyc_valid)

            self.kyc_valid = response.data.kyc_valid
            self.kyc_no_valid_reason = response.data.kyc_no_valid_reason
            if (store.getters.getLocale == Locales.EN) {
                self.kyc_no_valid_reason = response.data.kyc_no_valid_reason_EN
            }
            if (self.kyc_valid != 1) {
                showAlertKYC();
            } else {
                if (self.getData != undefined) {
                    self.getData()
                }
            }
        })
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
        }
        if (document.getElementById("date_fin") != null) {
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

export function followsInvest(invest_id, _this) {
    //follow or unfollow invest
    if (JQuery('#followsInvest_' + invest_id).html() == 'favorite') {
        InvestServices.deleteFollows(invest_id)
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            .then(response => {
                showAlert(_this.$t("views.Mi lista de proyectos favoritos"), _this.$t("views.Has eliminado el proyecto de tu lista de favoritos"))
                JQuery('#followsInvest_' + invest_id).html('favorite_border')
            })
            .catch(function (error) {
                showAlertError(error, _this)
            });
    } else {
        InvestServices.postFollows(invest_id)
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            .then(response => {
                showAlert(_this.$t("views.Mi lista de proyectos favoritos"), _this.$t("views.Has añadido el proyecto a tu lista de favoritos"))
                JQuery('#followsInvest_' + invest_id).html('favorite')
            })
            .catch(function (error) {
                showAlertError(error, _this)
            });
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
    let f = "";
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
    return new Date(Date.UTC(fechaLocal.getUTCFullYear(), fechaLocal.getUTCMonth(), fechaLocal.getUTCDate(), fechaLocal.getUTCHours(), fechaLocal.getUTCMinutes())).toISOString();
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

export function formatNumber(num, decimals = 2) {
    if (num === '00000000') return num;
    if (isNaN(num)) return 0;

    return new Intl.NumberFormat('de-DE', {
        minimumFractionDigits: 0,
        maximumFractionDigits: decimals,
    }).format(num);
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
export function funcGetImgUrl(pic) {
    return '/' + 'earastellar' + (process.env.VUE_APP_WHITE_LABEL_IS_DEVELOPMENT !== "true" ? '/' : 'app/' + 'earastellar' + '/') + pic;
}

export function initStepper() {
    /**
     * Select all form navigation buttons, and loop through them.
     */
    document.querySelectorAll(".btn-navigate-form-step").forEach((formNavigationBtn) => {
        /**
         * Add a click event listener to the button.
         */
        formNavigationBtn.addEventListener("click", () => {
            /**
             * Get the value of the step.
             */
            const stepNumber = parseInt(formNavigationBtn.getAttribute("step_number"));
            /**
             * Call the function to navigate to the target form step.
             */
            navigateToFormStep(stepNumber);
        });
    });
}
/**
 * Define a function to navigate betweens form steps.
 * It accepts one parameter. That is - step number.
 */
export function navigateToFormStep(stepNumber) {
    /**
     * Hide all form steps.
     */
    document.querySelectorAll(".form-step").forEach((formStepElement) => {
        formStepElement.classList.add("d-none");
    });
    /**
     * Mark all form steps as unfinished.
     */
    document.querySelectorAll(".form-stepper-list").forEach((formStepHeader) => {
        formStepHeader.classList.add("form-stepper-unfinished");
        formStepHeader.classList.remove("form-stepper-active", "form-stepper-completed");
    });
    /**
     * Show the current form step (as passed to the function).
     */
    const stepEl = document.querySelector("#step-" + stepNumber);
    if (!stepEl) return;
    stepEl.classList.remove("d-none");
    /**
     * Select the form step circle (progress bar).
     */
    const formStepCircle = document.querySelector('li[step="' + stepNumber + '"]');
    if (!formStepCircle) return;
    /**
     * Mark the current form step as active.
     */
    formStepCircle.classList.remove("form-stepper-unfinished", "form-stepper-completed");
    formStepCircle.classList.add("form-stepper-active");
    /**
     * Loop through each form step circles.
     * This loop will continue up to the current step number.
     * Example: If the current step is 3,
     * then the loop will perform operations for step 1 and 2.
     */
    for (let index = 0; index < stepNumber; index++) {
        /**
         * Select the form step circle (progress bar).
         */
        const formStepCircle = document.querySelector('li[step="' + index + '"]');
        /**
         * Check if the element exist. If yes, then proceed.
         */
        if (formStepCircle) {
            /**
             * Mark the form step as completed.
             */
            formStepCircle.classList.remove("form-stepper-unfinished", "form-stepper-active");
            formStepCircle.classList.add("form-stepper-completed");
        }
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

export function currencySymbol(currencyCode: string): string {
    const symbols: Record<string, string> = {
        'EUR': '€',
        'USD': '$',
        'GBP': '£',
        'JPY': '¥',
        'CNY': '¥',
        'INR': '₹',
        'RUB': '₽',
        'BRL': 'R$',
        'CHF': 'CHF',
        'CAD': 'C$',
        'AUD': 'A$',
        'MXN': 'MX$',
        'PLN': 'zł',
        'SEK': 'kr',
        'NOK': 'kr',
        'DKK': 'kr',
        'BTC': '₿',
        'ETH': 'Ξ'
    };

    // Return the symbol if found, otherwise return the original currency code
    return symbols[currencyCode] || currencyCode;
}