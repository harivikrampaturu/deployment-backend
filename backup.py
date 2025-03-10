from gevent import monkey
monkey.patch_all()

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from uuid import uuid4
from datetime import datetime, timezone
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')

# Configure CORS with environment variable
allowed_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '*')
CORS(app, resources={r"/*": {"origins": allowed_origins}})

socketio = SocketIO(app, cors_allowed_origins=allowed_origins)

# Mock databases
projects_db = []
resources_db = []
allocations_db = []
notifications_db = []
chat_messages_db = []
tasks_db = []

@app.route('/projects', methods=['GET', 'POST', 'PUT', 'DELETE'])
def projects():
    if request.method == 'GET':
        return jsonify(projects_db)
    
    elif request.method == 'POST':
        project = request.get_json()
        project['id'] = str(uuid4())
        project['createdAt'] = datetime.now(timezone.utc).isoformat()
        project['updatedAt'] = datetime.now(timezone.utc).isoformat()
        projects_db.append(project)
        return jsonify(project), 201
    
    elif request.method == 'PUT':
        project = request.get_json()
        for i, p in enumerate(projects_db):
            if p['id'] == project['id']:
                projects_db[i] = {**p, **project, 'updatedAt': datetime.now(timezone.utc).isoformat()}
                return jsonify(projects_db[i])
        return jsonify({'error': 'Project not found'}), 404
    
    elif request.method == 'DELETE':
        project_id = request.args.get('id')
        projects_db[:] = [p for p in projects_db if p['id'] != project_id]
        return jsonify({'message': 'Project deleted'}), 200

