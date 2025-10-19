// ...existing code...
document.addEventListener('DOMContentLoaded', function(){
  const btn = document.getElementById('theme-toggle');
  if(!btn) return;
  const root = document.documentElement;
  const saved = localStorage.getItem('mf-theme');
  if(saved === 'dark') document.body.classList.add('dark');
  btn.addEventListener('click', function(){
    document.body.classList.toggle('dark');
    localStorage.setItem('mf-theme', document.body.classList.contains('dark') ? 'dark' : 'light');
  });
});

// Expand / collapse events details
document.addEventListener('click', function(e){
  const card = e.target.closest('.event-card');
  if(!card) return;
  // if click on button or header -> toggle
  if(e.target.closest('.btn-toggle') || e.target.closest('.event-summary')){
    const expanded = card.classList.toggle('expanded');
    card.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    const details = card.querySelector('.event-details');
    if(details) details.setAttribute('aria-hidden', expanded ? 'false' : 'true');
    // update button text
    const btn = card.querySelector('.btn-toggle');
    if(btn) btn.textContent = expanded ? 'إخفاء' : 'عرض';
  }
});

// General expand/collapse for cards (Events / Notes / Plans)
document.addEventListener('click', function(e){
  const card = e.target.closest('.collapsible-card');
  if(!card) return;
  // toggle on summary click or button
  if(e.target.closest('.btn-toggle') || e.target.closest('.card-summary')){
    const expanded = card.classList.toggle('expanded');
    card.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    const details = card.querySelector('.card-details');
    if(details) details.setAttribute('aria-hidden', expanded ? 'false' : 'true');
    const btn = card.querySelector('.btn-toggle');
    if(btn) btn.textContent = expanded ? 'إخفاء' : 'عرض';
  }
});

// keyboard: Enter/Space on focused summary
document.addEventListener('keydown', function(e){
  if(e.key === 'Enter' || e.key === ' '){
    const el = document.activeElement;
    if(el && el.classList && el.classList.contains('card-summary')){
      e.preventDefault();
      const card = el.closest('.collapsible-card');
      if(card){
        const expanded = card.classList.toggle('expanded');
        card.setAttribute('aria-expanded', expanded ? 'true' : 'false');
        const details = card.querySelector('.card-details');
        if(details) details.setAttribute('aria-hidden', expanded ? 'false' : 'true');
        const btn = card.querySelector('.btn-toggle');
        if(btn) btn.textContent = expanded ? 'إخفاء' : 'عرض';
      }
    }
  }
});

// Dashboard date picker + today/tomorrow buttons (AJAX)
document.addEventListener('DOMContentLoaded', function(){
  const dateInput = document.getElementById('dashboard-date');
  const btnToday = document.getElementById('btn-today');
  const btnTomorrow = document.getElementById('btn-tomorrow');
  const btnFilter = document.getElementById('dashboard-filter');
  const content = document.getElementById('dashboard-content');

  async function loadFor(d){
    console.log('loadFor called', d);
    try{
      const res = await fetch(`/dashboard/data?d=${encodeURIComponent(d)}`);
      console.log('fetch status', res.status);
      if(res.ok){
        const html = await res.text();
        content.innerHTML = html;
        history.replaceState(null, '', `/?d=${encodeURIComponent(d)}`);
      }
    }catch(err){
      console.error(err);
    }
  }

  // expose globally so toggle handler can refresh dashboard
  window.loadDashboardFor = loadFor;

  // عند تغيير التاريخ لا يتم التحميل تلقائياً — ينتظر الضغط على "تصفية"
  if(dateInput){
    dateInput.addEventListener('change', function(){
      // فقط يحدث القيمة؛ يمكن إضافة فحص/تأكيد هنا
    });
    // دعم Enter كمفتاح تصفية سريع
    dateInput.addEventListener('keydown', function(e){
      if(e.key === 'Enter'){
        e.preventDefault();
        const d = this.value || new Date().toISOString().slice(0,10);
        loadFor(d);
      }
    });
  }

  // الأزرار تضبط التاريخ فقط الآن
  btnToday?.addEventListener('click', function(){
    const d = new Date().toISOString().slice(0,10);
    if(dateInput) dateInput.value = d;
  });
  btnTomorrow?.addEventListener('click', function(){
    const t = new Date(Date.now() + 86400000).toISOString().slice(0,10);
    if(dateInput) dateInput.value = t;
  });

  // الزر الجديد يفعل التحميل/التصفية
  btnFilter?.addEventListener('click', function(){
    const d = (dateInput && dateInput.value) ? dateInput.value : new Date().toISOString().slice(0,10);
    loadFor(d);
  });
});

// Global click handler: toggle task from dashboard/tasks (delegation)
// توحيد التعامل مع عناصر .task-toggle المستخدمة في الصفحتين
document.addEventListener('click', async function(e){
  const btn = e.target.closest('.task-toggle');
  if(!btn) return;
  e.preventDefault();
  const id = btn.getAttribute('data-id');
  if(!id) return;

  const prevPressed = btn.getAttribute('aria-pressed') === 'true';

  // optimistic UI: عكس الحالة فورًا بصريًا
  btn.setAttribute('aria-pressed', (!prevPressed).toString());
  btn.disabled = true;

  try {
    const res = await fetch(`/tasks/toggle_ajax/${id}`, { method: 'POST' });
    if(!res.ok) throw new Error('Network error: ' + res.status);
    const json = await res.json();
    if(!json.ok) throw new Error(json.error || 'Toggle failed');

    // اضبط aria-pressed حسب الحالة الفعلية المطلوبة من السيرفر
    btn.setAttribute('aria-pressed', json.status === 'Done' ? 'true' : 'false');

    // إعادة تحميل جزئي للوحة لإظهار التغيير في القوائم والأعداد
    const dateInput = document.getElementById('dashboard-date');
    const d = (dateInput && dateInput.value) ? dateInput.value : new Date().toISOString().slice(0,10);
    if(window.loadDashboardFor) window.loadDashboardFor(d);
    else location.reload();
  } catch (err) {
    console.error(err);
    // revert optimistic UI on error
    btn.setAttribute('aria-pressed', prevPressed.toString());
    alert('حدث خطأ أثناء تغيير حالة المهمة.');
  } finally {
    btn.disabled = false;
  }
});

// Mark select/date as active when server-side sets a selected option/value
document.addEventListener('DOMContentLoaded', function(){
  try {
    const period = document.getElementById('tasks-period');
    const tasksDate = document.getElementById('tasks-date');
    if(period){
      // if any option has selected attribute (server rendered) mark active
      if(period.querySelector('option[selected]')) period.classList.add('active');
    }
    if(tasksDate && tasksDate.value) tasksDate.classList.add('active');
  } catch(e){ /* ignore */ }
});