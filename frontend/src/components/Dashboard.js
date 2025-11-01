import React, { useState, useEffect } from 'react';
import { getTodos, createTodo, updateTodo, deleteTodo } from '../services/api';
import TodoCard from './TodoCard';
import './Dashboard.css';

import TodoList from './TodoList';
import './Dashboard.css';

function Dashboard({ onLogout }) {
  const userName = localStorage.getItem('userName');

  const handleLogout = () => {
    localStorage.clear();
    onLogout();
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div className="header-content">
          <h1>Welcome, {userName}!</h1>
          <button onClick={handleLogout} className="btn-logout">Logout</button>
        </div>
      </div>
      <div className="dashboard-content">
        <TodoList />
      </div>
    </div>
  );
}

export default Dashboard;
