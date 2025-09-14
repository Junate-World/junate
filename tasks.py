from flask import Blueprint, request, jsonify, render_template, Response, url_for, abort
from flask_login import login_required, current_user
from models import db, Task, User

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/user')
@login_required
def user_page():
    total_tasks = Task.query.filter_by(user_id=current_user.id).count()
    active_count = Task.query.filter_by(user_id=current_user.id, status='Active').count()
    onhold_count = Task.query.filter_by(user_id=current_user.id, status='On hold').count()
    closed_count = Task.query.filter_by(user_id=current_user.id, status='Closed').count()
    return render_template('user.html', total_tasks=total_tasks, active_count=active_count, onhold_count=onhold_count, closed_count=closed_count)

@tasks_bp.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    total_tasks = len(tasks)
    active_count = sum(1 for t in tasks if t.status == 'Active')
    onhold_count = sum(1 for t in tasks if t.status == 'On hold')
    closed_count = sum(1 for t in tasks if t.status == 'Closed')
    return render_template('dashboard.html', tasks=tasks, total_tasks=total_tasks, active_count=active_count, onhold_count=onhold_count, closed_count=closed_count)

@tasks_bp.route('/add', methods=['POST'])
@login_required
def add_task():
    data = request.json if request.is_json else None
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    task = data.get('task')
    owner = data.get('owner')
    contact = data.get('contact')
    if not task or not owner or not contact:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    new_task = Task()
    new_task.task = task
    new_task.owner = owner
    new_task.contact = contact
    new_task.summary = data.get('summary', '')
    new_task.phone = data.get('phone', '')
    new_task.site_name = data.get('site_name', '')
    new_task.status = data.get('status', 'Active')
    # Costs: ensure integers; default 0
    try:
        new_task.project_cost = int(data.get('project_cost', 0))
    except (TypeError, ValueError):
        new_task.project_cost = 0
    try:
        new_task.execution_cost = int(data.get('execution_cost', 0))
    except (TypeError, ValueError):
        new_task.execution_cost = 0
    new_task.user_id = current_user.id
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'id': new_task.id, 'task': new_task.task, 'owner': new_task.owner, 'contact': new_task.contact, 'summary': new_task.summary, 'phone': new_task.phone, 'site_name': new_task.site_name, 'created_at': new_task.created_at.isoformat(), 'status': new_task.status, 'project_cost': new_task.project_cost, 'execution_cost': new_task.execution_cost})

@tasks_bp.route('/update', methods=['POST'])
@login_required
def update_task():
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    task = Task.query.filter_by(id=data['id'], user_id=current_user.id).first()
    if task:
        task.task = data['task']
        task.owner = data['owner']
        task.contact = data['contact']
        task.summary = data.get('summary', '')
        task.phone = data.get('phone', '')
        task.site_name = data.get('site_name', '')
        task.status = data.get('status', task.status)
        # Costs: parsed as integers and clamped to >= 0
        def parse_int(value, default=0):
            try:
                i = int(value)
                return i if i >= 0 else 0
            except (TypeError, ValueError):
                return default
        if 'project_cost' in data:
            task.project_cost = parse_int(data.get('project_cost'), task.project_cost or 0)
        if 'execution_cost' in data:
            task.execution_cost = parse_int(data.get('execution_cost'), task.execution_cost or 0)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 404

@tasks_bp.route('/delete/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'status': 'deleted'})
    return jsonify({'status': 'error'}), 404

@tasks_bp.route('/task/<int:task_id>')
@login_required
def view_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    return render_template('task_view.html', task=task)

@tasks_bp.route('/search')
@login_required
def search_tasks():
    q = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'task')
    if not q:
        return jsonify([])
    if search_type == 'owner':
        tasks = Task.query.filter(Task.owner.ilike(f'%{q}%'), Task.user_id == current_user.id).all()
    elif search_type == 'site_name':
        tasks = Task.query.filter(Task.site_name.ilike(f'%{q}%'), Task.user_id == current_user.id).all()
    else:
        tasks = Task.query.filter(Task.task.ilike(f'%{q}%'), Task.user_id == current_user.id).all()
    return jsonify([
        {
            'id': t.id,
            'task': t.task,
            'owner': t.owner,
            'contact': t.contact,
            'summary': t.summary,
            'phone': t.phone,
            'site_name': t.site_name,
            'created_at': t.created_at.isoformat() if t.created_at else '',
            'status': t.status,
            'project_cost': getattr(t, 'project_cost', 0),
            'execution_cost': getattr(t, 'execution_cost', 0)
        } for t in tasks
    ])

