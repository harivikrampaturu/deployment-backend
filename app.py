from gevent import monkey
monkey.patch_all()

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from uuid import uuid4
from datetime import datetime, timezone
from flask_socketio import SocketIO, emit, join_room, leave_room
""" import requests
from typing import List, Dict, Any """

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')

# Configure CORS with environment variable
allowed_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '*')
CORS(app, resources={r"/*": {"origins": allowed_origins}})

socketio = SocketIO(app, cors_allowed_origins=allowed_origins)

# Mock databases with realistic test data
resources_db = [
    # American resources
    {'id': 'r1', 'name': 'John Smith', 'role': 'DEVELOPER', 'team': 'Frontend', 'availability': 100},
    {'id': 'r2', 'name': 'Sarah Johnson', 'role': 'DESIGNER', 'team': 'UX', 'availability': 100},
    {'id': 'r3', 'name': 'Michael Brown', 'role': 'PROJECT_MANAGER', 'team': 'Product', 'availability': 100},
    {'id': 'r4', 'name': 'Emily Davis', 'role': 'QA_ENGINEER', 'team': 'QA', 'availability': 100},
    {'id': 'r5', 'name': 'David Wilson', 'role': 'DEVELOPER', 'team': 'Backend', 'availability': 100},
    {'id': 'r6', 'name': 'Jessica Miller', 'role': 'BUSINESS_ANALYST', 'team': 'Product', 'availability': 100},
    {'id': 'r7', 'name': 'Robert Taylor', 'role': 'DEVOPS_ENGINEER', 'team': 'DevOps', 'availability': 100},
    {'id': 'r8', 'name': 'Jennifer Anderson', 'role': 'DATA_SCIENTIST', 'team': 'Data', 'availability': 100},
    {'id': 'r9', 'name': 'Christopher Thomas', 'role': 'DEVELOPER', 'team': 'Backend', 'availability': 100},
    {'id': 'r10', 'name': 'Lisa Martinez', 'role': 'TECHNICAL_WRITER', 'team': 'Product', 'availability': 100},
    {'id': 'r11', 'name': 'Daniel Clark', 'role': 'DEVELOPER', 'team': 'Frontend', 'availability': 100},
    {'id': 'r12', 'name': 'Michelle Lee', 'role': 'DESIGNER', 'team': 'UX', 'availability': 100},
    {'id': 'r13', 'name': 'James Rodriguez', 'role': 'QA_ENGINEER', 'team': 'QA', 'availability': 100},
    {'id': 'r14', 'name': 'Ashley White', 'role': 'DEVELOPER', 'team': 'Backend', 'availability': 100},
    {'id': 'r15', 'name': 'Kevin Walker', 'role': 'DEVOPS_ENGINEER', 'team': 'DevOps', 'availability': 100},
    
    # Indian resources
    {'id': 'r16', 'name': 'Arun Sharma', 'role': 'DEVELOPER', 'team': 'Backend', 'availability': 100},
    {'id': 'r17', 'name': 'Priya Patel', 'role': 'DESIGNER', 'team': 'UX', 'availability': 100},
    {'id': 'r18', 'name': 'Rahul Kumar', 'role': 'PROJECT_MANAGER', 'team': 'Product', 'availability': 100},
    {'id': 'r19', 'name': 'Neha Singh', 'role': 'QA_ENGINEER', 'team': 'QA', 'availability': 100},
    {'id': 'r20', 'name': 'Vikram Desai', 'role': 'DEVELOPER', 'team': 'Frontend', 'availability': 100},
    {'id': 'r21', 'name': 'Anjali Gupta', 'role': 'BUSINESS_ANALYST', 'team': 'Product', 'availability': 100},
    {'id': 'r22', 'name': 'Suresh Reddy', 'role': 'DEVOPS_ENGINEER', 'team': 'DevOps', 'availability': 100},
    {'id': 'r23', 'name': 'Meera Joshi', 'role': 'DATA_SCIENTIST', 'team': 'Data', 'availability': 100},
    {'id': 'r24', 'name': 'Rajesh Malhotra', 'role': 'DEVELOPER', 'team': 'Backend', 'availability': 100},
    {'id': 'r25', 'name': 'Sunita Verma', 'role': 'TECHNICAL_WRITER', 'team': 'Product', 'availability': 100},
    {'id': 'r26', 'name': 'Amit Choudhary', 'role': 'DEVELOPER', 'team': 'Frontend', 'availability': 100},
    {'id': 'r27', 'name': 'Divya Kapoor', 'role': 'DESIGNER', 'team': 'UX', 'availability': 100},
    {'id': 'r28', 'name': 'Sanjay Iyer', 'role': 'QA_ENGINEER', 'team': 'QA', 'availability': 100},
    {'id': 'r29', 'name': 'Pooja Agarwal', 'role': 'DEVELOPER', 'team': 'Backend', 'availability': 100},
    {'id': 'r30', 'name': 'Kiran Nair', 'role': 'DEVOPS_ENGINEER', 'team': 'DevOps', 'availability': 100}
]

