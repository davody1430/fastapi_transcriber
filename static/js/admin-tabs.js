/* ---------- admin-tabs.js (AJAX Tab Loader) ----------
 * بارگذاری پویا‌ی تب‌ها + مقداردهی DataTables
 * نسخه: 1404/05/ — همگام با DataTables 2.0.8
 * ---------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
    const btns   = document.querySelectorAll('.tab-btn');
    const box    = document.getElementById('tab-container');
    const loader = document.getElementById('loader');
    const DT_LANG_URL = 'https://cdn.datatables.net/plug-ins/2.0.8/i18n/fa.json';

    /** جدول‌های تازه را یک‌بار DataTables کن */
    const initTables = (scope) => {
        scope.querySelectorAll('table[data-datatables]').forEach(tbl => {
            if (!tbl.dataset.dtInit) {
                $(tbl).DataTable({
                    paging: false,
                    searching: false,
                    info: false,
                    language: { url: DT_LANG_URL }
                });
                tbl.dataset.dtInit = '1';
            }
        });
    };

    /** محتوا را از سرور بگیر و در جعبه بگذار */
    const loadTab = async (btn) => {
        loader.style.display = 'block';
        box.innerHTML = '';
        btns.forEach(b => b.classList.toggle('active', b === btn));

        try {
            const res = await fetch(btn.dataset.url, { headers: { 'X-Requested-With': 'fetch' } });
            if (!res.ok) throw new Error(res.statusText);
            const html = await res.text();
            loader.style.display = 'none';
            box.innerHTML = html;
            initTables(box);
        } catch (err) {
            loader.textContent = 'خطا در بارگذاری محتوا';
            console.error(err);
        }
    };

    // هندل کلیک تب‌ها
    btns.forEach(b => b.addEventListener('click', () => loadTab(b)));

    // تب پیش‌فرض
    loadTab(document.querySelector('.tab-btn.active'));
});
