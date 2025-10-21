const form = document.getElementById('waitlist-form');
const email = document.getElementById('email');
const msg = document.getElementById('form-msg');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  msg.textContent = 'Enviando...';
  try {
    const r = await fetch('/join', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ email: email.value.trim() })
    });
    const data = await r.json();
    if (r.ok && data.ok) {
      msg.textContent = 'Apuntado. Te escribiremos en breve.';
      form.reset();
    } else {
      msg.textContent = data?.error || 'No se pudo guardar el email.';
    }
  } catch (_) {
    msg.textContent = 'Conexión fallida. Intenta de nuevo.';
  }
});
