import React, { useState } from 'react';
import './Dashboard.css';

const priorities = ['HIGH', 'MEDIUM', 'LOW'];

export default function EditModal({ initial, onClose, onSave }) {
  const [title, setTitle] = useState(initial.title || initial.task || '');
  const [description, setDescription] = useState(initial.description || '');
  const [priority, setPriority] = useState((initial.priority || 'LOW').toUpperCase());

  const submit = (e) => {
    e.preventDefault();
    onSave({ title, description, priority });
  };

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <h3>Edit Task</h3>
        <form onSubmit={submit} className="add-todo-form">
          <input className="todo-input" value={title} onChange={(e)=>setTitle(e.target.value)} placeholder="Title" />
          <textarea className="todo-description" value={description} onChange={(e)=>setDescription(e.target.value)} placeholder="Description" rows={3} />
          <select className="toggle-btn" value={priority} onChange={(e)=>setPriority(e.target.value)}>
            {priorities.map(p=> <option key={p} value={p}>{p}</option>)}
          </select>
          <div className="form-actions" style={{justifyContent:'flex-end'}}>
            <button type="button" className="btn-add" onClick={onClose} style={{background:'#e1e8ed', color:'#333'}}>Cancel</button>
            <button type="submit" className="btn-add">Save</button>
          </div>
        </form>
      </div>
    </div>
  );
}
