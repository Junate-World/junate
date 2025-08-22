from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Task


chatbot_bp = Blueprint('chatbot', __name__)
@chatbot_bp.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    import re
    data = request.json
    user_message = data.get('message', '').strip()
    state = data.get('chatbot_state') or {}
    mode = data.get('chatbot_mode', 'step')
    # Task type options
    task_type_options = [
        'Decommission',
        'Decommission and Retrieval',
        'Infra Works',
        'Relocation'
    ]
    # --- Natural Language Mode ---
    if mode == 'nlp':
        # Try to extract all fields from the message
        def extract(pattern, text):
            m = re.search(pattern, text, re.IGNORECASE)
            return m.group(1).strip() if m else None
        # Try to find each field
        site_name = extract(r'(?:site name|site)\s*[:=]?\s*([\w\s\-]+?)(?:,|$)', user_message) or extract(r'at ([\w\s\-]+?)(?:,|$)', user_message)
        task_type = None
        for opt in task_type_options:
            if re.search(re.escape(opt), user_message, re.IGNORECASE):
                task_type = opt
                break
        owner = extract(r'(?:owner)\s*[:=]?\s*([\w\s\-]+?)(?:,|$)', user_message)
        contact = extract(r'(?:contact|email)\s*[:=]?\s*([\w\.-]+@[\w\.-]+)', user_message)
        phone = extract(r'(?:phone|number)\s*[:=]?\s*([\d\-\+\s]+)', user_message)
        summary = extract(r'(?:summary|comment)\s*[:=]?\s*([\w\s\-\.]+)', user_message)
        # Optional numeric costs
        def extract_int(pattern, text):
            m = re.search(pattern, text, re.IGNORECASE)
            if not m:
                return None
            try:
                val = int(m.group(1))
                return val if val >= 0 else 0
            except Exception:
                return None
        project_cost = extract_int(r'(?:project\s*cost|project_cost|projectcost)\s*[:=]?\s*(\d+)', user_message)
        execution_cost = extract_int(r'(?:execution\s*cost|execution_cost|executioncost)\s*[:=]?\s*(\d+)', user_message)
        # Prompt for missing fields
        if not site_name:
            return jsonify({'reply': 'What is the Site Name?', 'next_state': {'mode': 'nlp'}})
        if not task_type:
            return jsonify({'reply': 'What is the Task Type?\nOptions: ' + ', '.join(task_type_options), 'next_state': {'mode': 'nlp', 'site_name': site_name}})
        if not owner:
            return jsonify({'reply': 'Who is the Owner?', 'next_state': {'mode': 'nlp', 'site_name': site_name, 'task': task_type}})
        if not contact:
            return jsonify({'reply': 'What is the Contact Email?', 'next_state': {'mode': 'nlp', 'site_name': site_name, 'task': task_type, 'owner': owner}})
        if not phone:
            return jsonify({'reply': 'What is the Phone Number?', 'next_state': {'mode': 'nlp', 'site_name': site_name, 'task': task_type, 'owner': owner, 'contact': contact}})
        # summary is optional
        if not summary:
            summary = ''
        # default costs to 0 if not provided
        if project_cost is None:
            project_cost = 0
        if execution_cost is None:
            execution_cost = 0
        # All info collected, create the task
        new_task = Task(
            site_name=site_name,
            task=task_type,
            owner=owner,
            contact=contact,
            phone=phone,
            summary=summary,
            project_cost=project_cost,
            execution_cost=execution_cost,
            user_id=current_user.id
        )
        db.session.add(new_task)
        db.session.commit()
        reply = f"Task '{new_task.task}' for site '{new_task.site_name}' created!"
        return jsonify({'reply': reply, 'next_state': None})
    # --- Step-by-Step Mode ---
    # Multi-step task creation in correct order
    if state.get('step') == 'awaiting_site_name':
        state['data']['site_name'] = user_message
        reply = 'What is the Task Type?\nOptions: ' + ', '.join(task_type_options)
        state['step'] = 'awaiting_task_type'
        return jsonify({'reply': reply, 'next_state': state})
    elif state.get('step') == 'awaiting_task_type':
        if user_message not in task_type_options:
            reply = 'Invalid Task Type. Please choose one of the following:\n' + ', '.join(task_type_options)
            return jsonify({'reply': reply, 'next_state': state})
        state['data']['task'] = user_message
        reply = 'Who is the Owner?'
        state['step'] = 'awaiting_owner'
        return jsonify({'reply': reply, 'next_state': state})
    elif state.get('step') == 'awaiting_owner':
        state['data']['owner'] = user_message
        reply = 'What is the Contact Email?'
        state['step'] = 'awaiting_contact'
        return jsonify({'reply': reply, 'next_state': state})
    elif state.get('step') == 'awaiting_contact':
        state['data']['contact'] = user_message
        reply = 'What is the Phone Number?'
        state['step'] = 'awaiting_phone'
        return jsonify({'reply': reply, 'next_state': state})
    elif state.get('step') == 'awaiting_phone':
        state['data']['phone'] = user_message
        reply = 'Please provide a Task Summary (or type "skip"):'
        state['step'] = 'awaiting_summary'
        return jsonify({'reply': reply, 'next_state': state})
    elif state.get('step') == 'awaiting_summary':
        summary = user_message if user_message.lower() != 'skip' else ''
        state['data']['summary'] = summary
        # Ask for Project Cost (integer, default 0)
        state['step'] = 'awaiting_project_cost'
        return jsonify({'reply': 'What is the Project Cost? (integer, type "skip" for 0)', 'next_state': state})
    elif state.get('step') == 'awaiting_project_cost':
        txt = user_message.strip().lower()
        if txt == 'skip' or txt == '':
            state['data']['project_cost'] = 0
        else:
            try:
                val = int(user_message.strip())
                state['data']['project_cost'] = val if val >= 0 else 0
            except Exception:
                state['data']['project_cost'] = 0
        state['step'] = 'awaiting_execution_cost'
        return jsonify({'reply': 'What is the Execution Cost? (integer, type "skip" for 0)', 'next_state': state})
    elif state.get('step') == 'awaiting_execution_cost':
        txt = user_message.strip().lower()
        if txt == 'skip' or txt == '':
            state['data']['execution_cost'] = 0
        else:
            try:
                val = int(user_message.strip())
                state['data']['execution_cost'] = val if val >= 0 else 0
            except Exception:
                state['data']['execution_cost'] = 0
        # All info collected, create the task
        new_task = Task(
            site_name=state['data']['site_name'],
            task=state['data']['task'],
            owner=state['data']['owner'],
            contact=state['data']['contact'],
            phone=state['data']['phone'],
            summary=state['data']['summary'],
            project_cost=state['data'].get('project_cost', 0),
            execution_cost=state['data'].get('execution_cost', 0),
            user_id=current_user.id
        )
        db.session.add(new_task)
        db.session.commit()
        reply = f"Task '{new_task.task}' for site '{new_task.site_name}' created!"
        return jsonify({'reply': reply, 'next_state': None})
    # --- Instructional Responses ---
    help_intents = [
        (['how do i create a task', 'how to create a task', 'create task manually', 'add task manually'],
         "To create a new task: Click on the 'Add Task' button or navigate to the task creation section. Enter the task details such as title, description, and due date, then click 'Save' or 'Create'. Your new task will appear in the task list."),
        (['how do i delete a task', 'how to delete a task', 'remove a task', 'delete task'],
         "To delete a task: Find the task you want to remove in your task list. Click the 'Delete' button (usually a trash can icon) next to the task. Confirm the deletion if prompted. The task will be permanently removed."),
        (['how do i edit a task', 'how to edit a task', 'edit task', 'modify a task'],
         "To edit a task: Locate the task you wish to modify. Click the 'Edit' button (often a pencil icon) next to the task. Update the task details as needed, then click 'Save' to apply your changes."),
        (['how do i view a task', 'how to view a task', 'view task', 'see task details'],
         "To view a task: Browse your task list and click on the task you want to view. This will display the full details of the task, including its description, due date, and status."),
        (['how do i save a task', 'how to save a task', 'save task'],
         "To save a task: After entering or editing task details, click the 'Save' button. This will store your changes and update the task list accordingly.")
    ]
    name_intents = ['what is your name', "what's your name", 'who are you', 'your name']
    
    # Check for instructional intents
    lower_msg = user_message.lower()
    for triggers, response in help_intents:
        if any(trigger in lower_msg for trigger in triggers):
            return jsonify({'reply': response, 'next_state': None})
    if any(name in lower_msg for name in name_intents):
        return jsonify({'reply': "My name is Junate, your assistant for managing tasks efficiently!", 'next_state': None})
    
    # Start task creation if 
    message_options = ['create task', 'add task', 'create a task', 'add a task', 'please create me a task', 'I want to create a task']
    if any(option in user_message.lower() for option in message_options):   
        reply = 'What is the Site Name?'
        state = {'step': 'awaiting_site_name', 'data': {}}
        return jsonify({'reply': reply, 'next_state': state})
    # Default reply
    return jsonify({'reply': "Hi, it's your boy, Junate! Ask me to create a task or help with your dashboard.", 'next_state': None})
