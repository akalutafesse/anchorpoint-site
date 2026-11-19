/* Anchor Point — shared behaviour: mobile navigation + project inquiry form */
(function () {
  'use strict';

  /* Mobile navigation */
  var burger = document.getElementById('burger');
  var nav = document.getElementById('nav');
  if (burger && nav) {
    var close = function () { nav.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); };
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) close(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) { close(); burger.focus(); }
    });
  }

  /* Project inquiry form.
     With an endpoint: posts to the form-to-Telegram service; success is shown ONLY after it confirms (HTTP 2xx).
     With a Telegram username instead: opens Telegram with the inquiry written out for the visitor to send.
     With neither: says honestly that the form is not sent. */
  var form = document.getElementById('inquiry');
  if (!form) return;
  var msg = document.getElementById('fmsg');
  var btn = document.getElementById('fsub');
  var endpoint = (form.getAttribute('data-endpoint') || '').trim();
  var telegram = (form.getAttribute('data-telegram') || '').trim();
  var PHONE = 'Please call us on +251 911 25 75 92 or +251 969 15 15 55.';

  function show(kind, text) { msg.className = 'fmsg ' + kind; msg.textContent = text; }

  function validate() {
    var ok = true, first = null;
    form.querySelectorAll('[required]').forEach(function (el) {
      var good = el.value.trim().length > 1;
      el.closest('.fg').classList.toggle('bad', !good);
      el.setAttribute('aria-invalid', good ? 'false' : 'true');
      if (!good) { ok = false; first = first || el; }
    });
    if (first) first.focus();
    return ok;
  }

  function sendViaTelegram() {
    var f = form.elements, lines = ['Project inquiry — Anchor Point website', ''];
    [['Name', f.name], ['Contact', f.contact], ['Organization', f.organization]].forEach(function (p) {
      var v = p[1].value.trim();
      if (v) lines.push(p[0] + ': ' + v);
    });
    lines.push('', f.message.value.trim());
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
    if (!endpoint) { show('info', 'Online inquiries are being set up, so this message has not been sent. ' + PHONE); return; }
    var label = btn.querySelector('span');
    var text = label.textContent;
    btn.disabled = true; label.textContent = 'Sending…';
    fetch(endpoint, { method: 'POST', headers: { 'Accept': 'application/json' }, body: new FormData(form) })
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        form.reset();
        show('ok', 'Thank you. Your inquiry has been received. A member of our team will review it and contact you shortly.');
      })
      .catch(function () { show('no', 'We could not send your inquiry. Please try again. ' + PHONE); })
      .then(function () { btn.disabled = false; label.textContent = text; });
  });
})();