projects_db = [
    {'id': 'p1', 'name': 'Customer Portal Redesign', 'phase': 'IN_PROGRESS', 'startDate': '2025-01-15', 'endDate': '2025-06-30', 'description': 'Revamp the customer portal with modern UI and improved UX'},
    {'id': 'p2', 'name': 'Data Analytics Platform', 'phase': 'PLANNING', 'startDate': '2025-04-01', 'endDate': '2025-09-30', 'description': 'Build a comprehensive data analytics solution for business insights'},
    {'id': 'p3', 'name': 'Mobile App Development', 'phase': 'IN_PROGRESS', 'startDate': '2025-02-10', 'endDate': '2025-07-15', 'description': 'Develop cross-platform mobile application for iOS and Android'},
    {'id': 'p4', 'name': 'Infrastructure Migration', 'phase': 'ON_HOLD', 'startDate': '2025-03-01', 'endDate': '2025-08-31', 'description': 'Migrate on-premise infrastructure to cloud-based solutions'},
    {'id': 'p5', 'name': 'Security Compliance Upgrade', 'phase': 'PLANNING', 'startDate': '2025-05-15', 'endDate': '2025-11-30', 'description': 'Implement enhanced security measures to meet regulatory requirements'},
    {'id': 'p6', 'name': 'E-commerce Integration', 'phase': 'IN_PROGRESS', 'startDate': '2025-01-05', 'endDate': '2025-05-20', 'description': 'Integrate e-commerce capabilities into existing platform'},
    {'id': 'p7', 'name': 'Legacy System Modernization', 'phase': 'COMPLETED', 'startDate': '2023-10-01', 'endDate': '2025-03-31', 'description': 'Modernize legacy systems with current technologies'},
    {'id': 'p8', 'name': 'Enterprise CRM Implementation', 'phase': 'IN_PROGRESS', 'startDate': '2025-02-15', 'endDate': '2025-08-15', 'description': 'Deploy and customize enterprise CRM solution'},
    {'id': 'p9', 'name': 'AI Chatbot Development', 'phase': 'PLANNING', 'startDate': '2025-05-01', 'endDate': '2025-10-31', 'description': 'Develop AI-powered chatbot for customer service'},
    {'id': 'p10', 'name': 'Supply Chain Optimization', 'phase': 'ON_HOLD', 'startDate': '2025-04-15', 'endDate': '2025-09-15', 'description': 'Optimize supply chain processes and logistics workflow'}
]

