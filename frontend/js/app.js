let currentUser = null;

// ========================================
// VERIFICACIÓN INICIAL
// ========================================
console.log("✅ app.js cargado correctamente");
console.log("📍 API URL:", API_URL);

// ========================================
// UTILIDADES
// ========================================

function showTab(tab) {
    const loginForm = document.getElementById('formLogin');
    const registerForm = document.getElementById('formRegister');
    const tabs = document.querySelectorAll('.tab');
    
    tabs.forEach(t => t.classList.remove('active'));
    
    if (tab === 'login') {
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
        tabs[0].classList.add('active');
    } else {
        loginForm.classList.remove('active');
        registerForm.classList.add('active');
        tabs[1].classList.add('active');
    }
}

function showMessage(elementId, message, isError = false) {
    const el = document.getElementById(elementId);
    el.textContent = message;
    el.className = isError ? 'error' : 'message';
    setTimeout(() => el.textContent = '', 5000);
}

function formatMoney(amount) {
    return `$${parseFloat(amount).toFixed(2)}`;
}

function showMainApp() {
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('mainSection').style.display = 'block';
    document.getElementById('userName').textContent = currentUser.nombre;
    document.getElementById('fecha').valueAsDate = new Date();
    cargarResumen();
    cargarMovimientos();
}

function logout() {
    currentUser = null;
    document.getElementById('authSection').style.display = 'block';
    document.getElementById('mainSection').style.display = 'none';
    document.getElementById('formLogin').reset();
}

// ========================================
// AUTENTICACIÓN
// ========================================

document.getElementById('formLogin').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        email: document.getElementById('loginEmail').value,
        password: document.getElementById('loginPassword').value
    };
    
    try {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            currentUser = result.user;
            showMainApp();
        } else {
            showMessage('loginError', result.error, true);
        }
    } catch (error) {
        showMessage('loginError', 'Error de conexión', true);
    }
});

document.getElementById('formRegister').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const password = document.getElementById('registerPassword').value;
    
    if (password.length < 6) {
        showMessage('registerError', 'La contraseña debe tener al menos 6 caracteres', true);
        return;
    }
    
    const data = {
        nombre: document.getElementById('registerNombre').value,
        email: document.getElementById('registerEmail').value,
        password: password
    };
    
    try {
        const response = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('✅ Cuenta creada exitosamente. Ahora inicia sesión.');
            showTab('login');
            document.getElementById('formRegister').reset();
        } else {
            showMessage('registerError', result.error, true);
        }
    } catch (error) {
        showMessage('registerError', 'Error de conexión', true);
    }
});

// ========================================
// MOVIMIENTOS
// ========================================

document.getElementById('formMovimiento').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!currentUser) {
        alert('Debes iniciar sesión');
        return;
    }
    
    const data = {
        user_id: currentUser.id,
        tipo: document.getElementById('tipo').value,
        monto: document.getElementById('monto').value,
        categoria: document.getElementById('categoria').value,
        descripcion: document.getElementById('descripcion').value,
        fecha: document.getElementById('fecha').value
    };
    
    try {
        const response = await fetch(`${API_URL}/api/movimientos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('formMessage', '✅ ' + result.mensaje);
            document.getElementById('formMovimiento').reset();
            document.getElementById('fecha').valueAsDate = new Date();
            cargarResumen();
            cargarMovimientos();
        } else {
            showMessage('formMessage', result.error, true);
        }
    } catch (error) {
        showMessage('formMessage', 'Error de conexión', true);
    }
});

async function cargarMovimientos() {
    if (!currentUser) return;
    
    const tipo = document.getElementById('filtroTipo').value;
    const estado = document.getElementById('filtroEstado').value;
    
    let url = `${API_URL}/api/movimientos/${currentUser.id}?`;
    if (tipo) url += `tipo=${tipo}&`;
    if (estado) url += `estado=${estado}`;
    
    try {
        const response = await fetch(url);
        const result = await response.json();
        
        const lista = document.getElementById('movimientosList');
        
        if (result.movimientos.length === 0) {
            lista.innerHTML = '<p class="no-data">No hay movimientos registrados</p>';
            return;
        }
        
        lista.innerHTML = result.movimientos.map(m => `
            <div class="movimiento-item ${m.tipo.toLowerCase()} ${m.estado.toLowerCase()}">
                <div class="movimiento-header">
                    <span class="tipo-badge">${m.tipo}</span>
                    <span class="fecha">${m.fecha}</span>
                </div>
                <div class="movimiento-body">
                    <div>
                        <strong>${m.categoria || 'Sin categoría'}</strong>
                        <p>${m.descripcion || ''}</p>
                    </div>
                    <div class="monto ${m.tipo.toLowerCase()}">
                        ${m.tipo === 'INGRESO' ? '+' : '-'}${formatMoney(m.monto)}
                    </div>
                </div>
                <div class="movimiento-actions">
                    <span class="estado-badge ${m.estado.toLowerCase()}">${m.estado}</span>
                    ${m.estado === 'BORRADOR' ? `
                        <button onclick="confirmarMovimiento(${m.id})" class="btn-small">✓ Confirmar</button>
                    ` : ''}
                    <button onclick="eliminarMovimiento(${m.id})" class="btn-small btn-danger">✗ Eliminar</button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error cargando movimientos:', error);
    }
}

async function confirmarMovimiento(id) {
    if (!confirm('¿Confirmar este movimiento?')) return;
    
    try {
        const response = await fetch(`${API_URL}/api/movimientos/${id}/confirmar`, {
            method: 'PUT'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            cargarResumen();
            cargarMovimientos();
        } else {
            alert(result.error);
        }
    } catch (error) {
        alert('Error de conexión');
    }
}

async function eliminarMovimiento(id) {
    if (!confirm('¿Eliminar este movimiento?')) return;
    
    try {
        const response = await fetch(`${API_URL}/api/movimientos/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            cargarResumen();
            cargarMovimientos();
        }
    } catch (error) {
        alert('Error de conexión');
    }
}

async function cargarResumen() {
    if (!currentUser) return;
    
    try {
        const response = await fetch(`${API_URL}/api/resumen/${currentUser.id}`);
        const result = await response.json();
        
        document.getElementById('totalIngresos').textContent = formatMoney(result.ingresos);
        document.getElementById('totalGastos').textContent = formatMoney(result.gastos);
        
        const balanceEl = document.getElementById('balance');
        balanceEl.textContent = formatMoney(result.balance);
        balanceEl.style.color = result.balance >= 0 ? '#22c55e' : '#ef4444';
        
    } catch (error) {
        console.error('Error cargando resumen:', error);
    }
}