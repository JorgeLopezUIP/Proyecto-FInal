(function () {
  "use strict";

  const state = { paqueteActual: null };

  const ESTADO_CLASE = {
    "recibido en bodega": "st-recibido",
    "en transito": "st-transito",
    "en aduana": "st-aduana",
    "listo para retiro": "st-listo",
  };

  const ESTADO_LABEL = {
    "recibido en bodega": "Recibido en bodega",
    "en transito": "En tránsito",
    "en aduana": "En aduana",
    "listo para retiro": "Listo para retiro",
  };

  function badgeEstado(estado) {
    const clase = ESTADO_CLASE[estado] || "st-recibido";
    const label = ESTADO_LABEL[estado] || estado;
    return `<span class="badge ${clase}">${label}</span>`;
  }

  async function buscar() {
    const params = new URLSearchParams();
    const q = document.getElementById("f-buscar").value.trim();
    const estado = document.getElementById("f-estado").value;
    const metodo = document.getElementById("f-metodo").value;
    const orden = document.getElementById("f-orden").value;
    if (q) params.set("q", q);
    if (estado) params.set("estado", estado);
    if (metodo) params.set("metodo", metodo);
    if (orden) params.set("orden", orden);

    const cuerpoTabla = document.getElementById("tabla-paquetes-body");
    cuerpoTabla.innerHTML = "";

    try {
      const res = await fetch("/api/paquetes?" + params.toString());
      const data = await res.json();

      if (!res.ok) {
        document.getElementById("contador-resultados").textContent = "error";
        document.getElementById("empty-hint").style.display = "block";
        document.getElementById("empty-hint").textContent = data.error || "No se pudo consultar la base de datos.";
        return;
      }

      const paquetes = data.paquetes || [];
      document.getElementById("contador-resultados").textContent = paquetes.length + " resultados";
      document.getElementById("empty-hint").style.display = paquetes.length ? "none" : "block";
      document.getElementById("empty-hint").textContent = "No se encontraron paquetes con esos filtros.";

      paquetes.forEach((p) => {
        const tr = document.createElement("tr");
        tr.className = "fila-paquete";
        tr.innerHTML = `
          <td>${p.tracking}</td>
          <td>${p.cliente_nombre}</td>
          <td>${p.categoria}</td>
          <td>${p.peso} kg</td>
          <td>${p.metodo_de_llegada}</td>
          <td>${badgeEstado(p.estado)}</td>
          <td>${p.fecha_de_recepcion || ""}</td>
        `;
        tr.addEventListener("click", () => abrirDetalle(p.id));
        cuerpoTabla.appendChild(tr);
      });
    } catch (err) {
      document.getElementById("empty-hint").style.display = "block";
      document.getElementById("empty-hint").textContent = "No se pudo conectar con el servidor.";
    }
  }

  async function abrirDetalle(id) {
    const res = await fetch(`/api/paquetes/${id}`);
    const data = await res.json();

    if (!res.ok) {
      alert(data.error || "No se pudo cargar el paquete");
      return;
    }

    state.paqueteActual = data.paquete;

    document.getElementById("pd-tracking").textContent = data.paquete.tracking;
    document.getElementById("pd-recepcion").textContent =
      "Recibido: " + (data.paquete.fecha_de_recepcion || "—");
    document.getElementById("pd-cliente-nombre").textContent = data.paquete.cliente_nombre;
    document.getElementById("pd-cliente-cedula").textContent = data.paquete.cedula_pasaporte;
    document.getElementById("pd-categoria").textContent = data.paquete.categoria || "—";

    const fmtDim = (v) => (v === null || v === undefined || v === "") ? "No registrado" : `${v} cm`;
    document.getElementById("pd-largo").textContent = fmtDim(data.paquete.largo);
    document.getElementById("pd-ancho").textContent = fmtDim(data.paquete.ancho);
    document.getElementById("pd-alto").textContent = fmtDim(data.paquete.alto);

    if (data.zona) {
      document.getElementById("pd-zona").textContent = data.zona.zona_nombre;
    } else {
      document.getElementById("pd-zona").textContent = "El cliente no tiene zona asignada";
    }

    if (data.tarifa) {
      document.getElementById("pd-tarifa").textContent = "$" + data.tarifa.precio.toFixed(2);
      document.getElementById("pd-tarifa-tipo").textContent = data.tarifa.tipo_servicio;
    } else {
      document.getElementById("pd-tarifa").textContent = "No disponible";
      document.getElementById("pd-tarifa-tipo").textContent = "";
    }

    document.getElementById("d-peso").value = data.paquete.peso ?? "";
    document.getElementById("d-largo").value = data.paquete.largo ?? "";
    document.getElementById("d-ancho").value = data.paquete.ancho ?? "";
    document.getElementById("d-alto").value = data.paquete.alto ?? "";
    document.getElementById("d-metodo").value = data.paquete.metodo_de_llegada;
    document.getElementById("d-estado").value = data.paquete.estado;
    document.getElementById("d-descripcion").value = data.paquete.descripcion || "";
    document.getElementById("d-notificar").checked = true;

    ocultarEmailStatus();

    const eventos = document.getElementById("pd-eventos");
    eventos.innerHTML = "";
    if (!data.eventos || !data.eventos.length) {
      eventos.innerHTML = '<div class="log-line"><span>Sin eventos registrados.</span></div>';
    } else {
      data.eventos.forEach((ev) => {
        const linea = document.createElement("div");
        linea.className = "log-line";
        linea.innerHTML = `<span>${ev.fecha} — ${ESTADO_LABEL[ev.estado] || ev.estado}${ev.comentario ? " · " + ev.comentario : ""}</span>`;
        eventos.appendChild(linea);
      });
    }

    document.getElementById("overlay").classList.add("is-open");
    document.getElementById("panel-detalle").classList.add("is-open");
  }

  function cerrarDetalle() {
    document.getElementById("overlay").classList.remove("is-open");
    document.getElementById("panel-detalle").classList.remove("is-open");
    state.paqueteActual = null;
  }

  function mostrarEmailStatus(enviado, mensaje) {
    const el = document.getElementById("email-status");
    el.textContent = (enviado ? "Correo enviado — " : "Correo no enviado — ") + mensaje;
    el.className = "email-status " + (enviado ? "ok" : "fail");
  }

  function ocultarEmailStatus() {
    const el = document.getElementById("email-status");
    el.className = "email-status";
    el.textContent = "";
  }

  async function guardarCambios(ev) {
    ev.preventDefault();
    if (!state.paqueteActual) return;

    const payload = {
      peso: document.getElementById("d-peso").value,
      largo: document.getElementById("d-largo").value,
      ancho: document.getElementById("d-ancho").value,
      alto: document.getElementById("d-alto").value,
      metodo_de_llegada: document.getElementById("d-metodo").value,
      descripcion: document.getElementById("d-descripcion").value,
      estado: document.getElementById("d-estado").value,
      notificar: document.getElementById("d-notificar").checked,
    };

    const res = await fetch(`/api/paquetes/${state.paqueteActual.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      alert(data.error || "No se pudo guardar el cambio");
      return;
    }

    const idGuardado = state.paqueteActual.id;

    // Volvemos a abrir el detalle del mismo paquete: esto recalcula y
    // refresca la tarifa mostrada (depende del peso, que puede haber
    // cambiado), el historial de tracking y el resto de los campos.
    await abrirDetalle(idGuardado);

    if (data.email) {
      mostrarEmailStatus(data.email.enviado, data.email.mensaje);
    }

    buscar();
  }

  async function reenviarNotificacion() {
    if (!state.paqueteActual) return;
    const res = await fetch(`/api/paquetes/${state.paqueteActual.id}/notificar`, { method: "POST" });
    const data = await res.json();

    if (!res.ok) {
      alert(data.error || "No se pudo reenviar la notificación");
      return;
    }
    mostrarEmailStatus(data.enviado, data.mensaje);
  }

  async function eliminarPaquete() {
    if (!state.paqueteActual) return;

    const tracking = state.paqueteActual.tracking;
    const confirmado = confirm(
      `¿Eliminar el paquete ${tracking}? Esta acción no se puede deshacer ` +
      `(también se borra su historial de tracking).`
    );
    if (!confirmado) return;

    const res = await fetch(`/api/paquetes/${state.paqueteActual.id}`, { method: "DELETE" });
    const data = await res.json();

    if (!res.ok) {
      alert(data.error || "No se pudo eliminar el paquete");
      return;
    }

    cerrarDetalle();
    buscar();
  }

  async function eliminarTodosLosPaquetes() {
    const confirmado = confirm(
      "¿Eliminar TODOS los paquetes de la base de datos? Esta acción no se " +
      "puede deshacer y borra también todo el historial de tracking."
    );
    if (!confirmado) return;

    const res = await fetch("/api/paquetes", { method: "DELETE" });
    const data = await res.json();

    if (!res.ok) {
      alert(data.error || "No se pudieron eliminar los paquetes");
      return;
    }

    cerrarDetalle();
    buscar();
  }

  document.getElementById("btn-buscar").addEventListener("click", buscar);
  document.getElementById("f-orden").addEventListener("change", buscar);
  document.getElementById("f-buscar").addEventListener("keydown", (e) => {
    if (e.key === "Enter") buscar();
  });
  document.getElementById("pd-close").addEventListener("click", cerrarDetalle);
  document.getElementById("overlay").addEventListener("click", cerrarDetalle);
  document.getElementById("form-editar").addEventListener("submit", guardarCambios);
  document.getElementById("btn-reenviar").addEventListener("click", reenviarNotificacion);
  document.getElementById("btn-eliminar-paquete").addEventListener("click", eliminarPaquete);
  document.getElementById("btn-eliminar-todos").addEventListener("click", eliminarTodosLosPaquetes);

  buscar();
})();
