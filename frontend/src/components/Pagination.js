import React from 'react';
import './Dashboard.css';

export default function Pagination({ page, totalPages, onPageChange }) {
  const prev = () => page > 1 && onPageChange(page - 1);
  const next = () => page < totalPages && onPageChange(page + 1);

  if (totalPages <= 1) return null;

  return (
    <div style={{display:'flex', justifyContent:'center', gap:'10px', marginTop:'20px'}}>
      <button className="filter-btn" disabled={page===1} onClick={prev}>Previous</button>
      <span className="loading-text" style={{color:'#333'}}>Page {page} of {totalPages}</span>
      <button className="filter-btn" disabled={page===totalPages} onClick={next}>Next</button>
    </div>
  );
}