@app.route('/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    project = next((p for p in projects_db if p['id'] == project_id), None)
    if project is None:
        return jsonify({'error': 'Project not found'}), 404
    return jsonify(project)

@app.route('/resources', methods=['GET', 'POST', 'PUT', 'DELETE'])
def resources():
    if request.method == 'GET':
        return jsonify(resources_db)
    
    elif request.method == 'POST':
        resource = request.get_json()
        new_resource = {
            'id': str(uuid4()),
            'name': resource['name'],
            'alias': resource.get('alias', ''),
            'role': resource['role'],
            'team': resource['team'],
            'availability': resource.get('availability', 100),
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'updatedAt': datetime.now(timezone.utc).isoformat()
        }
        resources_db.append(new_resource)
        return jsonify(new_resource), 201
    
    elif request.method == 'PUT':
        resource = request.get_json()
        for i, r in enumerate(resources_db):
            if r['id'] == resource['id']:
                resources_db[i] = {**r, **resource, 'updatedAt': datetime.now(timezone.utc).isoformat()}
                return jsonify(resources_db[i])
        return jsonify({'error': 'Resource not found'}), 404
    
    elif request.method == 'DELETE':
        resource_id = request.args.get('id')
        resources_db[:] = [r for r in resources_db if r['id'] != resource_id]
        return jsonify({'message': 'Resource deleted'}), 200

# Add all other routes from local_server.py
@app.route('/projects/import/tpm', methods=['POST'])
def import_tpm():
    data = request.get_json()
    new_project = {
        'id': str(uuid4()),
        'name': f"TPM Import {len(projects_db) + 1}",
        'phase': 'PLANNING',
        'startDate': datetime.now(timezone.utc).isoformat(),
        'endDate': datetime.now(timezone.utc).isoformat(),
        'resources': []
    }
    projects_db.append(new_project)
    return jsonify(new_project), 201

@app.route('/projects/export/jira', methods=['POST'])
def export_jira():
    project_id = request.args.get('id')
    return jsonify({'jiraId': f'JIRA-{project_id}'}), 200

@app.route('/reports/project/<project_id>', methods=['GET'])
def project_report(project_id):
    project = next((p for p in projects_db if p['id'] == project_id), None)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    project_resources = [r for r in resources_db if any(
        a.get('projectId') == project_id 
        for a in r.get('allocations', [])
    )]
    
    project_tasks = [t for t in tasks_db if t.get('projectId') == project_id]
    
    total_tasks = len(project_tasks)
    completed_tasks = len([t for t in project_tasks if t.get('status') == 'COMPLETED'])
    
    phase_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    total_allocation = sum(
        next((a['allocation'] for a in r.get('allocations', []) 
             if a.get('projectId') == project_id), 0)
        for r in project_resources
    )
    resource_count = len(project_resources)
    avg_utilization = (total_allocation / resource_count) if resource_count > 0 else 0
    
    if project.get('startDate') and project.get('endDate'):
        planned_end = datetime.fromisoformat(project['endDate'].replace('Z', '+00:00'))
        current_date = datetime.now(timezone.utc).replace(tzinfo=None)
        planned_end = planned_end.replace(tzinfo=None)
        timeline_deviation = (current_date - planned_end).days if current_date > planned_end else 0
    else:
        timeline_deviation = 0
    
    return jsonify({
        'projectId': project_id,
        'metrics': {
            'resourceUtilization': round(avg_utilization, 2),
            'phaseProgress': round(phase_progress, 2),
            'timelineDeviation': timeline_deviation,
            'resourceCount': resource_count,
            'totalTasks': total_tasks,
            'completedTasks': completed_tasks
        },
        'risks': [
            'High resource utilization' if avg_utilization > 80 else None,
            f'Project delayed by {timeline_deviation} days' if timeline_deviation > 0 else None,
            'Behind schedule' if phase_progress < 50 and timeline_deviation > 0 else None
        ],
        'recommendations': [
            'Consider adding more resources' if avg_utilization > 80 else None,
            'Review and adjust project timeline' if timeline_deviation > 0 else None,
            'Evaluate task priorities and resource allocation' if phase_progress < 50 and timeline_deviation > 0 else None
        ]
    })

@app.route('/notifications', methods=['POST'])
def create_notification():
    notification = request.get_json()
    notification['id'] = str(uuid4())
    notification['timestamp'] = datetime.now(timezone.utc).isoformat()
    notifications_db.append(notification)
    
    socketio.emit('notification', notification)
    return jsonify(notification), 201

@app.route('/chat', methods=['GET'])
def get_chat_messages():
    project_id = request.args.get('projectId')
    if project_id:
        messages = [m for m in chat_messages_db if m.get('projectId') == project_id]
    else:
        messages = chat_messages_db
    return jsonify(messages)

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    message = {
        'id': str(uuid4()),
        'userId': request.sid,
        'userName': 'User ' + request.sid[:4],
        'content': data['content'],
        'projectId': data.get('projectId'),
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    chat_messages_db.append(message)
    
    if message.get('projectId'):
        emit('message', message, room=message['projectId'])
    else:
        emit('message', message, broadcast=True)

@socketio.on('join')
def on_join(data):
    room = data['projectId']
    join_room(room)

@socketio.on('leave')
def on_leave(data):
    room = data['projectId']
    leave_room(room)

# Tasks routes
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'GET':
        project_id = request.args.get('projectId')
        if project_id:
            return jsonify([t for t in tasks_db if t.get('projectId') == project_id])
        return jsonify(tasks_db)
    
    elif request.method == 'POST':
        task = request.get_json()
        task['id'] = str(uuid4())
        task['createdAt'] = datetime.now(timezone.utc).isoformat()
        task['updatedAt'] = datetime.now(timezone.utc).isoformat()
        tasks_db.append(task)
        return jsonify(task), 201

@app.route('/tasks/<task_id>', methods=['GET', 'PATCH', 'DELETE'])
def task(task_id):
    task_index = next((i for i, t in enumerate(tasks_db) if t['id'] == task_id), None)
    
    if task_index is None:
        return jsonify({'error': 'Task not found'}), 404
    
    if request.method == 'GET':
        return jsonify(tasks_db[task_index])
    
    elif request.method == 'PATCH':
        updates = request.get_json()
        tasks_db[task_index] = {
            **tasks_db[task_index],
            **updates,
            'updatedAt': datetime.now(timezone.utc).isoformat()
        }
        return jsonify(tasks_db[task_index])
    
    elif request.method == 'DELETE':
        deleted_task = tasks_db.pop(task_index)
        return jsonify(deleted_task)

# Resource allocation routes
@app.route('/projects/<project_id>/resources', methods=['POST'])
def assign_project_resource(project_id):
    project = next((p for p in projects_db if p['id'] == project_id), None)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    resource_allocation = request.get_json()
    resource_id = resource_allocation.get('resourceId')
    allocation = resource_allocation.get('allocation', 0)

    resource = next((r for r in resources_db if r['id'] == resource_id), None)
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404

    current_allocations = sum(
        alloc.get('allocation', 0)
        for alloc in resource.get('allocations', [])
        if alloc.get('projectId') != project_id
    )

    if current_allocations + allocation > resource['availability']:
        return jsonify({
            'error': 'Resource does not have enough availability',
            'available': resource['availability'] - current_allocations
        }), 400

    if 'allocations' not in resource:
        resource['allocations'] = []

    resource['allocations'] = [
        a for a in resource['allocations']
        if a.get('projectId') != project_id
    ]

    resource['allocations'].append({
        'projectId': project_id,
        'allocation': allocation
    })

    return jsonify(resource)

@app.route('/projects/<project_id>/resources/<resource_id>', methods=['PUT', 'DELETE'])
def manage_project_resource(project_id, resource_id):
    resource = next((r for r in resources_db if r['id'] == resource_id), None)
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404

    if request.method == 'PUT':
        allocation_data = request.get_json()
        new_allocation = allocation_data.get('allocation', 0)

        current_allocations = sum(
            alloc.get('allocation', 0)
            for alloc in resource.get('allocations', [])
            if alloc.get('projectId') != project_id
        )

        if current_allocations + new_allocation > resource['availability']:
            return jsonify({
                'error': 'Resource does not have enough availability',
                'available': resource['availability'] - current_allocations
            }), 400

        for alloc in resource.get('allocations', []):
            if alloc.get('projectId') == project_id:
                alloc['allocation'] = new_allocation
                break

        return jsonify(resource)

    elif request.method == 'DELETE':
        resource['allocations'] = [
            alloc for alloc in resource.get('allocations', [])
            if alloc.get('projectId') != project_id
        ]
        return jsonify(resource)

@app.route('/projects/<project_id>/phase', methods=['PUT'])
def update_project_phase(project_id):
    project = next((p for p in projects_db if p['id'] == project_id), None)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    data = request.get_json()
    phase = data.get('phase')
    start_date = data.get('startDate')
    end_date = data.get('endDate')

    # Update project details
    project['phase'] = phase
    project['startDate'] = start_date
    project['endDate'] = end_date
    project['updatedAt'] = datetime.now(timezone.utc).isoformat()

    return jsonify(project)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4000))
    socketio.run(app, 
                host='0.0.0.0', 
                port=port,
                debug=os.environ.get('FLASK_ENV') != 'production') 