import React, { useState, useEffect } from 'react';

interface ResponseOptions {
  tones: string[];
  formats: string[];
  audience_levels: string[];
  quick_response_types: string[];
  grade_levels: string[];
  default_values: {
    tone: string;
    format_type: string;
    audience_level: string;
    max_tokens: number;
    temperature: number;
    use_context: boolean;
  };
}

interface TailoredChatRequest {
  question: string;
  topic: string;
  tone?: string;
  format_type?: string;
  audience_level?: string;
  custom_instructions?: string;
  persona?: string;
  max_tokens?: number;
  temperature?: number;
  use_context?: boolean;
}

interface TailoredChatResponse {
  answer: string;
  sources: string[];
  used_context: string[];
  llm_model: string;
  response_config: Record<string, any>;
  confidence?: number;
  processing_time: number;
}

const TailoredChatInterface: React.FC = () => {
  const [options, setOptions] = useState<ResponseOptions | null>(null);
  const [request, setRequest] = useState<TailoredChatRequest>({
    question: '',
    topic: 'Science',
    tone: 'friendly',
    format_type: 'paragraph',
    audience_level: 'high_school',
    custom_instructions: '',
    persona: '',
    max_tokens: 512,
    temperature: 0.7,
    use_context: true
  });
  const [response, setResponse] = useState<TailoredChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load response options on component mount
  useEffect(() => {
    fetchResponseOptions();
  }, []);

  const fetchResponseOptions = async () => {
    try {
      const res = await fetch('/api/v1/chat/response-options');
      if (res.ok) {
        const data = await res.json();
        setOptions(data);
        // Set defaults from API
        setRequest(prev => ({
          ...prev,
          ...data.default_values
        }));
      }
    } catch (err) {
      console.error('Failed to fetch response options:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!request.question.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await fetch('/api/v1/chat/tailored', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (res.ok) {
        const data = await res.json();
        setResponse(data);
      } else {
        const errorData = await res.json();
        setError(errorData.detail || 'Failed to get response');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof TailoredChatRequest, value: any) => {
    setRequest(prev => ({ ...prev, [field]: value }));
  };

  if (!options) {
    return <div className="p-4">Loading response options...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h1 className="text-2xl font-bold text-green-600 mb-6">
        🎯 Tailored AI Responses
      </h1>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Question Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Question
          </label>
          <textarea
            value={request.question}
            onChange={(e) => handleInputChange('question', e.target.value)}
            placeholder="Ask your question here..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            rows={3}
            required
          />
        </div>

        {/* Topic Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Subject/Topic
          </label>
          <select
            value={request.topic}
            onChange={(e) => handleInputChange('topic', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="Mathematics">Mathematics</option>
            <option value="Science">Science</option>
            <option value="English">English</option>
            <option value="History">History</option>
            <option value="Geography">Geography</option>
            <option value="Technology">Technology</option>
          </select>
        </div>

        {/* Response Customization Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Tone Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Response Tone
            </label>
            <select
              value={request.tone}
              onChange={(e) => handleInputChange('tone', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {options.tones.map(tone => (
                <option key={tone} value={tone}>
                  {tone.replace('_', ' ').split(' ').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                  ).join(' ')}
                </option>
              ))}
            </select>
          </div>

          {/* Format Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Response Format
            </label>
            <select
              value={request.format_type}
              onChange={(e) => handleInputChange('format_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {options.formats.map(format => (
                <option key={format} value={format}>
                  {format.replace('_', ' ').split(' ').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                  ).join(' ')}
                </option>
              ))}
            </select>
          </div>

          {/* Audience Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Audience Level
            </label>
            <select
              value={request.audience_level}
              onChange={(e) => handleInputChange('audience_level', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {options.audience_levels.map(level => (
                <option key={level} value={level}>
                  {level.replace('_', ' ').split(' ').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                  ).join(' ')}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Advanced Options */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-800">Advanced Options</h3>
          
          {/* Custom Instructions */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Custom Instructions (Optional)
            </label>
            <textarea
              value={request.custom_instructions}
              onChange={(e) => handleInputChange('custom_instructions', e.target.value)}
              placeholder="Add specific instructions for the AI response..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              rows={2}
            />
          </div>

          {/* Persona */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AI Persona (Optional)
            </label>
            <input
              type="text"
              value={request.persona}
              onChange={(e) => handleInputChange('persona', e.target.value)}
              placeholder="e.g., 'You are an enthusiastic science teacher'"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          {/* Technical Parameters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Tokens: {request.max_tokens}
              </label>
              <input
                type="range"
                min="50"
                max="2048"
                step="50"
                value={request.max_tokens}
                onChange={(e) => handleInputChange('max_tokens', parseInt(e.target.value))}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Temperature: {request.temperature}
              </label>
              <input
                type="range"
                min="0.1"
                max="2.0"
                step="0.1"
                value={request.temperature}
                onChange={(e) => handleInputChange('temperature', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="use_context"
                checked={request.use_context}
                onChange={(e) => handleInputChange('use_context', e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="use_context" className="text-sm font-medium text-gray-700">
                Use Document Context
              </label>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !request.question.trim()}
          className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
        >
          {loading ? 'Generating Response...' : 'Get Tailored Response'}
        </button>
      </form>

      {/* Error Display */}
      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Response Display */}
      {response && (
        <div className="mt-6 space-y-4">
          <h3 className="text-lg font-bold text-gray-800">Response</h3>
          
          {/* Response Content */}
          <div className="p-4 bg-gray-50 border border-gray-200 rounded-md">
            <div className="prose max-w-none">
              {response.answer.split('\n').map((paragraph, index) => (
                <p key={index} className="mb-2">{paragraph}</p>
              ))}
            </div>
          </div>

          {/* Response Metadata */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
            <div>
              <p><strong>Model:</strong> {response.llm_model}</p>
              <p><strong>Processing Time:</strong> {response.processing_time.toFixed(2)}s</p>
              <p><strong>Confidence:</strong> {response.confidence ? `${(response.confidence * 100).toFixed(1)}%` : 'N/A'}</p>
            </div>
            <div>
              <p><strong>Configuration:</strong></p>
              <p>• Tone: {response.response_config.tone}</p>
              <p>• Format: {response.response_config.format}</p>
              <p>• Audience: {response.response_config.audience_level}</p>
            </div>
          </div>

          {/* Sources */}
          {response.sources.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-800">Sources:</h4>
              <ul className="list-disc list-inside text-sm text-gray-600">
                {response.sources.map((source, index) => (
                  <li key={index}>{source}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TailoredChatInterface;
