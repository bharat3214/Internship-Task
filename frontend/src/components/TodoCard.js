import React from 'react';
import './TodoCard.css';

function TodoCard({ item, onEdit, onDelete }) {
  const formatDate = (dateString) => {
    if (!dateString) return 'No date';
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit', hour12: true,
      timeZone: 'Asia/Kolkata',
    });
  };

  const prio = (item.priority || 'LOW').toUpperCase();

  return (
    <div className={`todo-card ${item.done ? 'completed' : ''}`}>
      <div className="todo-card-header">
        <div style={{display:'flex', gap:'8px', alignItems:'center'}}>
          <span className={`priority-badge ${prio === 'HIGH' ? 'priority-high' : prio === 'MEDIUM' ? 'priority-medium' : 'priority-low'}`}>
            {prio}
          </span>
          {item.database && (
            <span className={`db-badge ${item.database === 'MongoDB' ? 'mongo' : 'postgres'}`}>{item.database}</span>
          )}
        </div>
        <div>
          <button className="btn-edit" onClick={() => onEdit(item)}>Edit</button>
          <button className="btn-delete" onClick={() => onDelete(item.id)} title="Delete todo">×</button>
        </div>
      </div>

      <div className="todo-card-body">
        <h3 className="todo-task">{item.title || item.task}</h3>
        {item.description && (
          <p className="todo-description">{item.description}</p>
        )}
        <p className="todo-timestamp">
          <span className="clock-icon">🕒</span>
          {formatDate(item.created_at)}
        </p>
      </div>
    </div>
  );
}

export default TodoCard;
