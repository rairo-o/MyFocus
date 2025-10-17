from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
from datetime import date, datetime, timedelta
import io, csv
from models import db_init, tasks as task_model, events as event_model, notes as note_model, plans as plan_model
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "local-dev-secret"
db_init('database.db')


# @app.route('/')
# def dashboard():
#     today = date.today().isoformat()
#     week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()
#     week_end = (date.fromisoformat(week_start) + timedelta(days=6)).isoformat()

#     # جمع مهام اليوم وفرزها إلى مطلوب إكماله ومكتمل
#     todays_all = task_model.list(range_filter=(today, today))
#     todays_pending = [t for t in todays_all if t.get('status') != 'Done']
#     todays_done = [t for t in todays_all if t.get('status') == 'Done']

#     todays_events = event_model.list(filter_by={'date_only': today})

#     week_tasks = task_model.list(range_filter=(week_start, week_end))
#     total = len(week_tasks)
#     done = sum(1 for t in week_tasks if t['status'] == 'Done')
#     percent_done = int(done * 100 / total) if total else 0

#     return render_template('dashboard.html',
#                            todays_all=todays_all,
#                            todays_pending=todays_pending,
#                            todays_done=todays_done,
#                            todays_events=todays_events,
#                            percent_done=percent_done,
#                            total=total, done=done)
# # ...existing code...

# ...existing code...
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
# ...existing code...

@app.route('/')
def dashboard():
    sel = request.args.get('d')
    try:
        sel_date = date.fromisoformat(sel) if sel else date.today()
    except Exception:
        sel_date = date.today()
    sd = sel_date.isoformat()
    # label for header
    if sel_date == date.today():
        selected_label = 'مهام اليوم'
    elif sel_date == date.today() + timedelta(days=1):
        selected_label = 'مهام غدًا'
    else:
        selected_label = f"مهام {sel_date.strftime('%d/%m/%Y')}"

    week_start = (sel_date - timedelta(days=sel_date.weekday())).isoformat()
    week_end = (date.fromisoformat(week_start) + timedelta(days=6)).isoformat()

    todays_all = task_model.list(range_filter=(sd, sd))
    todays_pending = [t for t in todays_all if t.get('status') != 'Done']
    todays_done = [t for t in todays_all if t.get('status') == 'Done']
    todays_events = event_model.list(filter_by={'date_only': sd})

    week_tasks = task_model.list(range_filter=(week_start, week_end))
    total = len(week_tasks)
    done = sum(1 for t in week_tasks if t['status'] == 'Done')
    percent_done = int(done * 100 / total) if total else 0

    return render_template('dashboard.html',
                           selected_date=sd,
                           selected_label=selected_label,
                           todays_all=todays_all,
                           todays_pending=todays_pending,
                           todays_done=todays_done,
                           todays_events=todays_events,
                           percent_done=percent_done,
                           total=total, done=done)

@app.route('/dashboard/data')
def dashboard_data():
    sel = request.args.get('d')
    try:
        sel_date = date.fromisoformat(sel) if sel else date.today()
    except Exception:
        sel_date = date.today()
    sd = sel_date.isoformat()
    if sel_date == date.today():
        selected_label = 'مهام اليوم'
    elif sel_date == date.today() + timedelta(days=1):
        selected_label = 'مهام غدًا'
    else:
        selected_label = f"مهام {sel_date.strftime('%d/%m/%Y')}"

    todays_all = task_model.list(range_filter=(sd, sd))
    todays_pending = [t for t in todays_all if t.get('status') != 'Done']
    todays_done = [t for t in todays_all if t.get('status') == 'Done']
    todays_events = event_model.list(filter_by={'date_only': sd})
    return render_template('_dashboard_tasks.html',
                           selected_label=selected_label,
                           todays_all=todays_all,
                           todays_pending=todays_pending,
                           todays_done=todays_done,
                           todays_events=todays_events)
# ...existing code...

# Tasks
@app.route('/tasks')
def tasks_page():
    q = request.args.get('q', '').strip()
    period = request.args.get('period', 'all')
    today = date.today()
    range_filter = None
    if period == 'day':
        range_filter = (today.isoformat(), today.isoformat())
    elif period == 'tomorrow':
        td = (today + timedelta(days=1)).isoformat()
        range_filter = (td, td)
    elif period == 'week':
        ws = today - timedelta(days=today.weekday())
        range_filter = (ws.isoformat(), (ws + timedelta(days=6)).isoformat())
    elif period == 'month':
        ms = today.replace(day=1)
        next_month = (ms.replace(day=28) + timedelta(days=4)).replace(day=1)
        range_filter = (ms.isoformat(), (next_month - timedelta(days=1)).isoformat())
    elif period == 'date':
        sel = request.args.get('date')
        try:
            d = date.fromisoformat(sel)
            range_filter = (d.isoformat(), d.isoformat())
        except Exception:
            range_filter = None

    items = task_model.list(search=q or None, range_filter=range_filter)
    return render_template('tasks.html', tasks=items, q=q, period=period)

@app.route('/tasks/add', methods=['POST'])
def add_task():
    title = request.form.get('title', '').strip()
    date_str = request.form.get('date', '').strip()
    if not title or not date_str:
        flash('العنوان والتاريخ مطلوبان', 'error')
        return redirect(url_for('tasks_page'))
    task_model.create(title=title,
                      description=request.form.get('description', '').strip() or None,
                      category=request.form.get('category', '').strip() or None,
                      date=date_str,
                      status=request.form.get('status') or 'Pending')
    return redirect(url_for('tasks_page'))

