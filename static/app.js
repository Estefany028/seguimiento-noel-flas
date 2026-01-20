const tbodyExterno = document.querySelector("#tablaExterno tbody");
const contSolicitudes = document.getElementById("contenedorSolicitudes");

let ADMIN_TOKEN = "";
let personas = [];

function badge(text) {
  if (text === "CUMPLE" || text === "VIGENTE" || text === "LISTO") {
    return `<span class="badge ok">${text}</span>`;
  }
  if (text === "NO CUMPLE" || text === "VENCIDA") {
    return `<span class="badge bad">${text}</span>`;
  }
  return `<span class="badge warn">${text || ""}</span>`;
}

/* ===== Modal externo ===== */
window.mostrarDetalle = function(motivo) {
  document.getElementById("modalMotivo").innerText = "❌ " + (motivo || "");
  document.getElementById("modal").style.display = "block";
};
window.cerrarModal = function() {
  document.getElementById("modal").style.display = "none";
};

/* ===== Externo ===== */
function renderExterno(data) {
  const tbody = tbodyExterno;
  tbody.innerHTML = "";

  data.forEach(p => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${p.nombre || ""}</td>
      <td>${p.cedula || ""}</td>
      <td>${p.empresa || ""}</td>
      <td>${badge(p.certificados)}</td>
      <td>${badge(p.induccion)}</td>
      <td>${badge(p.seguridadSocial)}</td>
      <td>
        ${p.estado === "REVISAR"
          ? `<span class="badge warn" style="cursor:pointer"
              onclick="mostrarDetalle('${String(p.motivo || "").replace(/'/g, "\\'")}')">REVISAR</span>`
          : `<span class="badge ok">CUMPLE</span>`
        }
      </td>
    `;
    tbody.appendChild(tr);
  });
}

async function cargarExterno() {
  const r = await fetch("/api/external");
  const data = await r.json();
  personas = data;
  renderExterno(personas);

  // estado actualización (simple)
  const el = document.getElementById("estadoActualizacion");
  el.innerText = `Actualizado: ${new Date().toLocaleString()}`;
}

/* ===== Admin ===== */
function mostrarVistaAdmin() {
  document.getElementById("vistaAdmin").classList.remove("hidden");
  document.getElementById("vistaExterno").classList.add("hidden");
}

function mostrarVistaExterno() {
  document.getElementById("vistaAdmin").classList.add("hidden");
  document.getElementById("vistaExterno").classList.remove("hidden");
}

async function cargarAdmin() {
  const r = await fetch("/api/admin/solicitudes", {
    headers: { "X-ADMIN-TOKEN": ADMIN_TOKEN }
  });

  if (r.status === 403) {
    document.getElementById("modo").innerText = "⛔ Token inválido";
    mostrarVistaExterno();
    return false;
  }

  const solicitudes = await r.json();

  document.getElementById("modo").innerText = "✅ Modo Admin";
  mostrarVistaAdmin();
  contSolicitudes.innerHTML = "";

  if (!solicitudes.length) {
    contSolicitudes.innerHTML = `<div class="card"><div class="card-head"><strong>No hay solicitudes activas.</strong><div></div></div></div>`;
    return true;
  }

  solicitudes.forEach(sol => {
    const card = document.createElement("div");
    card.className = "card";

    card.innerHTML = `
      <div class="card-head">
        <div>
          <strong>${sol.empresa || ""}</strong> · NIT: ${sol.nit || ""}
          <div style="font-size:12px; color:#666; margin-top:4px;">
            🕒 ${sol.horaIngreso || ""} - ${sol.horaSalida || ""} · 🔁 Turno: ${sol.turno || ""} · 📅 ${sol.fechaInicio || ""} → ${sol.fechaFin || ""}
          </div>
        </div>
        <div class="flecha">▶</div>
      </div>

      <div class="meta">
        <span>🧩 ${sol.tipoTrabajo || ""}</span>
        <span>📞 Ext: ${sol.extension || ""}</span>
        <span>👷 Interventor: ${sol.interventor || ""}</span>
      </div>

      <div class="people">
        <table>
          <thead>
            <tr>
              <th>Nombre</th><th>CC</th><th>Cert.</th><th>Ind.</th><th>SS</th><th>Estado</th><th>Consecutivo</th><th>Acción</th>
            </tr>
          </thead>
          <tbody>
            ${(sol.personas || []).map(p => `
              <tr>
                <td>${p.nombre || ""}</td>
                <td>${p.cedula || ""}</td>
                <td>${badge(p.certificados)}</td>
                <td>${badge(p.induccion)}</td>
                <td>${badge(p.seguridadSocial)}</td>
                <td>${badge(p.estado)}</td>
                <td><input data-row="${p.row}" value="${p.consecutivo || ""}" placeholder="Ej: 3553"></td>
                <td><button type="button" onclick="guardarConsecutivo(${p.row}, this)">Guardar</button></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;

    card.querySelector(".card-head").addEventListener("click", () => {
      card.classList.toggle("open");
    });

    contSolicitudes.appendChild(card);
  });

  return true;
}

window.guardarConsecutivo = async function(row, btn) {
  const input = document.querySelector(`input[data-row="${row}"]`);
  const consecutivo = (input?.value || "").trim();
  if (!consecutivo) return alert("Consecutivo vacío");

  btn.disabled = true;

  const r = await fetch("/api/admin/consecutivo", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-ADMIN-TOKEN": ADMIN_TOKEN
    },
    body: JSON.stringify({ row, consecutivo })
  });

  btn.disabled = false;

  if (!r.ok) {
    const out = await r.json().catch(() => ({}));
    alert("No se pudo guardar: " + (out.error || "Error"));
    return;
  }
  alert("✅ Consecutivo guardado");
};

/* ===== UI ===== */
document.getElementById("btnEntrarAdmin").addEventListener("click", async () => {
  ADMIN_TOKEN = document.getElementById("adminToken").value.trim();
  if (!ADMIN_TOKEN) return alert("Ingresa el token admin");
  await cargarAdmin();
});

document.getElementById("buscador").addEventListener("input", e => {
  const q = e.target.value.trim();
  renderExterno(personas.filter(p => String(p.cedula || "").includes(q)));
});

/* ===== Init ===== */
(async function init() {
  mostrarVistaExterno();
  await cargarExterno();
})();

