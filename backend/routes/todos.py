from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import todos_mongo_collection, get_postgres_connection
from bson import ObjectId
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

try:
    IST = ZoneInfo('Asia/Kolkata')
except Exception:
    # Fallback when IANA tz data is unavailable; uses fixed offset +05:30
    IST = timezone(timedelta(hours=5, minutes=30))

def _now_utc():
    return datetime.now(timezone.utc)

def _to_ist_iso(dt: datetime | None):
    if not dt:
        return None
    # Treat naive as UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST).isoformat()

def _normalize_priority(p: str | None) -> str:
    if not p:
        return 'LOW'
    p = p.strip().upper()
    return 'HIGH' if p == 'HIGH' else 'MEDIUM' if p == 'MEDIUM' else 'LOW'

todos_bp = Blueprint('todos', __name__)

@todos_bp.route('/add', methods=['POST'])
@jwt_required()
def add_task():
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        title = data.get('title') or data.get('task')  # allow legacy 'task'
        description = data.get('description', '')
        priority = _normalize_priority(data.get('priority'))
        if not title:
            return jsonify({'error': 'title is required'}), 400
        doc = {
            'userId': user_id,
            'task': title,
            'description': description,
            'priority': priority,
            'done': False,
            'created_at': _now_utc(),
            'updated_at': _now_utc(),
        }
        res = todos_mongo_collection.insert_one(doc)
        return jsonify({'message': 'created', 'id': str(res.inserted_id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@todos_bp.route('/list', methods=['GET'])
@jwt_required()
def list_tasks():
    try:
        user_id = get_jwt_identity()
        page = max(int(request.args.get('page', 1)), 1)
        per_page = max(min(int(request.args.get('per_page', 6)), 50), 1)
        sort = request.args.get('sort', 'date')  # 'date' or 'priority'

        match = {'userId': user_id}
        pipeline = [{'$match': match}]
        if sort == 'priority':
            pipeline += [
                {'$addFields': {
                    'prioOrder': {
                        '$switch': {
                            'branches': [
                                {'case': {'$eq': ['$priority', 'HIGH']}, 'then': 0},
                                {'case': {'$eq': ['$priority', 'MEDIUM']}, 'then': 1},
                            ],
                            'default': 2
                        }
                    }
                }},
                {'$sort': {'prioOrder': 1, 'created_at': -1}}
            ]
        else:
            pipeline += [{'$sort': {'created_at': -1}}]

        total = todos_mongo_collection.count_documents(match)
        pipeline += [
            {'$skip': (page - 1) * per_page},
            {'$limit': per_page}
        ]
        items = []
        for t in todos_mongo_collection.aggregate(pipeline):
            items.append({
                'id': str(t['_id']),
                'title': t.get('task'),
                'description': t.get('description', ''),
                'priority': t.get('priority', 'LOW'),
                'done': t.get('done', False),
                'created_at': _to_ist_iso(t.get('created_at')),
                'updated_at': _to_ist_iso(t.get('updated_at')),
            })
        total_pages = (total + per_page - 1) // per_page
        return jsonify({'items': items, 'page': page, 'per_page': per_page, 'total': total, 'total_pages': total_pages}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@todos_bp.route('/edit/<task_id>', methods=['PUT'])
@jwt_required()
def edit_task(task_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        update = {}
        if 'title' in data or 'task' in data:
            update['task'] = data.get('title') or data.get('task')
        if 'description' in data:
            update['description'] = data.get('description') or ''
        if 'priority' in data:
            update['priority'] = _normalize_priority(data.get('priority'))
        if 'done' in data:
            update['done'] = bool(data.get('done'))
        if not update:
            return jsonify({'error': 'no fields to update'}), 400
        update['updated_at'] = _now_utc()
        res = todos_mongo_collection.update_one({'_id': ObjectId(task_id), 'userId': user_id}, {'$set': update})
        if res.matched_count == 0:
            return jsonify({'error': 'not found'}), 404
        return jsonify({'message': 'updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@todos_bp.route('/delete/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    try:
        user_id = get_jwt_identity()
        res = todos_mongo_collection.delete_one({'_id': ObjectId(task_id), 'userId': user_id})
        if res.deleted_count == 0:
            return jsonify({'error': 'not found'}), 404
        return jsonify({'message': 'deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# existing routes retained below for backward compatibility
@todos_bp.route('/todo', methods=['POST'])
@jwt_required()
def create_todo():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        task = data.get('task')
        description = data.get('description', '')
        database = data.get('database', 'mongodb')  # Default to mongodb if not specified

        if not task:
            return jsonify({'error': 'Task is required'}), 400

        if database == 'mongodb':
            # Write to MongoDB only
            mongo_todo = {
                'userId': user_id,
                'task': task,
                'description': description,
                'priority': _normalize_priority(request.json.get('priority')) if request.is_json else 'LOW',
                'done': False,
                'created_at': _now_utc(),
                'updated_at': _now_utc(),
            }
            mongo_result = todos_mongo_collection.insert_one(mongo_todo)
            return jsonify({
                'message': 'Todo created successfully in MongoDB',
                'id': str(mongo_result.inserted_id),
                'database': 'MongoDB'
            }), 201
        
        elif database == 'postgresql':
            # Write to PostgreSQL only
            conn = get_postgres_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO todos (user_id, task, description, priority, done) VALUES (%s, %s, %s, %s, %s) RETURNING id',
                (user_id, task, description, _normalize_priority(request.json.get('priority')) if request.is_json else 'LOW', False)
            )
            postgres_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({
                'message': 'Todo created successfully in PostgreSQL',
                'id': f'pg_{postgres_id}',
                'database': 'PostgreSQL'
            }), 201
        
        else:
            return jsonify({'error': 'Invalid database specified'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@todos_bp.route('/todos', methods=['GET'])
@jwt_required()
def get_todos():
    try:
        user_id = get_jwt_identity()
        db_source = request.args.get('source', 'all')  # 'all', 'mongodb', 'postgresql'

        todos = []

        # Fetch from MongoDB
        if db_source in ['all', 'mongodb']:
            mongo_todos = todos_mongo_collection.find({'userId': user_id}).sort('created_at', -1)
            for todo in mongo_todos:
                todos.append({
                    'id': str(todo['_id']),
                    'task': todo['task'],
                    'description': todo.get('description', ''),
                    'priority': todo.get('priority', 'LOW'),
                    'done': todo['done'],
                    'created_at': _to_ist_iso(todo.get('created_at')),
                    'database': 'MongoDB'
                })

        # Fetch from PostgreSQL
        if db_source in ['all', 'postgresql']:
            conn = get_postgres_connection()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, task, description, priority, done, created_at FROM todos WHERE user_id = %s ORDER BY created_at DESC',
                (user_id,)
            )
            postgres_todos = cursor.fetchall()
            cursor.close()
            conn.close()

            for todo in postgres_todos:
                todos.append({
                    'id': f'pg_{todo[0]}',
                    'task': todo[1],
                    'description': todo[2] or '',
                    'priority': todo[3] or 'LOW',
                    'done': todo[4],
                    'created_at': _to_ist_iso(todo[5]),
                    'database': 'PostgreSQL'
                })

        return jsonify({'todos': todos}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@todos_bp.route('/todo/<todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        # Allow 'title' alias for 'task'
        task = data.get('task') if 'task' in data else data.get('title')
        done = data.get('done')
        description = data.get('description') if 'description' in data else None

        if all(
            field is None for field in [done, task, description]
        ) and 'priority' not in data:
            return jsonify({'message': 'No changes'}), 200

        # Determine which database the todo is from
        if todo_id.startswith('pg_'):
            # Update PostgreSQL only
            postgres_id = int(todo_id.replace('pg_', ''))
            conn = get_postgres_connection()
            cursor = conn.cursor()
            
            update_fields = []
            update_values = []
            if done is not None:
                update_fields.append('done = %s')
                update_values.append(done)
            if task is not None:
                update_fields.append('task = %s')
                update_values.append(task)
            if description is not None:
                update_fields.append('description = %s')
                update_values.append(description)
            if 'priority' in data:
                update_fields.append('priority = %s')
                update_values.append(_normalize_priority(data.get('priority')))
            
            if not update_fields:
                cursor.close(); conn.close()
                return jsonify({'message': 'No changes'}), 200
            update_values.extend([postgres_id, user_id])
            query = f"UPDATE todos SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s"
            cursor.execute(query, tuple(update_values))
            conn.commit()
            cursor.close()
            conn.close()
        else:
            # Update MongoDB only
            update_data = {}
            if done is not None:
                update_data['done'] = done
            if task is not None:
                update_data['task'] = task
            if description is not None:
                update_data['description'] = description
            if 'priority' in data:
                update_data['priority'] = _normalize_priority(data.get('priority'))
            if not update_data:
                return jsonify({'message': 'No changes'}), 200
            update_data['updated_at'] = _now_utc()
            
            todos_mongo_collection.update_one(
                {'_id': ObjectId(todo_id), 'userId': user_id},
                {'$set': update_data}
            )

        return jsonify({'message': 'Todo updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@todos_bp.route('/todo/<todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    try:
        user_id = get_jwt_identity()

        # Determine which database the todo is from
        if todo_id.startswith('pg_'):
            # Delete from PostgreSQL
            postgres_id = int(todo_id.replace('pg_', ''))
            conn = get_postgres_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM todos WHERE id = %s AND user_id = %s', (postgres_id, user_id))
            conn.commit()
            cursor.close()
            conn.close()
        else:
            # Delete from MongoDB
            todos_mongo_collection.delete_one({'_id': ObjectId(todo_id), 'userId': user_id})

        return jsonify({'message': 'Todo deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
