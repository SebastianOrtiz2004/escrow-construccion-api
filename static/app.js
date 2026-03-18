const API_URL = 'http://localhost:8000';

let currentUser = null;
let usuariosGlobales = [];

// ---- Inicialización ----
window.onload = async () => {
    await cargarUsuariosGlobales();
    llenarSelectLogin();
};

async function recargarDatos(){
    await cargarUsuariosGlobales();
    const userUpdated = usuariosGlobales.find(u => u.id === currentUser.id);
    if(userUpdated) currentUser = userUpdated;
    actualizarHeader();
    await cargarDashboard();
}

// ---- Modales y Utilidades ----
function showScreen(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
});

function Toast(msg, icon='success') {
    Swal.fire({ toast: true, position: 'top-end', icon, title: msg, showConfirmButton: false, timer: 3000, background: '#1e242d', color: '#fff' });
}

// ---- Autenticación Simulada ----
async function cargarUsuariosGlobales() {
    try {
        const res = await fetch(`${API_URL}/usuarios/`);
        usuariosGlobales = await res.json();
    } catch(e) { console.error(e); }
}

function llenarSelectLogin() {
    const select = document.getElementById('loginSelect');
    select.innerHTML = '<option value="">-- Cuentas Existentes --</option>';
    usuariosGlobales.forEach(u => {
        select.innerHTML += `<option value="${u.id}">${u.nombre} (${u.rol})</option>`;
    });
}

function login() {
    const id = document.getElementById('loginSelect').value;
    if(!id) return Toast('Selecciona una cuenta', 'warning');
    currentUser = usuariosGlobales.find(u => u.id == id);
    
    document.getElementById('cMaestroSelect').innerHTML = '<option value="">-- Selecciona Maestro --</option>';
    usuariosGlobales.filter(u => u.rol === 'MAESTRO').forEach(m => {
        document.getElementById('cMaestroSelect').innerHTML += `<option value="${m.id}">${m.nombre}</option>`;
    });

    actualizarHeader();
    showScreen('dashboard-screen');
    cargarDashboard();
}

function logout() {
    currentUser = null;
    showScreen('login-screen');
    llenarSelectLogin();
}

async function crearUsuario() {
    const nombre = document.getElementById('nuevoNombre').value;
    const rol = document.getElementById('nuevoRol').value;
    if(!nombre) return Toast('Ingresa un nombre', 'warning');

    try {
        const res = await fetch(`${API_URL}/usuarios/`, { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({nombre, rol}) });
        const data = await res.json();
        Toast(`Cuenta creada para ${data.nombre}`);
        await cargarUsuariosGlobales();
        llenarSelectLogin();
        document.getElementById('loginSelect').value = data.id;
        login();
    } catch (e) { Toast('Error', 'error'); }
}

function actualizarHeader() {
    document.getElementById('headerName').innerText = `${currentUser.nombre} | ${currentUser.rol}`;
    document.getElementById('walletBalance').innerText = formatter.format(currentUser.saldo_billetera).replace('$', '');
    
    // Configurar vista según rol
    const panelCreator = document.getElementById('creatorPanel');
    if (currentUser.rol === 'CLIENTE') {
        panelCreator.classList.remove('hidden');
    } else {
        panelCreator.classList.add('hidden');
    }
}

async function recargarBilletera() {
    const monto = document.getElementById('recargaMonto').value;
    if(!monto || monto <= 0) return Toast('Monto inválido', 'warning');
    
    try {
        await fetch(`${API_URL}/usuarios/${currentUser.id}/agregar_saldo?monto=${monto}`, { method: 'POST' });
        Toast('Saldo Transferido al Banco');
        recargarDatos();
        document.getElementById('recargaMonto').value = "";
    } catch(e) { Toast('Error al recargar', 'error'); }
}

