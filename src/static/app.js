// ==========================================================================
//  Verificador de Seguridad – Robot Doméstico  (Frontend JS)
// ==========================================================================

(function () {
    "use strict";

    // ------------------------------------------------------------------
    // Referencias al DOM
    // ------------------------------------------------------------------
    const $selector      = document.getElementById("selector-escenario");
    const $btnRestaurar  = document.getElementById("btn-restaurar");
    const $btnEjecutar   = document.getElementById("btn-ejecutar");
    const $btnTema       = document.getElementById("btn-tema");
    const $editorJSON    = document.getElementById("editor-json");
    const $lineNumbers   = document.getElementById("line-numbers");
    const $editorStatus  = document.getElementById("editor-status");
    const $vistaJSON     = document.getElementById("vista-json");
    const $vistaResumen  = document.getElementById("vista-resumen");
    const $resumenContenido = document.getElementById("resumen-contenido");

    // Tabs
    const $tabs = document.querySelectorAll(".tab");

    // Resultados
    const $estadoVacio     = document.getElementById("estado-vacio");
    const $estadoCargando  = document.getElementById("estado-cargando");
    const $estadoError     = document.getElementById("estado-error");
    const $errorMensaje    = document.getElementById("error-mensaje");
    const $kpis            = document.getElementById("kpis");
    const $kpiEstado       = document.getElementById("kpi-estado");
    const $kpiEstadoValor  = document.getElementById("kpi-estado-valor");
    const $kpiTEnum        = document.getElementById("kpi-t-enum");
    const $kpiTRes         = document.getElementById("kpi-t-res");
    const $tablaPropiedades = document.getElementById("tabla-propiedades");
    const $propiedadesLista = document.getElementById("propiedades-lista");
    const $tablaMetricas   = document.getElementById("tabla-metricas");
    const $metricasBody    = document.getElementById("metricas-body");

    // ------------------------------------------------------------------
    // Estado
    // ------------------------------------------------------------------
    let escenarioOriginal = null;   // JSON descargado del servidor
    let jsonValido = false;
    let debounceTimer = null;

    // ------------------------------------------------------------------
    // Tema claro / oscuro
    // ------------------------------------------------------------------
    function initTheme() {
        const saved = localStorage.getItem("theme") || "light";
        document.documentElement.setAttribute("data-theme", saved);
        $btnTema.textContent = saved === "dark" ? "☀️" : "🌙";
    }

    $btnTema.addEventListener("click", function () {
        const current = document.documentElement.getAttribute("data-theme");
        const next = current === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("theme", next);
        $btnTema.textContent = next === "dark" ? "☀️" : "🌙";
    });

    // ------------------------------------------------------------------
    // Cargar lista de escenarios
    // ------------------------------------------------------------------
    async function cargarEscenarios() {
        try {
            const res = await fetch("/api/escenarios");
            const nombres = await res.json();
            nombres.forEach(function (nombre) {
                const opt = document.createElement("option");
                opt.value = nombre;
                opt.textContent = nombre;
                $selector.appendChild(opt);
            });
        } catch (e) {
            console.error("Error al cargar escenarios:", e);
        }
    }

    // ------------------------------------------------------------------
    // Seleccionar escenario
    // ------------------------------------------------------------------
    $selector.addEventListener("change", async function () {
        const nombre = $selector.value;
        if (!nombre) {
            $editorJSON.value = "";
            escenarioOriginal = null;
            $btnRestaurar.disabled = true;
            $btnEjecutar.disabled = true;
            actualizarLineNumbers();
            validarJSON();
            return;
        }
        try {
            const res = await fetch("/api/escenarios/" + encodeURIComponent(nombre));
            const data = await res.json();
            escenarioOriginal = data;
            $editorJSON.value = JSON.stringify(data, null, 2);
            $btnRestaurar.disabled = false;
            actualizarLineNumbers();
            validarJSON();
            actualizarResumen(data);
        } catch (e) {
            console.error("Error al cargar escenario:", e);
        }
    });

    // ------------------------------------------------------------------
    // Restaurar original
    // ------------------------------------------------------------------
    $btnRestaurar.addEventListener("click", function () {
        if (escenarioOriginal) {
            $editorJSON.value = JSON.stringify(escenarioOriginal, null, 2);
            actualizarLineNumbers();
            validarJSON();
            actualizarResumen(escenarioOriginal);
        }
    });

    // ------------------------------------------------------------------
    // Numeración de líneas
    // ------------------------------------------------------------------
    function actualizarLineNumbers() {
        const lines = $editorJSON.value.split("\n").length;
        let html = "";
        for (let i = 1; i <= lines; i++) {
            html += i + "\n";
        }
        $lineNumbers.textContent = html;
    }

    $editorJSON.addEventListener("scroll", function () {
        $lineNumbers.scrollTop = $editorJSON.scrollTop;
    });

    // ------------------------------------------------------------------
    // Validación JSON con debounce
    // ------------------------------------------------------------------
    $editorJSON.addEventListener("input", function () {
        actualizarLineNumbers();
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(validarJSON, 300);
    });

    function validarJSON() {
        const text = $editorJSON.value.trim();
        if (!text) {
            setStatus("⏳", "Sin contenido", "");
            jsonValido = false;
            $btnEjecutar.disabled = true;
            return;
        }

        try {
            const obj = JSON.parse(text);
            // Verificar claves requeridas
            const faltantes = ["variables", "reglas", "propiedades"].filter(
                function (k) { return !(k in obj); }
            );
            if (faltantes.length > 0) {
                setStatus("✕", "Faltan claves: " + faltantes.join(", "), "invalid");
                jsonValido = false;
                $btnEjecutar.disabled = true;
                return;
            }
            setStatus("✓", "JSON válido", "valid");
            jsonValido = true;
            $btnEjecutar.disabled = false;
        } catch (e) {
            const match = e.message.match(/position (\d+)/);
            let info = "Error de sintaxis";
            if (match) {
                const pos = parseInt(match[1], 10);
                const linea = text.substring(0, pos).split("\n").length;
                info += " cerca de la línea " + linea;
            }
            setStatus("✕", info, "invalid");
            jsonValido = false;
            $btnEjecutar.disabled = true;
        }
    }

    function setStatus(icon, text, cls) {
        $editorStatus.querySelector(".status-icon").textContent = icon;
        $editorStatus.querySelector(".status-text").textContent = text;
        $editorStatus.className = "editor-status" + (cls ? " " + cls : "");
    }

    // ------------------------------------------------------------------
    // Vista resumida
    // ------------------------------------------------------------------
    function actualizarResumen(data) {
        let html = "";

        // Variables
        html += "<h3>Variables (" + Object.keys(data.variables).length + ")</h3><ul>";
        for (const [nombre, info] of Object.entries(data.variables)) {
            html += '<li><span class="regla-id">' + nombre + '</span> <small>(' +
                info.tipo + ')</small> — ' + info.significado + '</li>';
        }
        html += "</ul>";

        // Reglas
        html += "<h3>Reglas (" + data.reglas.length + ")</h3><ul>";
        data.reglas.forEach(function (r) {
            html += '<li><span class="regla-id">' + r.id + ':</span> <code>' +
                r.formula + '</code> — ' + r.descripcion + '</li>';
        });
        html += "</ul>";

        // Propiedades
        html += "<h3>Propiedades (" + data.propiedades.length + ")</h3><ul>";
        data.propiedades.forEach(function (p) {
            html += '<li><span class="prop-id">' + p.id + ':</span> <code>' +
                p.formula + '</code> — ' + p.descripcion + '</li>';
        });
        html += "</ul>";

        $resumenContenido.innerHTML = html;
    }

    // ------------------------------------------------------------------
    // Tabs
    // ------------------------------------------------------------------
    $tabs.forEach(function (tab) {
        tab.addEventListener("click", function () {
            $tabs.forEach(function (t) { t.classList.remove("tab--active"); });
            tab.classList.add("tab--active");
            const target = tab.getAttribute("data-tab");
            if (target === "json") {
                $vistaJSON.hidden = false;
                $vistaResumen.hidden = true;
            } else {
                $vistaJSON.hidden = true;
                $vistaResumen.hidden = false;
            }
        });
    });

    // ------------------------------------------------------------------
    // Ejecutar verificación
    // ------------------------------------------------------------------
    $btnEjecutar.addEventListener("click", ejecutarVerificacion);

    async function ejecutarVerificacion() {
        if (!jsonValido) return;

        const escenario = JSON.parse($editorJSON.value);

        // UI: loading
        mostrarEstado("cargando");
        $btnEjecutar.disabled = true;

        try {
            const res = await fetch("/api/verificar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(escenario),
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Error del servidor");
            }

            const data = await res.json();
            renderResultados(data);
        } catch (e) {
            mostrarEstado("error");
            $errorMensaje.textContent = e.message;
        } finally {
            $btnEjecutar.disabled = false;
        }
    }

    // ------------------------------------------------------------------
    // Mostrar / ocultar estados
    // ------------------------------------------------------------------
    function mostrarEstado(estado) {
        $estadoVacio.hidden    = true;
        $estadoCargando.hidden = true;
        $estadoError.hidden    = true;
        $kpis.hidden           = true;
        $tablaPropiedades.hidden = true;
        $tablaMetricas.hidden  = true;

        switch (estado) {
            case "vacio":
                $estadoVacio.hidden = false;
                break;
            case "cargando":
                $estadoCargando.hidden = false;
                break;
            case "error":
                $estadoError.hidden = false;
                break;
            case "resultados":
                $kpis.hidden = false;
                $tablaPropiedades.hidden = false;
                $tablaMetricas.hidden = false;
                break;
        }
    }

    // ------------------------------------------------------------------
    // Renderizar resultados
    // ------------------------------------------------------------------
    function renderResultados(data) {
        mostrarEstado("resultados");

        // KPIs
        const esSeguro = data.estado_global === "SEGURO";
        $kpiEstadoValor.textContent = data.estado_global;
        $kpiEstado.className = "kpi " + (esSeguro ? "kpi--safe" : "kpi--fail");

        let totalEnum = 0;
        let totalRes = 0;
        data.propiedades.forEach(function (p) {
            totalEnum += p.enumeracion.tiempo_ms;
            totalRes += p.resolucion.tiempo_ms;
        });
        $kpiTEnum.textContent = totalEnum.toFixed(3) + " ms";
        $kpiTRes.textContent = totalRes.toFixed(3) + " ms";

        // Tarjetas de propiedades
        $propiedadesLista.innerHTML = "";
        data.propiedades.forEach(function (prop) {
            const card = document.createElement("div");
            card.className = "prop-card";

            const cumpleEnum = prop.enumeracion.se_cumple;
            const cumpleRes = prop.resolucion.se_cumple;

            // Header
            let headerHTML = '<div class="prop-card__header">';
            headerHTML += '<span class="prop-card__id">' + prop.id + '</span>';
            headerHTML += '<span class="prop-card__formula">' + escapeHTML(prop.formula) + '</span>';
            headerHTML += '<div class="prop-card__badges">';
            headerHTML += '<span class="badge ' + (cumpleEnum ? 'badge--safe' : 'badge--fail') + '">';
            headerHTML += 'Enum: ' + (cumpleEnum ? 'Cumple' : 'Falla') + '</span>';
            headerHTML += '<span class="badge ' + (cumpleRes ? 'badge--safe' : 'badge--fail') + '">';
            headerHTML += 'Res: ' + (cumpleRes ? 'Cumple' : 'Falla') + '</span>';
            headerHTML += '</div></div>';

            // Details
            let detailHTML = "<details><summary>Ver detalles</summary>";
            detailHTML += '<div class="prop-card__detail-body">';

            if (prop.descripcion) {
                detailHTML += "Descripción: " + escapeHTML(prop.descripcion) + "\n\n";
            }

            detailHTML += "── Enumeración ──\n";
            detailHTML += "Modelos evaluados: " + prop.enumeracion.modelos_evaluados + "\n";
            detailHTML += "KB consistente: " + (prop.enumeracion.kb_consistente ? "Sí" : "No") + "\n";
            if (prop.enumeracion.contraejemplo) {
                detailHTML += "Contraejemplo: " + JSON.stringify(prop.enumeracion.contraejemplo) + "\n";
            }

            detailHTML += "\n── Resolución ──\n";
            detailHTML += "Cláusulas generadas: " + prop.resolucion.clausulas_generadas + "\n";
            detailHTML += "KB consistente: " + (prop.resolucion.kb_consistente ? "Sí" : "No") + "\n";
            if (prop.resolucion.pasos && prop.resolucion.pasos.length > 0) {
                detailHTML += "Pasos de resolución:\n";
                prop.resolucion.pasos.forEach(function (paso, i) {
                    detailHTML += "  " + (i + 1) + ". " + escapeHTML(paso) + "\n";
                });
            }

            detailHTML += "</div></details>";

            card.innerHTML = headerHTML + detailHTML;
            $propiedadesLista.appendChild(card);
        });

        // Tabla de métricas
        $metricasBody.innerHTML = "";
        data.propiedades.forEach(function (prop) {
            const tr = document.createElement("tr");
            tr.innerHTML =
                "<td><strong>" + prop.id + "</strong></td>" +
                "<td>" + prop.enumeracion.tiempo_ms.toFixed(3) + "</td>" +
                "<td>" + prop.resolucion.tiempo_ms.toFixed(3) + "</td>" +
                "<td>" + prop.enumeracion.modelos_evaluados + "</td>" +
                "<td>" + prop.resolucion.clausulas_generadas + "</td>";
            $metricasBody.appendChild(tr);
        });
    }

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------
    function escapeHTML(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    // ------------------------------------------------------------------
    // Init
    // ------------------------------------------------------------------
    initTheme();
    cargarEscenarios();
    actualizarLineNumbers();
})();
