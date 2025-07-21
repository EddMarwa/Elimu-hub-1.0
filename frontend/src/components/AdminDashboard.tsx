'use client';

import { useState, useEffect, useCallback } from 'react';

interface AdminStats {
  total_documents: number;
  total_topics: number;
  total_users: number;
  storage_used_mb: number;
  recent_uploads: Array<{
    id: number;
    filename: string;
    topic: string;
    upload_date: string;
    size_mb: number;
    pages: number;
  }>;
  system_health: {
    database: string;
    vector_store: string;
    llm: string;
    storage: string;
  };
}

interface KnowledgeBaseTopic {
  topic_name: string;
  document_count: number;
  total_pages: number;
  total_size_mb: number;
  last_updated: string;
  embedding_count: number;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBaseTopic[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [uploadFiles, setUploadFiles] = useState<FileList | null>(null);
  const [uploadTopic, setUploadTopic] = useState('');
  const [uploadDescription, setUploadDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'overview' | 'upload' | 'knowledge' | 'logs'>('overview');

  const apiBaseUrl = 'http://localhost:8000/api/v1';

  const fetchStats = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiBaseUrl}/admin/dashboard/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  }, []);

  const fetchKnowledgeBase = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiBaseUrl}/admin/knowledge-base/overview`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setKnowledgeBase(data.topics || []);
      }
    } catch (error) {
      console.error('Error fetching knowledge base:', error);
    }
  }, []);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      await Promise.all([fetchStats(), fetchKnowledgeBase()]);
      setIsLoading(false);
    };
    loadData();
  }, [fetchStats, fetchKnowledgeBase]);

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFiles || uploadFiles.length === 0 || !uploadTopic.trim()) {
      alert('Please select files and enter a topic name');
      return;
    }

    setIsUploading(true);
    setUploadProgress('Preparing files...');

    try {
      const token = localStorage.getItem('access_token');
      const formData = new FormData();
      
      formData.append('topic', uploadTopic.trim());
      formData.append('description', uploadDescription.trim());
      
      for (let i = 0; i < uploadFiles.length; i++) {
        formData.append('files', uploadFiles[i]);
      }

      setUploadProgress('Uploading files...');
      
      const response = await fetch(`${apiBaseUrl}/admin/upload/training-files`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setUploadProgress(`Upload successful! Job ID: ${result.job_id}`);
        
        // Reset form
        setUploadFiles(null);
        setUploadTopic('');
        setUploadDescription('');
        
        // Refresh data
        await fetchStats();
        await fetchKnowledgeBase();
        
        setTimeout(() => {
          setUploadProgress('');
        }, 3000);
      } else {
        const error = await response.json();
        setUploadProgress(`Upload failed: ${error.detail}`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadProgress('Upload failed: Network error');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteTopic = async (topicName: string) => {
    if (!confirm(`Are you sure you want to delete the topic "${topicName}" and all its documents?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiBaseUrl}/admin/knowledge-base/${topicName}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        alert('Topic deleted successfully');
        await fetchStats();
        await fetchKnowledgeBase();
      } else {
        const error = await response.json();
        alert(`Delete failed: ${error.detail}`);
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert('Delete failed: Network error');
    }
  };

  const handleRetrainTopic = async (topicName: string) => {
    if (!confirm(`Are you sure you want to retrain embeddings for "${topicName}"?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiBaseUrl}/admin/knowledge-base/retrain/${topicName}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Retrain started: ${result.message}`);
      } else {
        const error = await response.json();
        alert(`Retrain failed: ${error.detail}`);
      }
    } catch (error) {
      console.error('Retrain error:', error);
      alert('Retrain failed: Network error');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-gray-600">Manage your AI knowledge base and system</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-sm text-gray-500">
                Last updated: {new Date().toLocaleTimeString()}
              </div>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              >
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'upload', label: 'Upload Files' },
              { id: 'knowledge', label: 'Knowledge Base' },
              { id: 'logs', label: 'System Logs' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="text-2xl">📄</div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-500">Total Documents</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.total_documents}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="text-2xl">📚</div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-500">Topics</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.total_topics}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="text-2xl">👥</div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-500">Users</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.total_users}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="text-2xl">💾</div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-500">Storage Used</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.storage_used_mb.toFixed(1)} MB</p>
                  </div>
                </div>
              </div>
            </div>

            {/* System Health */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">System Health</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(stats.system_health).map(([component, status]) => (
                    <div key={component} className="flex items-center gap-2">
                      <div
                        className={`h-3 w-3 rounded-full ${
                          status === 'healthy' ? 'bg-green-500' : 
                          status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                      ></div>
                      <span className="text-sm text-gray-700 capitalize">
                        {component.replace('_', ' ')}: {status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recent Uploads */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Recent Uploads</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        File
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Topic
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Size
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Pages
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Uploaded
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {stats.recent_uploads.map((upload) => (
                      <tr key={upload.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {upload.filename}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {upload.topic}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {upload.size_mb.toFixed(1)} MB
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {upload.pages}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(upload.upload_date).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="max-w-2xl">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Upload Training Files</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Upload PDF files to train your AI knowledge base
                </p>
              </div>
              <div className="p-6">
                <form onSubmit={handleFileUpload} className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Topic Name *
                    </label>
                    <input
                      type="text"
                      value={uploadTopic}
                      onChange={(e) => setUploadTopic(e.target.value)}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., Mathematics, Physics, Biology"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Description
                    </label>
                    <textarea
                      value={uploadDescription}
                      onChange={(e) => setUploadDescription(e.target.value)}
                      rows={3}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Optional description for this topic"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      PDF Files *
                    </label>
                    <input
                      type="file"
                      multiple
                      accept=".pdf"
                      onChange={(e) => setUploadFiles(e.target.files)}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Select one or more PDF files (max 50MB each)
                    </p>
                  </div>

                  {uploadProgress && (
                    <div className={`p-4 rounded-md ${
                      uploadProgress.includes('successful') ? 'bg-green-50 text-green-700' :
                      uploadProgress.includes('failed') ? 'bg-red-50 text-red-700' :
                      'bg-blue-50 text-blue-700'
                    }`}>
                      {uploadProgress}
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={isUploading}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {isUploading ? (
                      <div className="flex items-center gap-2">
                        <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Uploading...
                      </div>
                    ) : (
                      'Upload Files'
                    )}
                  </button>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Knowledge Base Tab */}
        {activeTab === 'knowledge' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Knowledge Base Topics</h3>
              <p className="text-sm text-gray-600 mt-1">
                Manage your AI training topics and documents
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Topic
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Documents
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Pages
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Size
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Embeddings
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {knowledgeBase.map((topic) => (
                    <tr key={topic.topic_name}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {topic.topic_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {topic.document_count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {topic.total_pages}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {topic.total_size_mb.toFixed(1)} MB
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {topic.embedding_count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleRetrainTopic(topic.topic_name)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Retrain
                          </button>
                          <button
                            onClick={() => handleDeleteTopic(topic.topic_name)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* System Logs Tab */}
        {activeTab === 'logs' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">System Logs</h3>
              <p className="text-sm text-gray-600 mt-1">
                Recent system activity and errors
              </p>
            </div>
            <div className="p-6">
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-auto h-96">
                <p>System logs would appear here...</p>
                <p>This feature requires additional backend implementation.</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