// ---- Logica de Contratos y Dashboard ----
async function crearContrato() {
    const titulo = document.getElementById('cTitulo').value;
    const desc = document.getElementById('cDesc').value;
    const mId = document.getElementById('cMaestroSelect').value;
    if(!titulo || !mId) return Toast('Llenar Título y seleccionar Maestro', 'warning');

    const payload = { titulo, descripcion: desc, cliente_id: currentUser.id, maestro_id: parseInt(mId) };
    try {
        const res = await fetch(`${API_URL}/contratos/`, { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        if(res.ok) {
            Toast('Contrato Redactado Oficialmente');
            document.getElementById('cTitulo').value = '';
            document.getElementById('cDesc').value = '';
            cargarDashboard();
        }
    } catch(e) { Toast('Error', 'error'); }
}

async function cargarDashboard() {
    try {
        const res = await fetch(`${API_URL}/usuarios/${currentUser.id}/contratos`);
        const contratos = await res.json();
        
        const grid = document.getElementById('contractsList');
        grid.innerHTML = '';
        
        if (contratos.length === 0) {
            grid.innerHTML = `<p style="grid-column: 1/-1; text-align: center; margin-top: 2rem;">No tienes contratos activos aún.</p>`;
            return;
        }

        contratos.forEach(c => {
            const isCliente = currentUser.rol === 'CLIENTE';
            const otraParte = isCliente ? usuariosGlobales.find(u=>u.id==c.maestro_id)?.nombre : usuariosGlobales.find(u=>u.id==c.cliente_id)?.nombre;
            const rolOtraParte = isCliente ? "Maestro" : "Cliente";

            let hitosHtml = '';
            let totalAsignado = 0;
            
            c.hitos.forEach(h => {
                totalAsignado += h.monto_asignado;
                
                let btnHtml = '';
                let colorDot = '#8b949e'; // Pendiente
                
                if (h.estado === 'PENDIENTE') {
                    if (!isCliente && c.estado === 'FONDEADO') {
                        btnHtml = `<button class="btn btn-small btn-warning" onclick="enviarRevision(${h.id})">Entregar Trabajo</button>`;
                    }
                } else if (h.estado === 'EN_REVISION') {
                    colorDot = '#d29922';
                    if (isCliente) {
                        btnHtml = `<button class="btn btn-small btn-success" onclick="aprobarHito(${h.id})">Aprobar (${formatter.format(h.monto_asignado)})</button>`;
                    } else {
                        btnHtml = `<span style="font-size:0.8rem; color:var(--warning)">El Cliente está revisando...</span>`;
                    }
                } else if (h.estado === 'PAGADO') {
                    colorDot = '#2ea043';
                    btnHtml = `<span style="font-size:0.8rem; color:var(--success)">PAGADO ✓</span>`;
                }

                hitosHtml += `
                    <div class="hito-item">
                        <div class="hito-info">
                            <strong><span class="dot" style="background:${colorDot}"></span> ${h.descripcion}</strong>
                            <span>${formatter.format(h.monto_asignado)}</span>
                        </div>
                        <div class="hito-actions">${btnHtml}</div>
                    </div>
                `;
            });

            // Botón superior de Contrato
            let contratoBtn = '';
            if (c.estado === 'BORRADOR') {
                if (isCliente) {
                    contratoBtn = `
                        <button class="btn btn-small" style="background:rgba(255,255,255,0.1)" onclick="abrirModalHito(${c.id}, '${c.titulo}')">Añadir Hito</button>
                        <button class="btn btn-small btn-primary" onclick="fondearContrato(${c.id})">💰 Fondear Escrow (${formatter.format(totalAsignado)})</button>
                    `;
                } else {
                    contratoBtn = `<span style="font-size:0.8rem; color:#8b949e">Esperando que el cliente fondee</span>`;
                }
            }

            grid.innerHTML += `
                <div class="contract-card">
                    <div class="c-header">
                        <div>
                            <div class="c-title">${c.titulo}</div>
                            <div class="c-desc">${rolOtraParte}: ${otraParte}</div>
                        </div>
                        <div class="c-status status-${c.estado}">${c.estado}</div>
                    </div>
                    <div class="c-body">
                        <div class="c-box">
                            <span>Bóveda Escrow:</span>
                            <span class="escrow-amount">🔒 ${formatter.format(c.saldo_retenido)}</span>
                        </div>
                        <div style="display:flex; justify-content: space-between; align-items:flex-end;">
                           <p style="margin:0; font-size:0.85rem; padding-top:1rem; opacity:0.6;">Total Proyecto: ${formatter.format(totalAsignado)}</p>
                           ${contratoBtn}
                        </div>
                    </div>
                    ${hitosHtml ? `<div class="hitos-list">${hitosHtml}</div>` : '<p style="text-align:center; padding: 1rem; color:var(--text-muted)">Sin hitos aún</p>'}
                </div>
            `;
        });
    } catch(e) { console.error(e); Toast('Error cargando contratos', 'error'); }
}

// ---- Transacciones Escrow ----
async function fondearContrato(id) {
    Swal.fire({
        title: '¿Bloquear fondos en Escrow?',
        text: "El Smart Contract debitará de tu billetera y asegurará los fondos en la bóveda.",
        icon: 'info',
        showCancelButton: true,
        confirmButtonText: 'Sí, Bloquear',
        cancelButtonText: 'Cancelar',
        background: '#1e242d', color: '#fff'
    }).then(async (result) => {
        if (result.isConfirmed) {
            try {
                const res = await fetch(`${API_URL}/contratos/${id}/fondear`, { method: 'POST' });
                if(res.ok) { Toast('Contrato Fondeado Exitosamente!'); recargarDatos(); }
                else { const e = await res.json(); Toast(e.detail, 'error'); }
            } catch(e) { Toast('Error de red', 'error'); }
        }
    });
}

async function enviarRevision(id) {
    try {
        const res = await fetch(`${API_URL}/hitos/${id}/enviar_revision`, { method: 'POST' });
        if(res.ok) { Toast('Evidencia enviada al cliente para revisión'); recargarDatos(); }
    } catch(e) { Toast('Error', 'error'); }
}

async function aprobarHito(id) {
    Swal.fire({
        title: '¿Aprobar Trabajo?',
        text: "Fondos se liberarán irrevocablemente al Maestro.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#2ea043',
        confirmButtonText: 'Aprobar y Pagar',
        background: '#1e242d', color: '#fff'
    }).then(async (result) => {
        if (result.isConfirmed) {
            try {
                const res = await fetch(`${API_URL}/hitos/${id}/aprobar`, { method: 'POST' });
                if(res.ok) { Toast('¡Pago liberado exitosamente!'); recargarDatos(); }
                else { const e = await res.json(); Toast(e.detail, 'error'); }
            } catch(e) { Toast('Error de red', 'error'); }
        }
    });
}

// Config Hito Modal
let currentHitoContrato = null;
function abrirModalHito(contratoId, titulo) {
    currentHitoContrato = contratoId;
    document.getElementById('hitoModalText').innerText = `Contrato: ${titulo}`;
    document.getElementById('hitoModal').classList.add('flex');
}
function cerrarModal() {
    currentHitoContrato = null;
    document.getElementById('hDesc').value = '';
    document.getElementById('hMonto').value = '';
    document.getElementById('hitoModal').classList.remove('flex');
}
async function guardarHito() {
    const desc = document.getElementById('hDesc').value;
    const monto = document.getElementById('hMonto').value;
    if(!desc || !monto) return Toast('Completa los campos', 'warning');
    
    try {
        const res = await fetch(`${API_URL}/contratos/${currentHitoContrato}/hitos/`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({descripcion: desc, monto_asignado: parseFloat(monto)})
        });
        if(res.ok) { Toast('Hito Creado'); cerrarModal(); recargarDatos(); }
    } catch(e) { Toast('Error', 'error'); }
}
