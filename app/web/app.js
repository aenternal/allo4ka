const jsonHeaders = { 'Content-Type': 'application/json' };

async function apiFetch(url, options = {}) {
  const response = await fetch(url, options);
  if (response.status === 401) {
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(payload.detail || 'Request failed');
  }
  return response.json();
}

function formToPayload(form) {
  const data = new FormData(form);
  const payload = {};
  for (const [key, value] of data.entries()) {
    payload[key] = value;
  }
  for (const element of form.querySelectorAll('input[type="checkbox"]')) {
    payload[element.name] = element.checked;
  }
  for (const element of form.querySelectorAll('input[type="number"]')) {
    payload[element.name] = Number(element.value);
  }
  return payload;
}

function renderList(elementId, rows, formatter) {
  const target = document.getElementById(elementId);
  target.innerHTML = '';
  rows.forEach((row) => {
    const item = document.createElement('article');
    item.className = 'list-item';
    item.innerHTML = formatter(row);
    target.appendChild(item);
  });
}

async function refreshAll() {
  const [triggers, responses, links, fragments, audioCache] = await Promise.all([
    apiFetch('/triggers'),
    apiFetch('/responses'),
    apiFetch('/trigger-responses'),
    apiFetch('/fragments'),
    apiFetch('/audio-cache'),
  ]);

  renderList('triggers-list', triggers, (row) => `<strong>#${row.id}</strong> [${row.platform}] ${row.pattern} · active=${row.is_active}`);
  renderList('responses-list', responses, (row) => `<strong>#${row.id}</strong> ${row.text}<br><span class="muted">voice_enabled=${row.voice_enabled}</span>`);
  renderList('links-list', links, (row) => `<strong>#${row.id}</strong> trigger=${row.trigger_id} → response=${row.response_id}`);
  renderList('fragments-list', fragments, (row) => `<strong>#${row.id}</strong> ${row.part1}${row.part2}${row.part3}${row.part4}`);
  renderList('audio-cache-list', audioCache, (row) => `<strong>#${row.id}</strong> ${row.text}<br><span class="muted">${row.file_path}</span>`);
}

function bindForm(formId, url, afterMessage) {
  document.getElementById(formId).addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    try {
      await apiFetch(url, {
        method: 'POST',
        headers: jsonHeaders,
        body: JSON.stringify(formToPayload(form)),
      });
      form.reset();
      await refreshAll();
      if (afterMessage) {
        afterMessage.textContent = '';
      }
    } catch (error) {
      if (afterMessage) {
        afterMessage.textContent = error.message;
      }
    }
  });
}

window.addEventListener('DOMContentLoaded', async () => {
  const pregenResult = document.getElementById('pregeneration-result');

  bindForm('trigger-form', '/triggers');
  bindForm('response-form', '/responses');
  bindForm('link-form', '/trigger-responses');
  bindForm('fragment-form', '/fragments');

  document.getElementById('voice-pregeneration-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    try {
      const payload = formToPayload(event.currentTarget);
      const result = await apiFetch('/voice-pregeneration', {
        method: 'POST',
        headers: jsonHeaders,
        body: JSON.stringify(payload),
      });
      pregenResult.textContent = `Задача ${result.task_id} поставлена в очередь. fragment_count=${result.fragment_count}`;
    } catch (error) {
      pregenResult.textContent = error.message;
    }
  });

  document.getElementById('logout-button').addEventListener('click', async () => {
    await apiFetch('/auth/logout', { method: 'POST' });
    window.location.href = '/login';
  });

  await refreshAll();
});