allocations_db = [
    # Project 1 allocations
    {'id': 'a1', 'resourceId': 'r1', 'projectId': 'p1', 'percentage': 50, 'startDate': '2025-01-15', 'endDate': '2025-06-30'},
    {'id': 'a2', 'resourceId': 'r2', 'projectId': 'p1', 'percentage': 75, 'startDate': '2025-01-15', 'endDate': '2025-06-30'},
    {'id': 'a3', 'resourceId': 'r20', 'projectId': 'p1', 'percentage': 60, 'startDate': '2025-01-15', 'endDate': '2025-06-30'},
    {'id': 'a4', 'resourceId': 'r27', 'projectId': 'p1', 'percentage': 80, 'startDate': '2025-01-15', 'endDate': '2025-06-30'},
    
    # Project 2 allocations - increased percentages
    {'id': 'a5', 'resourceId': 'r5', 'projectId': 'p2', 'percentage': 60, 'startDate': '2025-04-01', 'endDate': '2025-09-30'},
    {'id': 'a6', 'resourceId': 'r8', 'projectId': 'p2', 'percentage': 70, 'startDate': '2025-04-01', 'endDate': '2025-09-30'},
    {'id': 'a7', 'resourceId': 'r23', 'projectId': 'p2', 'percentage': 80, 'startDate': '2025-04-01', 'endDate': '2025-09-30'},
    
    # Project 3 allocations
    {'id': 'a8', 'resourceId': 'r11', 'projectId': 'p3', 'percentage': 65, 'startDate': '2025-02-10', 'endDate': '2025-07-15'},
    {'id': 'a9', 'resourceId': 'r16', 'projectId': 'p3', 'percentage': 55, 'startDate': '2025-02-10', 'endDate': '2025-07-15'},
    {'id': 'a10', 'resourceId': 'r26', 'projectId': 'p3', 'percentage': 70, 'startDate': '2025-02-10', 'endDate': '2025-07-15'},
    {'id': 'a11', 'resourceId': 'r19', 'projectId': 'p3', 'percentage': 45, 'startDate': '2025-02-10', 'endDate': '2025-07-15'},
    
    # Project 4 allocations
    {'id': 'a12', 'resourceId': 'r7', 'projectId': 'p4', 'percentage': 60, 'startDate': '2025-03-01', 'endDate': '2025-08-31'},
    {'id': 'a13', 'resourceId': 'r15', 'projectId': 'p4', 'percentage': 50, 'startDate': '2025-03-01', 'endDate': '2025-08-31'},
    {'id': 'a14', 'resourceId': 'r22', 'projectId': 'p4', 'percentage': 75, 'startDate': '2025-03-01', 'endDate': '2025-08-31'},
    
    # Project 5 allocations - increased percentages
    {'id': 'a15', 'resourceId': 'r9', 'projectId': 'p5', 'percentage': 65, 'startDate': '2025-05-15', 'endDate': '2025-11-30'},
    {'id': 'a16', 'resourceId': 'r24', 'projectId': 'p5', 'percentage': 60, 'startDate': '2025-05-15', 'endDate': '2025-11-30'},
    
    # Project 6 allocations
    {'id': 'a17', 'resourceId': 'r1', 'projectId': 'p6', 'percentage': 40, 'startDate': '2025-01-05', 'endDate': '2025-05-20'},
    {'id': 'a18', 'resourceId': 'r5', 'projectId': 'p6', 'percentage': 50, 'startDate': '2025-01-05', 'endDate': '2025-05-20'},
    {'id': 'a19', 'resourceId': 'r29', 'projectId': 'p6', 'percentage': 60, 'startDate': '2025-01-05', 'endDate': '2025-05-20'},
    
    # Project 7 allocations
    {'id': 'a20', 'resourceId': 'r14', 'projectId': 'p7', 'percentage': 80, 'startDate': '2023-10-01', 'endDate': '2025-03-31'},
    {'id': 'a21', 'resourceId': 'r16', 'projectId': 'p7', 'percentage': 35, 'startDate': '2023-10-01', 'endDate': '2025-03-31'},
    {'id': 'a22', 'resourceId': 'r13', 'projectId': 'p7', 'percentage': 45, 'startDate': '2023-10-01', 'endDate': '2025-03-31'},
    
    # Project 8 allocations
    {'id': 'a23', 'resourceId': 'r3', 'projectId': 'p8', 'percentage': 70, 'startDate': '2025-02-15', 'endDate': '2025-08-15'},
    {'id': 'a24', 'resourceId': 'r6', 'projectId': 'p8', 'percentage': 50, 'startDate': '2025-02-15', 'endDate': '2025-08-15'},
    {'id': 'a25', 'resourceId': 'r21', 'projectId': 'p8', 'percentage': 60, 'startDate': '2025-02-15', 'endDate': '2025-08-15'},
    
    # Project 9 allocations - increased percentages
    {'id': 'a26', 'resourceId': 'r8', 'projectId': 'p9', 'percentage': 30, 'startDate': '2025-05-01', 'endDate': '2025-10-31'},
    {'id': 'a27', 'resourceId': 'r23', 'projectId': 'p9', 'percentage': 20, 'startDate': '2025-05-01', 'endDate': '2025-10-31'},
    {'id': 'a28', 'resourceId': 'r17', 'projectId': 'p9', 'percentage': 65, 'startDate': '2025-05-01', 'endDate': '2025-10-31'},
    
    # Project 10 allocations - increased percentages
    {'id': 'a29', 'resourceId': 'r18', 'projectId': 'p10', 'percentage': 65, 'startDate': '2025-04-15', 'endDate': '2025-09-15'},
    {'id': 'a30', 'resourceId': 'r25', 'projectId': 'p10', 'percentage': 70, 'startDate': '2025-04-15', 'endDate': '2025-09-15'},
    
    # Adding allocations for more resources that previously had 0%
    {'id': 'a31', 'resourceId': 'r4', 'projectId': 'p1', 'percentage': 55, 'startDate': '2025-01-15', 'endDate': '2025-06-30'},
    {'id': 'a32', 'resourceId': 'r10', 'projectId': 'p3', 'percentage': 40, 'startDate': '2025-02-10', 'endDate': '2025-07-15'},
    {'id': 'a33', 'resourceId': 'r12', 'projectId': 'p1', 'percentage': 65, 'startDate': '2025-01-15', 'endDate': '2025-06-30'},
    {'id': 'a34', 'resourceId': 'r28', 'projectId': 'p5', 'percentage': 50, 'startDate': '2025-05-15', 'endDate': '2025-11-30'},
    {'id': 'a35', 'resourceId': 'r30', 'projectId': 'p8', 'percentage': 60, 'startDate': '2025-02-15', 'endDate': '2025-08-15'}
]