@app.route('/tasks/edit/<int:item_id>', methods=['GET','POST'])
def edit_task(item_id):
    item = task_model.get(item_id)
    if request.method == 'POST':
        task_model.update(item_id,
                          title=request.form.get('title', '').strip(),
                          description=request.form.get('description', '').strip() or None,
                          category=request.form.get('category', '').strip() or None,
                          date=request.form.get('date', '').strip(),
                          status=request.form.get('status') or 'Pending')
        return redirect(url_for('tasks_page'))
    return render_template('task_edit.html', task=item)

@app.route('/tasks/delete/<int:item_id>', methods=['POST'])
def delete_task(item_id):
    task_model.delete(item_id)
    return redirect(url_for('tasks_page'))

@app.route('/tasks/toggle/<int:item_id>', methods=['POST'])
def toggle_task(item_id):
    task_model.toggle_status(item_id)
    return redirect(url_for('tasks_page'))

@app.route('/tasks/export/csv')
def tasks_export_csv():
    items = task_model.list()
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['id','title','description','category','date','status'])
    for t in items:
        writer.writerow([t['id'], t['title'], t.get('description') or '', t.get('category') or '', t.get('date') or '', t.get('status')])
    mem = io.BytesIO()
    mem.write(si.getvalue().encode('utf-8'))
    mem.seek(0)
    return send_file(mem, as_attachment=True, download_name='tasks.csv', mimetype='text/csv')

@app.route('/tasks/export/pdf')
def tasks_export_pdf():
    items = task_model.list()
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    y = h - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "MyFocus - Tasks Export")
    y -= 24
    c.setFont("Helvetica", 10)
    for t in items:
        line = f"{t['date'] or 'N/A'} — [{t['status']}] {t['title']}"
        c.drawString(40, y, line)
        y -= 14
        if t.get('description'):
            # wrap simple
            desc = t['description']
            while desc:
                part = desc[:80]
                c.drawString(50, y, part)
                desc = desc[80:]
                y -= 12
                if y < 60:
                    c.showPage()
                    y = h - 40
        y -= 6
        if y < 60:
            c.showPage()
            y = h - 40
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='tasks.pdf', mimetype='application/pdf')

# Events
@app.route('/events')
def events_page():
    items = event_model.list()
    return render_template('events.html', events=items)

@app.route('/events/add', methods=['POST'])
def add_event():
    title = request.form.get('title', '').strip()
    dt = request.form.get('datetime', '').strip()
    if not title or not dt:
        flash('العنوان والوقت مطلوبان', 'error')
        return redirect(url_for('events_page'))
    event_model.create(title=title,
                       description=request.form.get('description', '').strip() or None,
                       dt=dt,
                       location=request.form.get('location', '').strip() or None)
    return redirect(url_for('events_page'))

@app.route('/events/delete/<int:item_id>', methods=['POST'])
def delete_event(item_id):
    event_model.delete(item_id)
    return redirect(url_for('events_page'))

# Notes
@app.route('/notes')
def notes_page():
    items = note_model.list()
    return render_template('notes.html', notes=items)

@app.route('/notes/add', methods=['POST'])
def add_note():
    content = request.form.get('content', '').strip()
    if not content:
        flash('الملاحظة فارغة', 'error')
        return redirect(url_for('notes_page'))
    note_model.create(content=content)
    return redirect(url_for('notes_page'))

# Plans
@app.route('/plans')
def plans_page():
    items = plan_model.list()
    return render_template('plans.html', plans=items)

@app.route('/plans/add', methods=['POST'])
def add_plan():
    title = request.form.get('title', '').strip()
    if not title:
        flash('العنوان مطلوب', 'error')
        return redirect(url_for('plans_page'))
    plan_model.create(title=title,
                      description=request.form.get('description', '').strip() or None,
                      target_date=request.form.get('target_date', '').strip() or None)
    return redirect(url_for('plans_page'))

# ...existing code...
# Notes - تعديل وحذف
@app.route('/notes/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_note(item_id):
    item = note_model.get(item_id)
    if not item:
        flash('الملاحظة غير موجودة', 'error')
        return redirect(url_for('notes_page'))
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if not content:
            flash('المحتوى فارغ', 'error')
            return redirect(url_for('edit_note', item_id=item_id))
        note_model.update(item_id, content)
        return redirect(url_for('notes_page'))
    return render_template('note_edit.html', note=item)

@app.route('/notes/delete/<int:item_id>', methods=['POST'])
def delete_note(item_id):
    note_model.delete(item_id)
    return redirect(url_for('notes_page'))

# Plans - تعديل وحذف
@app.route('/plans/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_plan(item_id):
    item = plan_model.get(item_id)
    if not item:
        flash('الخطة غير موجودة', 'error')
        return redirect(url_for('plans_page'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('العنوان مطلوب', 'error')
            return redirect(url_for('edit_plan', item_id=item_id))
        plan_model.update(item_id,
                          title,
                          request.form.get('description', '').strip() or None,
                          request.form.get('target_date', '').strip() or None)
        return redirect(url_for('plans_page'))
    return render_template('plan_edit.html', plan=item)

@app.route('/plans/delete/<int:item_id>', methods=['POST'])
def delete_plan(item_id):
    plan_model.delete(item_id)
    return redirect(url_for('plans_page'))
# ...existing code...

if __name__ == '__main__':
    app.run(debug=True)