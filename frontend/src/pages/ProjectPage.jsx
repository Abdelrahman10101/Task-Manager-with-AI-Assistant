import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import api from '../lib/api';
import Modal from '../components/Modal';

const STATUSES = ['todo', 'in_progress', 'done'];
const STATUS_LABELS = { todo: 'To Do', in_progress: 'In Progress', done: 'Done' };
const STATUS_COLORS = { todo: 'var(--todo)', in_progress: 'var(--in-progress)', done: 'var(--done)' };
const PRIORITIES = ['low', 'medium', 'high'];

function TaskCard({ task, onUpdate, onDelete }) {
  const handleStatusChange = (e) => onUpdate(task.id, { status: e.target.value });

  return (
    <div className="task-card">
      <div className="task-card-title">{task.title}</div>
      {task.description && <div className="task-card-desc">{task.description}</div>}
      <div className="task-card-footer">
        <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
          <span className={`badge badge-${task.priority}`}>{task.priority}</span>
          <select className="status-select" value={task.status} onChange={handleStatusChange}>
            {STATUSES.map(s => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
          </select>
        </div>
        <div className="task-card-actions">
          <button className="task-action-btn" onClick={() => onDelete(task.id)} title="Delete">🗑️</button>
        </div>
      </div>
    </div>
  );
}

function KanbanColumn({ status, tasks, onUpdate, onDelete }) {
  return (
    <div className="kanban-col">
      <div className="kanban-col-header">
        <span className="kanban-col-title" style={{ color: STATUS_COLORS[status] }}>
          {STATUS_LABELS[status]}
        </span>
        <span className="kanban-count">{tasks.length}</span>
      </div>
      <div className="kanban-tasks">
        {tasks.length === 0
          ? <div style={{ color: 'var(--text-dim)', fontSize: '0.8rem', textAlign: 'center', padding: '1rem' }}>No tasks</div>
          : tasks.map(t => <TaskCard key={t.id} task={t} onUpdate={onUpdate} onDelete={onDelete} />)}
      </div>
    </div>
  );
}

export default function ProjectPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [taskForm, setTaskForm] = useState({ title: '', description: '', priority: 'medium', status: 'todo' });
  const [saving, setSaving] = useState(false);
  const [aiOpen, setAiOpen] = useState(false);
  const [aiSummary, setAiSummary] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [aiSuggestLoading, setAiSuggestLoading] = useState(false);

  const fetchProject = async () => {
    try {
      const res = await api.get(`/projects/${id}`);
      setProject(res.data);
    } catch { navigate('/dashboard'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchProject(); }, [id]);

  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!taskForm.title.trim()) return;
    setSaving(true);
    try {
      await api.post('/tasks', { ...taskForm, project_id: id });
      setShowTaskModal(false);
      setTaskForm({ title: '', description: '', priority: 'medium', status: 'todo' });
      fetchProject();
    } finally { setSaving(false); }
  };

  const handleUpdateTask = async (taskId, updates) => {
    await api.put(`/tasks/${taskId}`, updates);
    fetchProject();
  };

  const handleDeleteTask = async (taskId) => {
    if (!confirm('Delete this task?')) return;
    await api.delete(`/tasks/${taskId}`);
    fetchProject();
  };

  const handleDeleteProject = async () => {
    await api.delete(`/projects/${id}`);
    navigate('/dashboard');
  };

  const handleAISummarize = async () => {
    setAiOpen(true);
    setAiLoading(true);
    setAiSummary('');
    try {
      const res = await api.post('/ai/summarize', { project_id: id });
      setAiSummary(res.data.summary);
    } catch { setAiSummary('Failed to generate summary. Please try again.'); }
    finally { setAiLoading(false); }
  };

  const handleAISuggest = async () => {
    setAiSuggestLoading(true);
    setAiSuggestions([]);
    try {
      const res = await api.post('/ai/suggest', {
        project_title: project.title,
        project_description: project.description,
      });
      setAiSuggestions(res.data.suggestions);
    } finally { setAiSuggestLoading(false); }
  };

  const addSuggestedTask = async (suggestion) => {
    await api.post('/tasks', { ...suggestion, project_id: id });
    fetchProject();
  };

  if (loading) return <div className="main-content"><div className="empty-state"><div className="spinner" style={{ margin: '0 auto' }} /></div></div>;
  if (!project) return null;

  const tasksByStatus = {
    todo: project.tasks.filter(t => t.status === 'todo'),
    in_progress: project.tasks.filter(t => t.status === 'in_progress'),
    done: project.tasks.filter(t => t.status === 'done'),
  };

  return (
    <div className="main-content" style={{ paddingBottom: '5rem' }}>
      <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>

      <div className="project-detail-header">
        <div>
          <h1>{project.title}</h1>
          {project.description && <p>{project.description}</p>}
        </div>
        <div className="project-actions">
          <button className="btn btn-primary btn-sm" onClick={() => setShowTaskModal(true)}>+ Add Task</button>
          <button className="btn btn-danger btn-sm" onClick={() => setShowDeleteModal(true)}>Delete Project</button>
        </div>
      </div>

      <div className="kanban-board">
        {STATUSES.map(status => (
          <KanbanColumn key={status} status={status}
            tasks={tasksByStatus[status]}
            onUpdate={handleUpdateTask}
            onDelete={handleDeleteTask} />
        ))}
      </div>

      {/* AI FAB */}
      <button className="ai-fab" onClick={handleAISummarize}>✨ AI Summary</button>

      {/* AI Panel */}
      {aiOpen && (
        <div className="ai-panel">
          <div className="ai-panel-header">
            <div className="ai-panel-title">✨ AI Insights</div>
            <button className="modal-close" onClick={() => { setAiOpen(false); setAiSuggestions([]); }}>✕</button>
          </div>

          {aiLoading ? (
            <div className="ai-loader">
              <div className="spinner" />
              <span>Analyzing project…</span>
            </div>
          ) : (
            <div className="ai-content">
              <ReactMarkdown>{aiSummary}</ReactMarkdown>
            </div>
          )}

          <div style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border)', paddingTop: '1.5rem' }}>
            <button className="btn btn-ghost btn-sm btn-full" onClick={handleAISuggest} disabled={aiSuggestLoading}>
              {aiSuggestLoading ? 'Generating…' : '💡 Suggest Tasks for This Project'}
            </button>

            {aiSuggestions.length > 0 && (
              <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Click to add to project:</p>
                {aiSuggestions.map((s, i) => (
                  <div key={i} className="task-card" style={{ cursor: 'pointer' }} onClick={() => addSuggestedTask(s)}>
                    <div className="task-card-title">{s.title}</div>
                    <div className="task-card-desc">{s.description}</div>
                    <span className={`badge badge-${s.priority}`}>{s.priority}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Add Task Modal */}
      {showTaskModal && (
        <Modal title="Add Task" onClose={() => setShowTaskModal(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowTaskModal(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleCreateTask} disabled={saving}>
              {saving ? 'Adding…' : 'Add Task'}
            </button>
          </>}>
          <div className="form-group">
            <label>Task Title *</label>
            <input className="form-control" placeholder="e.g. Design landing page"
              value={taskForm.title} onChange={e => setTaskForm(f => ({ ...f, title: e.target.value }))} autoFocus />
          </div>
          <div className="form-group">
            <label>Description (optional)</label>
            <textarea className="form-control" placeholder="Task details…"
              value={taskForm.description} onChange={e => setTaskForm(f => ({ ...f, description: e.target.value }))} />
          </div>
          <div className="form-group">
            <label>Priority</label>
            <select className="form-control" value={taskForm.priority}
              onChange={e => setTaskForm(f => ({ ...f, priority: e.target.value }))}>
              {PRIORITIES.map(p => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Status</label>
            <select className="form-control" value={taskForm.status}
              onChange={e => setTaskForm(f => ({ ...f, status: e.target.value }))}>
              {STATUSES.map(s => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
            </select>
          </div>
        </Modal>
      )}

      {/* Delete Project Modal */}
      {showDeleteModal && (
        <Modal title="Delete Project" onClose={() => setShowDeleteModal(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowDeleteModal(false)}>Cancel</button>
            <button className="btn btn-danger" onClick={handleDeleteProject}>Delete Project</button>
          </>}>
          <p style={{ color: 'var(--text-muted)' }}>
            Are you sure you want to delete <strong style={{ color: 'var(--text)' }}>{project.title}</strong>?
            This will permanently delete all <strong style={{ color: 'var(--danger)' }}>{project.tasks.length} tasks</strong> as well.
          </p>
        </Modal>
      )}
    </div>
  );
}