notifications_db = []

@app.route('/projects', methods=['GET', 'POST', 'PUT', 'DELETE'])
def projects():
    if request.method == 'GET':
        # Enhance projects with resource allocations
        enhanced_projects = []
        for project in projects_db:
            project_allocations = [
                {
                    **alloc,
                    'resourceDetails': next(
                        (r for r in resources_db if r['id'] == alloc['resourceId']),
                        None
                    )
                }
                for alloc in allocations_db 
                if alloc['projectId'] == project['id']
            ]
            project_with_resources = {
                **project,
                'resources': project_allocations
            }
            enhanced_projects.append(project_with_resources)
        
        print("Enhanced Projects:", enhanced_projects)  # Debug log
        return jsonify(enhanced_projects)
    
    elif request.method == 'POST':
        project = request.get_json()
        project['id'] = str(uuid4())
        project['createdAt'] = datetime.now(timezone.utc).isoformat()
        project['updatedAt'] = datetime.now(timezone.utc).isoformat()
        
        # Ensure resources is initialized as an empty array if not provided
        resources = project.pop('resources', [])
        project['resources'] = []  # Initialize empty resources array
        projects_db.append(project)
        
        # Create resource allocations
        for resource in resources:
            allocation = {
                'id': str(uuid4()),
                'resourceId': resource['resourceId'],
                'projectId': project['id'],
                'percentage': resource['percentage'],
                'startDate': project['startDate'],
                'endDate': project['endDate']
            }
            allocations_db.append(allocation)
            project['resources'].append(allocation)  # Add to project's resources
        
        print("Created Project:", project)  # Debug log
        return jsonify(project), 201
    
    elif request.method == 'PUT':
        project = request.get_json()
        for i, p in enumerate(projects_db):
            if p['id'] == project['id']:
                # Ensure we're updating only the fields that were sent
                projects_db[i].update({
                    'phase': project.get('phase', p['phase']),
                    'startDate': project.get('startDate', p['startDate']),
                    'endDate': project.get('endDate', p['endDate']),
                    'updatedAt': datetime.now(timezone.utc).isoformat()
                })
                return jsonify(projects_db[i])
        return jsonify({'error': 'Project not found'}), 404

