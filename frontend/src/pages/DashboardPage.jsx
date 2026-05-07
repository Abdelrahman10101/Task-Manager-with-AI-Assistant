import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../lib/api';
import Modal from '../components/Modal';
import { useAuth } from '../context/AuthContext';

const COLORS = ['#6366f1','#8b5cf6','#ec4899','#f59e0b','#22c55e','#06b6d4','#f97316','#ef4444'];

function ProjectCard({ project }) {
  return (
    <Link to={`/projects/${project.id}`} className="project-card" style={{ '--card-color': project.color }}>
      <div className="project-card-title">{project.title}</div>
      {project.description && <div className="project-card-desc">{project.description}</div>}
      <div className="project-card-footer">
        <span className="badge badge-todo">📋 {project.todo_count} To Do</span>
        <span className="badge badge-in-progress">⚡ {project.in_progress_count} In Progress</span>
        <span className="badge badge-done">✅ {project.done_count} Done</span>
      </div>
    </Link>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', color: '#6366f1' });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const fetchProjects = async () => {
    try {
      const res = await api.get('/projects');
      setProjects(res.data);
    } catch { /* handled by interceptor */ }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchProjects(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) return;
    setSaving(true); setError('');
    try {
      await api.post('/projects', form);
      setShowModal(false);
      setForm({ title: '', description: '', color: '#6366f1' });
      fetchProjects();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project');
    } finally { setSaving(false); }
  };

  const totalTasks = projects.reduce((s, p) => s + p.task_count, 0);
  const totalDone = projects.reduce((s, p) => s + p.done_count, 0);
  const totalInProgress = projects.reduce((s, p) => s + p.in_progress_count, 0);

  return (
    <div className="main-content">
      <div className="dashboard-header">
        <h1>Good day, {user?.name?.split(' ')[0]} 👋</h1>
        <p>Here's an overview of all your projects</p>
      </div>

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-label">Projects</div>
          <div className="stat-value" style={{ color: 'var(--primary)' }}>{projects.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Tasks</div>
          <div className="stat-value">{totalTasks}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">In Progress</div>
          <div className="stat-value" style={{ color: 'var(--warning)' }}>{totalInProgress}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Completed</div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>{totalDone}</div>
        </div>
      </div>

      <div className="section-header">
        <h2>My Projects</h2>
        <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>+ New Project</button>
      </div>

      {loading ? (
        <div className="empty-state"><div className="spinner" style={{ margin: '0 auto' }} /></div>
      ) : projects.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📁</div>
          <h3>No projects yet</h3>
          <p>Create your first project to get started</p>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ Create Project</button>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map(p => <ProjectCard key={p.id} project={p} />)}
        </div>
      )}

      {showModal && (
        <Modal title="New Project" onClose={() => setShowModal(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleCreate} disabled={saving}>
              {saving ? 'Creating…' : 'Create Project'}
            </button>
          </>}>
          {error && <div className="alert alert-error">{error}</div>}
          <div className="form-group">
            <label>Project Title *</label>
            <input className="form-control" placeholder="e.g. E-Commerce Platform"
              value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} autoFocus />
          </div>
          <div className="form-group">
            <label>Description (optional)</label>
            <textarea className="form-control" placeholder="What is this project about?"
              value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          </div>
          <div className="form-group">
            <label>Color</label>
            <div className="color-picker">
              {COLORS.map(c => (
                <div key={c} className={`color-swatch ${form.color === c ? 'active' : ''}`}
                  style={{ background: c }} onClick={() => setForm(f => ({ ...f, color: c }))} />
              ))}
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
