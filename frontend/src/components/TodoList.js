import React, { useEffect, useState, useMemo } from 'react';
import { createTodo, getTodos, updateTodo, deleteTodo } from '../services/api';
import TodoCard from './TodoCard';
import EditModal from './EditModal';
import Pagination from './Pagination';
import './Dashboard.css';

const priorities = ['HIGH', 'MEDIUM', 'LOW'];
const sources = ['all', 'mongodb', 'postgresql'];

export default function TodoList() {
  const [allItems, setAllItems] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [sort, setSort] = useState('date');
  const [source, setSource] = useState('all');

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('LOW');
  const [selectedDatabase, setSelectedDatabase] = useState('mongodb');

  const [editing, setEditing] = useState(null);

  const perPage = 6;

  const sortedItems = useMemo(() => {
    const arr = [...allItems];
    if (sort === 'priority') {
      const order = { HIGH: 0, MEDIUM: 1, LOW: 2 };
      arr.sort((a,b)=> (order[(a.priority||'LOW').toUpperCase()] - order[(b.priority||'LOW').toUpperCase()]) || (new Date(b.created_at) - new Date(a.created_at)) );
    } else {
      arr.sort((a,b)=> new Date(b.created_at) - new Date(a.created_at));
    }
    return arr;
  }, [allItems, sort]);

  const totalPages = Math.max(1, Math.ceil(sortedItems.length / perPage));
  const pageItems = useMemo(() => {
    const start = (page - 1) * perPage;
    return sortedItems.slice(start, start + perPage);
  }, [sortedItems, page]);

  const fetchAll = async (src = source) => {
    setLoading(true);
    try {
      const { data } = await getTodos(src);
      setAllItems(data.todos || []);
      setPage(1);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(source); }, [source]);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    await createTodo(title.trim(), description.trim(), selectedDatabase, priority);
    setTitle(''); setDescription(''); setPriority('LOW');
    fetchAll(source);
  };

  const onDelete = async (id) => {
    if (!window.confirm('Delete this task?')) return;
    await deleteTodo(id);
    // If page becomes empty, step back
    const after = sortedItems.length - 1;
    const newTotalPages = Math.max(1, Math.ceil(after / perPage));
    if (page > newTotalPages) setPage(newTotalPages);
    fetchAll(source);
  };

  const onSaveEdit = async (id, payload) => {
    await updateTodo(id, payload);
    setEditing(null);
    fetchAll(source);
  };

  return (
    <>
      <div className="add-todo-section">
        <form onSubmit={onSubmit} className="add-todo-form">
          <div className="form-inputs">
            <input className="todo-input" placeholder="Title" value={title} onChange={(e)=>setTitle(e.target.value)} />
            <input className="todo-description" placeholder="Description" value={description} onChange={(e)=>setDescription(e.target.value)} />
          </div>
          <div className="form-actions">
            <div className="database-selector">
              <label>Save to:</label>
              <div className="database-toggle">
                <button type="button" className={`toggle-btn ${selectedDatabase==='mongodb'?'active':''}`} onClick={()=>setSelectedDatabase('mongodb')}>MongoDB</button>
                <button type="button" className={`toggle-btn ${selectedDatabase==='postgresql'?'active':''}`} onClick={()=>setSelectedDatabase('postgresql')}>PostgreSQL</button>
              </div>
            </div>
            <div className="database-selector">
              <label>Priority:</label>
              <div className="database-toggle">
                <select className="toggle-btn" value={priority} onChange={(e)=>setPriority(e.target.value)}>
                  {priorities.map(p=> <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
            </div>
            <button type="submit" className="btn-add">Add Task</button>
          </div>
        </form>
      </div>

      <div className="filter-section">
        <label>Show</label>
        <div className="filter-buttons" style={{marginBottom:'10px'}}>
          {sources.map(s => (
            <button key={s} className={`filter-btn ${source===s?'active':''}`} onClick={()=>setSource(s)}>{s.toUpperCase()}</button>
          ))}
        </div>
        <label>Sort</label>
        <div className="filter-buttons">
          <button className={`filter-btn ${sort==='date' ? 'active':''}`} onClick={()=>setSort('date')}>Newest</button>
          <button className={`filter-btn ${sort==='priority' ? 'active':''}`} onClick={()=>setSort('priority')}>Priority</button>
        </div>
      </div>

      <div className="todos-grid">
        {loading ? (
          <p className="loading-text">Loading...</p>
        ) : pageItems.length === 0 ? (
          <p className="empty-text">No tasks.</p>
        ) : (
          pageItems.map((it) => (
            <TodoCard key={it.id} item={it} onEdit={setEditing} onDelete={onDelete} />
          ))
        )}
      </div>

      <Pagination page={page} totalPages={totalPages} onPageChange={(p)=>setPage(p)} />

      {editing && (
        <EditModal
          initial={editing}
          onClose={()=>setEditing(null)}
          onSave={(payload)=>onSaveEdit(editing.id, payload)}
        />
      )}
    </>
  );
}