@app.route('/resources', methods=['GET', 'POST', 'PUT', 'DELETE'])
def resources():
    if request.method == 'GET':
        # Enhance resources with their allocations
        enhanced_resources = []
        for resource in resources_db:
            resource_allocations = [
                {
                    **alloc,
                    'allocation': alloc['percentage'],  # Add allocation field for frontend
                    'projectDetails': next(
                        (p for p in projects_db if p['id'] == alloc['projectId']),
                        None
                    )
                }
                for alloc in allocations_db 
                if alloc['resourceId'] == resource['id']
            ]
            resource_with_allocations = {
                **resource,
                'allocations': resource_allocations
            }
            enhanced_resources.append(resource_with_allocations)
        return jsonify(enhanced_resources)
    
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
                resources_db[i] = {
                    **r,
                    **resource,
                    'updatedAt': datetime.now(timezone.utc).isoformat()
                }
                return jsonify(resources_db[i])
        return jsonify({'error': 'Resource not found'}), 404
    
    elif request.method == 'DELETE':
        resource_id = request.args.get('id')
        # Remove resource allocations first
        allocations_db[:] = [a for a in allocations_db if a['resourceId'] != resource_id]
        # Then remove the resource
        resources_db[:] = [r for r in resources_db if r['id'] != resource_id]
        return jsonify({'message': 'Resource deleted'}), 200

@app.route('/projects/<project_id>/resources', methods=['POST', 'GET'])
def project_resources(project_id):
    if request.method == 'GET':
        project_allocations = [
            {
                **alloc,
                'allocation': alloc['percentage'],  # Add allocation field for frontend
                'resourceDetails': next(
                    (r for r in resources_db if r['id'] == alloc['resourceId']),
                    None
                )
            }
            for alloc in allocations_db 
            if alloc['projectId'] == project_id
        ]
        return jsonify(project_allocations)
    
    elif request.method == 'POST':
        data = request.get_json()
        allocation_value = int(data['allocation'])  # Convert to integer
        new_allocation = {
            'id': str(uuid4()),
            'resourceId': data['resourceId'],
            'projectId': project_id,
            'percentage': allocation_value,  # Store as percentage
            'allocation': allocation_value,  # Add allocation field for frontend
            'startDate': data.get('startDate', ''),
            'endDate': data.get('endDate', '')
        }
        
        # Debug print
        print(f"Received allocation data: {data}")
        print(f"Creating new allocation: {new_allocation}")
        
        existing = next(
            (a for a in allocations_db 
             if a['resourceId'] == data['resourceId'] and a['projectId'] == project_id),
            None
        )
        
        if existing:
            existing.update(new_allocation)
            return jsonify(existing), 200
        else:
            allocations_db.append(new_allocation)
            return jsonify(new_allocation), 201

