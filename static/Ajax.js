/**
 * ajax.js — manejo sin recarga para MiMundo
 */

// ── Utilidades ───────────────────────────────────────────────────────────────
async function postForm(url, formData) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
    body: formData,
  });
  return res.json();
}

async function deleteItem(table, id) {
  const res = await fetch(`/delete/${table}/${id}`, {
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
  });
  return res.json();
}

// ── Delegación Global de Eventos (No necesita reiniciarse al cambiar de página) ──
document.addEventListener('click', async (e) => {
  // 1. Toggle Actividades (Agenda/Kanban)
  if (e.target.closest('.btn-toggle-activity')) {
    const btn = e.target.closest('.btn-toggle-activity');
    const id = btn.dataset.id;
    const current = btn.dataset.status;
    const next = current === 'pendiente' ? 'completada' : 'pendiente';

    const fd = new FormData();
    fd.append('id', id);
    fd.append('status', next);
    const data = await fetch('/update_activity', { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' }, body: fd }).then(r => r.json());

    if (data.success) {
      btn.dataset.status = next;
      btn.textContent = next === 'pendiente' ? '✓' : '↩';
      const item = document.querySelector(`li[data-id="${id}"]`);
      if (item) item.className = `activity-item status-${next}`;
      updatePendingCount(next === 'completada' ? -1 : 1);
    }
  }

  // 2. Eliminar Actividad
  if (e.target.closest('.btn-delete-activity')) {
    const btn = e.target.closest('.btn-delete-activity');
    const id = btn.dataset.id;
    const item = document.querySelector(`li[data-id="${id}"]`);
    const wasPending = item?.classList.contains('status-pendiente');
    const data = await deleteItem('activities', id);
    if (data.success) {
      item?.remove();
      if (wasPending) updatePendingCount(-1);
    }
  }

  // 3. Eliminar Finanza
  if (e.target.closest('.btn-delete-finance')) {
    const btn = e.target.closest('.btn-delete-finance');
    const id = btn.dataset.id;
    const row = document.querySelector(`tr[data-id="${id}"]`);
    const data = await deleteItem('finances', id);
    if (data.success) {
      row?.remove();
      updateBalance(data.balance);
    }
  }
});

// ── Manejo de Formularios (Submit) ──
document.addEventListener('submit', async (e) => {
  // Agenda
  if (e.target.id === 'agenda-form') {
    e.preventDefault();
    const data = await postForm('/agenda', new FormData(e.target));
    if (data.success) {
      const a = data.activity;
      const list = document.getElementById('activities-list');
      if (list) {
        list.insertAdjacentHTML('afterbegin', `<li data-id="${a.id}" class="activity-item status-${a.status}">...</li>`);
      }
      e.target.reset();
      updatePendingCount(1);
    }
  }

  // Presupuesto
  if (e.target.id === 'presupuesto-form') {
    e.preventDefault();
    const data = await postForm('/presupuesto', new FormData(e.target));
    if (data.success) {
      const f = data.finance;
      const tbody = document.getElementById('finances-tbody');
      if (tbody) {
        tbody.insertAdjacentHTML('afterbegin', `<tr data-id="${f.id}"><td>${f.description}</td>...</tr>`);
      }
      e.target.reset();
      updateBalance(data.balance);
    }
  }
});

// ── Helpers UI ──
function updateBalance(newBalance) {
  const el = document.getElementById('balance-display');
  if (el) {
    el.textContent = `$${parseFloat(newBalance).toFixed(2)}`;
    el.className = newBalance >= 0 ? 'amount-pos' : 'amount-neg';
  }
}

function updatePendingCount(delta) {
  const el = document.getElementById('pending-count');
  if (el) {
    el.textContent = Math.max(0, (parseInt(el.textContent) || 0) + delta);
  }
}
