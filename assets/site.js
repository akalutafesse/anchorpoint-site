/* Anchor Point — shared behaviour: mobile navigation + project inquiry form */
(function () {
  'use strict';

  /* Mobile navigation */
  var burger = document.getElementById('burger');
  var nav = document.getElementById('nav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) {
        nav.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
        burger.focus();
      }
    });
  }

  /* Project inquiry form.
     The success message is shown ONLY after the backend confirms receipt (HTTP 2xx).
     If no endpoint has been configured yet, the form says so honestly and never claims success. */
  var form = document.getElementById('inquiry');
  if (!form) return;
  var msg = document.getElementById('fmsg');
  var btn = document.getElementById('fsub');
  var endpoint = (form.getAttribute('data-endpoint') || '').trim();
  var telegram = (form.getAttribute('data-telegram') || '').trim();

  function show(kind, text) { msg.className = 'fmsg ' + kind; msg.textContent = text; }

  if (!endpoint && !telegram) {
    show('info', 'Online inquiries are being set up. In the meantime, please contact us by telephone using the details on this page.');
  }

  function validate() {
    var ok = true, first = null;
    form.querySelectorAll('[required]').forEach(function (el) {
      var good = el.value.trim() !== '' && (el.type !== 'email' || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value.trim()));
      el.closest('.fg').classList.toggle('bad', !good);
      el.setAttribute('aria-invalid', good ? 'false' : 'true');
      if (!good) { ok = false; first = first || el; }
    });
    if (first) first.focus();
    return ok;
  }

  /* Telegram hand-off: opens the firm's Telegram chat with the inquiry pre-written.
     Plain text only. The visitor still has to press Send, so this never claims the inquiry was received. */
  function sendViaTelegram() {
    var f = form.elements, lines = ['Project inquiry — Anchor Point website', ''];
    [['Name', f.name], ['Organization', f.organization], ['Email', f.email], ['Telephone', f.telephone],
     ['Service required', f.service], ['Project location', f.location]].forEach(function (p) {
      var v = p[1].value.trim();
      if (v) lines.push(p[0] + ': ' + v);
    });
    lines.push('', 'Project description:', f.description.value.trim());
    var url = 'https://t.me/' + encodeURIComponent(telegram) + '?text=' + encodeURIComponent(lines.join('\n').slice(0, 3500));
    window.open(url, '_blank', 'noopener');
    msg.className = 'fmsg info';
    msg.textContent = 'Telegram is opening with your inquiry written out. Press Send in Telegram to deliver it; it is not sent until you do. ';
    var a = document.createElement('a');
    a.href = url; a.target = '_blank'; a.rel = 'noopener'; a.textContent = 'Open Telegram again';
    msg.appendChild(a);
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!validate()) { show('no', 'Please complete the highlighted fields.'); return; }
    if (form.elements.website && form.elements.website.value) return; /* spam honeypot */
    if (!endpoint && telegram) { sendViaTelegram(); return; }
    if (!endpoint) {
      show('info', 'Online inquiries are being set up, so this form has not been sent. Please contact us by telephone using the details on this page.');
      return;
    }
    var label = btn.textContent;
    btn.disabled = true; btn.textContent = 'Submitting…';
    fetch(endpoint, { method: 'POST', headers: { 'Accept': 'application/json' }, body: new FormData(form) })
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        form.reset();
        show('ok', 'Thank you for contacting Anchor Point. Your inquiry has been successfully received. A member of our team will review your request and contact you shortly.');
      })
      .catch(function () {
        show('no', 'We could not submit your inquiry. Please try again, or contact us by telephone using the details on this page.');
      })
      .then(function () { btn.disabled = false; btn.textContent = label; });
  });
})();