@tasks_bp.route('/progress')
@login_required
def progress_report():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    # Fields needed for the report: Site Name, Task, Owner, Status, Summary, Project Cost, Execution Cost, % Profit
    report_rows = [
        {
            'site_name': t.site_name or '',
            'task': t.task or '',
            'owner': t.owner or '',
            'status': t.status or '',
            'summary': t.summary or '',
            'project_cost': getattr(t, 'project_cost', 0) or 0,
            'execution_cost': getattr(t, 'execution_cost', 0) or 0,
            'profit_percent': (
                (round(((getattr(t, 'project_cost', 0) or 0) - (getattr(t, 'execution_cost', 0) or 0)) * 100.0 / (getattr(t, 'project_cost', 0) or 1), 2))
                if (getattr(t, 'project_cost', 0) or 0) > 0 else 0.0
            )
        }
        for t in tasks
    ]
    return render_template('progress_report.html', rows=report_rows)

@tasks_bp.route('/progress.csv')
@login_required
def download_progress_csv():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    # Build CSV content in-memory
    def generate_csv():
        yield 'Site Name,Task,Owner,Status,Summary,Project Cost,Execution Cost,% Profit\r\n'
        for t in tasks:
            # Basic CSV escaping for commas, quotes, and newlines
            def esc(value):
                if value is None:
                    value = ''
                value = str(value)
                if '"' in value or ',' in value or '\n' in value or '\r' in value:
                    value = '"' + value.replace('"', '""') + '"'
                return value
            project_cost = getattr(t, 'project_cost', 0) or 0
            execution_cost = getattr(t, 'execution_cost', 0) or 0
            profit_percent = round(((project_cost - execution_cost) * 100.0 / project_cost), 2) if project_cost > 0 else 0.0
            yield f"{esc(t.site_name)},{esc(t.task)},{esc(t.owner)},{esc(t.status)},{esc(t.summary)},{esc(project_cost)},{esc(execution_cost)},{esc(str(profit_percent) + '%')}\r\n"

    headers = {
        'Content-Disposition': 'attachment; filename="progress_report.csv"'
    }
    return Response(generate_csv(), mimetype='text/csv', headers=headers)

# Visitor dashboard (read-only)
@tasks_bp.route('/view/<int:user_id>/dashboard')
def visitor_dashboard(user_id):
    user = User.query.get_or_404(user_id)
    tasks = Task.query.filter_by(user_id=user.id).all()
    total_tasks = len(tasks)
    active_count = sum(1 for t in tasks if t.status == 'Active')
    onhold_count = sum(1 for t in tasks if t.status == 'On hold')
    closed_count = sum(1 for t in tasks if t.status == 'Closed')
    return render_template('dashboard.html', tasks=tasks, total_tasks=total_tasks, active_count=active_count, onhold_count=onhold_count, closed_count=closed_count, visitor_mode=True, user=user)

# Visitor task view (read-only)
@tasks_bp.route('/view/<int:user_id>/task/<int:task_id>')
def visitor_task_view(user_id, task_id):
    user = User.query.get_or_404(user_id)
    task = Task.query.filter_by(id=task_id, user_id=user.id).first_or_404()
    return render_template('task_view.html', task=task, visitor_mode=True, user=user)

# Visitor progress report (read-only)
@tasks_bp.route('/view/<int:user_id>/progress')
def visitor_progress_report(user_id):
    user = User.query.get_or_404(user_id)
    tasks = Task.query.filter_by(user_id=user.id).all()
    report_rows = [
        {
            'site_name': t.site_name or '',
            'task': t.task or '',
            'owner': t.owner or '',
            'status': t.status or '',
            'summary': t.summary or '',
            'project_cost': getattr(t, 'project_cost', 0) or 0,
            'execution_cost': getattr(t, 'execution_cost', 0) or 0,
            'profit_percent': (
                (round(((getattr(t, 'project_cost', 0) or 0) - (getattr(t, 'execution_cost', 0) or 0)) * 100.0 / (getattr(t, 'project_cost', 0) or 1), 2))
                if (getattr(t, 'project_cost', 0) or 0) > 0 else 0.0
            )
        }
        for t in tasks
    ]
    return render_template('progress_report.html', rows=report_rows, visitor_mode=True, user=user)