@app.route('/projects/<project_id>/resources/<resource_id>', methods=['PUT', 'DELETE'])
def manage_project_resource(project_id, resource_id):
    # Find existing allocation
    allocation = next(
        (a for a in allocations_db 
         if a['resourceId'] == resource_id and a['projectId'] == project_id),
        None
    )
    
    if request.method == 'PUT':
        data = request.get_json()
        new_allocation_value = int(data['allocation'])
        
        # Get resource details
        resource = next((r for r in resources_db if r['id'] == resource_id), None)
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
            
        # Calculate total allocation excluding current project
        total_other_allocations = sum(
            a['percentage'] for a in allocations_db 
            if a['resourceId'] == resource_id and a['projectId'] != project_id
        )
        
        # Check if new allocation is within limits
        if total_other_allocations + new_allocation_value > 100:
            return jsonify({
                'error': 'Total allocation cannot exceed 100%',
                'available': 100 - total_other_allocations
            }), 400
            
        if allocation:
            allocation['percentage'] = new_allocation_value
            allocation['allocation'] = new_allocation_value  # Update both fields
            return jsonify(allocation), 200
            
        return jsonify({'error': 'Allocation not found'}), 404
        
    elif request.method == 'DELETE':
        if allocation:
            allocations_db.remove(allocation)
            return jsonify({'message': 'Resource allocation removed'}), 200
        return jsonify({'error': 'Allocation not found'}), 404

@app.route('/resources/<resource_id>/projects', methods=['GET'])
def resource_projects(resource_id):
    # Get all projects where this resource is allocated
    resource_allocations = [
        alloc for alloc in allocations_db 
        if alloc['resourceId'] == resource_id
    ]
    
    # Get the full project details for each allocation
    resource_projects = []
    for allocation in resource_allocations:
        project = next(
            (p for p in projects_db if p['id'] == allocation['projectId']), 
            None
        )
        if project:
            project_with_allocation = {
                **project,
                'allocation': allocation['percentage']
            }
            resource_projects.append(project_with_allocation)
    
    return jsonify(resource_projects)

@app.route('/projects/<project_id>', methods=['GET', 'PUT'])
def get_project(project_id):
    if request.method == 'GET':
        project = next((p for p in projects_db if p['id'] == project_id), None)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Enhance project with resource allocations
        project_allocations = [
            {
                **alloc,
                'resourceDetails': next(
                    (r for r in resources_db if r['id'] == alloc['resourceId']),
                    None
                )
            }
            for alloc in allocations_db 
            if alloc['projectId'] == project_id
        ]
        
        project_with_resources = {
            **project,
            'resources': project_allocations
        }
        
        return jsonify(project_with_resources)
        
    elif request.method == 'PUT':
        project = request.get_json()
        for i, p in enumerate(projects_db):
            if p['id'] == project_id:
                projects_db[i].update({
                    'phase': project.get('phase', p['phase']),
                    'startDate': project.get('startDate', p['startDate']),
                    'endDate': project.get('endDate', p['endDate']),
                    'updatedAt': datetime.now(timezone.utc).isoformat()
                })
                return jsonify(projects_db[i])
        return jsonify({'error': 'Project not found'}), 404

@app.route('/reports/project/<project_id>', methods=['GET'])
def get_project_report(project_id):
    project = next((p for p in projects_db if p['id'] == project_id), None)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Get project allocations
    project_allocations = [
        alloc for alloc in allocations_db 
        if alloc['projectId'] == project_id
    ]
    
    # Calculate metrics
    resource_count = len(project_allocations)
    avg_utilization = sum(alloc['percentage'] for alloc in project_allocations) / resource_count if resource_count > 0 else 0
    
    # Calculate timeline deviation (mock data for now)
    timeline_deviation = 0  # In real app, calculate based on planned vs actual dates
    
    report = {
        'metrics': {
            'resourceUtilization': round(avg_utilization, 1),
            'timelineDeviation': timeline_deviation,
            'resourceCount': resource_count
        },
        'risks': [
            'Resource utilization is below optimal levels' if avg_utilization < 70 else 'Resource allocation is optimal',
            'Timeline may need adjustment' if timeline_deviation != 0 else 'Project is on schedule'
        ],
        'recommendations': [
            'Consider adding more resources' if resource_count < 3 else 'Team size is appropriate',
            'Review resource allocations' if avg_utilization < 70 else 'Maintain current resource allocation'
        ]
    }
    
    return jsonify(report)

@app.route('/resources/<resource_id>', methods=['PUT', 'DELETE'])
def manage_resource(resource_id):
    if request.method == 'PUT':
        try:
            resource = request.get_json()
            for i, r in enumerate(resources_db):
                if r['id'] == resource_id:
                    # Keep existing fields if not provided in update
                    updated_resource = {
                        **r,  # Keep existing data
                        **resource,  # Update with new data
                        'updatedAt': datetime.now(timezone.utc).isoformat()
                    }
                    resources_db[i] = updated_resource
                    return jsonify(updated_resource)
            return jsonify({'error': 'Resource not found'}), 404
        except Exception as e:
            print(f"Error updating resource: {str(e)}")  # Debug log
            return jsonify({'error': 'Failed to update resource'}), 500

    elif request.method == 'DELETE':
        try:
            # Remove resource allocations first
            allocations_db[:] = [a for a in allocations_db if a['resourceId'] != resource_id]
            # Then remove the resource
            resource = next((r for r in resources_db if r['id'] == resource_id), None)
            if resource:
                resources_db.remove(resource)
                return jsonify({'message': 'Resource deleted'}), 200
            return jsonify({'error': 'Resource not found'}), 404
        except Exception as e:
            print(f"Error deleting resource: {str(e)}")  # Debug log
            return jsonify({'error': 'Failed to delete resource'}), 500

""" @app.route('/api/projects/import-tpm', methods=['POST'])
def import_tpm_projects():
    try:
        # TODO: Replace with your actual TPM API endpoint and credentials
        TPM_API_ENDPOINT = os.environ.get('TPM_API_ENDPOINT', 'https://tpm-api.example.com')
        TPM_API_KEY = os.environ.get('TPM_API_KEY', '')

        # Fetch projects from TPM
        response = requests.get(
            f"{TPM_API_ENDPOINT}/projects",
            headers={"Authorization": f"Bearer {TPM_API_KEY}"}
        )
        
        if not response.ok:
            return jsonify({
                'error': 'Failed to fetch data from TPM',
                'message': response.text
            }), response.status_code

        tpm_projects = response.json()
        imported_projects: List[Dict[str, Any]] = []

        for tpm_project in tpm_projects:
            # Transform TPM project data to our format
            new_project = {
                'id': str(uuid4()),
                'name': tpm_project.get('title', ''),
                'phase': map_tpm_phase(tpm_project.get('status', '')),
                'startDate': tpm_project.get('startDate', ''),
                'endDate': tpm_project.get('endDate', ''),
                'description': tpm_project.get('description', ''),
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }

            # Check if project already exists (by name)
            existing_project = next(
                (p for p in projects_db if p['name'] == new_project['name']),
                None
            )

            if existing_project:
                # Update existing project
                existing_project.update(new_project)
                imported_projects.append(existing_project)
            else:
                # Add new project
                projects_db.append(new_project)
                imported_projects.append(new_project)

        return jsonify({
            'message': f'Successfully imported {len(imported_projects)} projects',
            'projects': imported_projects
        })

    except requests.RequestException as e:
        return jsonify({
            'error': 'Failed to connect to TPM service',
            'message': str(e)
        }), 503
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

def map_tpm_phase(tpm_status: str) -> str:
    ""Map TPM status to our project phases""
    status_mapping = {
        'NOT_STARTED': 'PLANNING',
        'IN_PROGRESS': 'IN_PROGRESS',
        'ON_HOLD': 'ON_HOLD',
        'COMPLETED': 'COMPLETED',
        # Add more mappings as needed
    }
    return status_mapping.get(tpm_status, 'PLANNING') """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4000))
    socketio.run(app, 
                host='0.0.0.0', 
                port=port,
                debug=os.environ.get('FLASK_ENV') != 'production')