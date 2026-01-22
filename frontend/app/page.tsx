'use client';

import { useState, useEffect, Suspense } from 'react';
import Navbar from '@/components/Navbar';
import Card from '@/components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import { scrapeWebsite, chatWithContent, detectForms, getProject, getChatHistory, getLatestScrape } from '../lib/api';
import { ScrapeResult, DetectedForm } from '../lib/types';
import { Globe, MessageSquare, FileText, Search, Sparkles, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { Download, Plus } from 'lucide-react';

function HomeContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated } = useAuth();

  // ... rest of component logic ...

  const [url, setUrl] = useState('');
  const [project, setProject] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'summary' | 'chat' | 'forms'>('summary');
  const [result, setResult] = useState<ScrapeResult | null>(null);
  const [projectId, setProjectId] = useState<number | null>(null);
  const [detectedForms, setDetectedForms] = useState<DetectedForm[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Advanced Options
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [selector, setSelector] = useState('');

  // Chat state
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState<{ role: 'user' | 'assistant'; content: string }[]>([]);

  // Check for auto-trigger from new project button
  // Check for auto-trigger from new project button or load existing project
  useEffect(() => {
    const projectIdParam = searchParams.get('project');
    const newParam = searchParams.get('new');

    const loadProjectData = async (id: number) => {
      setLoading(true);
      try {
        // Fetch project meta
        const projectData = await getProject(id);
        if (projectData) {
          setProject(projectData.name);
          setUrl(projectData.url);
          setProjectId(projectData.id);

          // Fetch chat history
          try {
            const history = await getChatHistory(id);
            if (Array.isArray(history)) {
              setChatHistory(history);
            }
          } catch (e) {
            console.error("Failed to load chat history", e);
          }

          // Fetch latest scrape to show summary/result
          try {
            const latestScrape = await getLatestScrape(id);
            if (latestScrape) {
              setResult(latestScrape);
              // If we have a scraped result, we can default to summary or chat
              setActiveTab('summary');
            } else {
              // Project exists but no scrape yet?
              setActiveTab('chat'); // Or prompt to scrape
            }
          } catch (e) {
            console.error("Failed to load latest scrape", e);
          }
        }
      } catch (e) {
        console.error("Failed to load project", e);
        setError("Failed to load project. It may have been deleted.");
      } finally {
        setLoading(false);
      }
    };

    if (projectIdParam && isAuthenticated) {
      loadProjectData(parseInt(projectIdParam));
    } else if (newParam === 'true' && url) {
      // Just focus
    }
  }, [searchParams, url, isAuthenticated]);

  const handleScrape = async () => {
    if (!url) return;

    // Auth Check: If naming a project, must be logged in
    if (project && !isAuthenticated) {
      if (confirm("You must be logged in to save a named project. Go to login?")) {
        router.push('/login');
      }
      return;
    }

    setLoading(true);
    setError(null);
    try {
      // Pass projectId if we want to add to existing project (Multi-Source), BUT 
      // current UI logic for "Scrape" button usually implies NEW scrape/project unless explicitly adding source.
      // Let's keep main scrape button as "New/Current" context.
      // If projectId exists and we are NOT creating a new named project, maybe we should add to it?
      // For now, let's keep it simple: "Add Source" is a separate action. 
      // Main "Scrape" creates new project if project name provided, or anonymous.

      const data = await scrapeWebsite(url, project, undefined, selector);
      if (data.success) {
        setResult(data);
        setProjectId(data.project_id);
      } else {
        setError(data.error || 'Scraping failed');
      }
    } catch (err: any) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async () => {
    if (!chatInput || !projectId) return;
    const message = chatInput;
    setChatInput('');
    setChatHistory((prev) => [...prev, { role: 'user', content: message }]);
    try {
      const data = await chatWithContent(projectId, message);
      setChatHistory((prev) => [...prev, { role: 'assistant', content: data.response }]);
    } catch (err) {
      setChatHistory((prev) => [...prev, { role: 'assistant', content: 'Failed to get response' }]);
    }
  };

  const handleDetectForms = async () => {
    if (!url) return;
    setLoading(true);
    try {
      const data = await detectForms(url);
      if (data.success) {
        setDetectedForms(data.details.forms);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSource = async () => {
    if (!url || !projectId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await scrapeWebsite(url, undefined, projectId, selector);
      if (data.success) {
        setResult(data);
        // Maybe show toast?
        alert("Source added to project!");
      } else {
        setError(data.error || 'Failed to add source');
      }
    } catch (err: any) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (format: 'json' | 'markdown') => {
    if (!result) return;

    let content = '';
    let filename = `scrape-${result.id}.${format === 'json' ? 'json' : 'md'}`;
    let type = format === 'json' ? 'application/json' : 'text/markdown';

    if (format === 'json') {
      content = JSON.stringify(result, null, 2);
    } else {
      content = `# ${result.summary?.slice(0, 50)}...\n\n`;
      content += `**Source**: ${result.url}\n`;
      content += `**Date**: ${result.created_at}\n\n`;
      content += `## Summary\n${result.summary}\n\n`;
      content += `## Key Points\n${result.key_points?.map(p => `- ${p}`).join('\n')}\n`;
    }

    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <main className="min-h-screen bg-black/90 text-white selection:bg-primary/30">
      <Navbar />

      {/* Background Ambience */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[128px] animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/10 rounded-full blur-[128px] animate-pulse delay-1000" />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-32 space-y-12">
        {/* Header */}
        <header className="text-center space-y-6 mb-16 relative">
          <div className="inline-flex items-center justify-center px-4 py-1.5 rounded-full bg-white/5 border border-white/10 mb-4 backdrop-blur-xl shadow-lg shadow-primary/10 animate-fade-in-up">
            <span className="w-2 h-2 rounded-full bg-success mr-2 animate-pulse" />
            <span className="text-xs font-medium text-white/80 tracking-wide uppercase">System Operational</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
            Web Scraping, <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary via-accent to-secondary animate-gradient">
              Reimagined with AI
            </span>
          </h1>

          <p className="text-xl text-white/60 max-w-2xl mx-auto font-light leading-relaxed">
            Extract content, analyze forms, and chat with any website instantly using our multi-model AI engine.
          </p>
        </header>

        <Card className="max-w-3xl mx-auto backdrop-blur-xl">
          <div className="space-y-4 p-2">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 space-y-4 md:space-y-0">
                <Input
                  placeholder="Enter website URL (e.g., https://example.com)"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="text-lg"
                />
                <div className="flex gap-2">
                  <Input
                    placeholder="Project Name (Optional)"
                    value={project}
                    onChange={(e) => setProject(e.target.value)}
                    className="text-sm mt-2 opacity-80 flex-1"
                  />
                  <button
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="text-xs text-white/50 hover:text-white underline mt-2"
                  >
                    {showAdvanced ? 'Hide Options' : 'Advanced Options'}
                  </button>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <Button
                  onClick={handleScrape}
                  isLoading={loading}
                  className="md:w-48 h-auto"
                >
                  <Search className="w-5 h-5 mr-2" />
                  Scrape
                </Button>

                {projectId && (
                  <Button
                    onClick={handleAddSource}
                    isLoading={loading}
                    variant="secondary"
                    className="md:w-48 h-auto text-xs"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Source
                  </Button>
                )}
              </div>
            </div>

            {showAdvanced && (
              <div className="pt-4 border-t border-white/10 animate-fade-in-down">
                <label className="text-xs text-white/60 mb-1 block">CSS Selector (Optional)</label>
                <Input
                  placeholder="e.g. .article-content, #main-text"
                  value={selector}
                  onChange={(e) => setSelector(e.target.value)}
                  className="text-sm font-mono"
                />
                <p className="text-[10px] text-white/40 mt-1">
                  Only scrape text from specific elements. Leave empty for full page.
                </p>
              </div>
            )}
          </div>
        </Card>

        {/* Error Message */}
        {error && (
          <div className="max-w-3xl mx-auto bg-error/10 border border-error/20 text-error rounded-xl p-4 flex items-center">
            <AlertCircle className="w-5 h-5 mr-3" />
            {error}
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="space-y-6 animate-in slide-in-from-bottom-10 fade-in duration-500">
            {/* Tabs */}
            <div className="flex justify-center space-x-2 p-1 bg-white/5 backdrop-blur-lg rounded-xl max-w-fit mx-auto border border-white/10">
              {[
                { id: 'summary', icon: FileText, label: 'Summary' },
                { id: 'chat', icon: MessageSquare, label: 'Chat' },
                { id: 'forms', icon: Globe, label: 'Forms' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center px-6 py-2.5 rounded-lg transition-all duration-300 font-medium ${activeTab === tab.id
                    ? 'bg-primary text-white shadow-lg shadow-primary/25'
                    : 'text-white/60 hover:text-white hover:bg-white/10'
                    }`}
                >
                  <tab.icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Content Area */}
            <div className="grid md:grid-cols-3 gap-6">
              {/* Main Content */}
              <Card className="md:col-span-2 min-h-[500px]">
                {activeTab === 'summary' && (
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-xl font-semibold mb-3 flex items-center justify-between text-primary">
                        <div className="flex items-center">
                          <Sparkles className="w-5 h-5 mr-2" />
                          AI Summary
                        </div>

                        <div className="flex gap-2">
                          <button
                            onClick={() => handleExport('json')}
                            className="text-xs bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-lg transition-colors flex items-center border border-white/10"
                          >
                            <Download className="w-3 h-3 mr-1.5" />
                            JSON
                          </button>
                          <button
                            onClick={() => handleExport('markdown')}
                            className="text-xs bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-lg transition-colors flex items-center border border-white/10"
                          >
                            <Download className="w-3 h-3 mr-1.5" />
                            Markdown
                          </button>
                        </div>
                      </h3>
                      <p className="text-white/80 leading-relaxed text-lg">
                        {result.summary}
                      </p>
                    </div>

                    {result.key_points && (
                      <div>
                        <h3 className="text-lg font-semibold mb-3 text-secondary">Key Points</h3>
                        <ul className="space-y-3">
                          {result.key_points.map((point, i) => (
                            <li key={i} className="flex items-start bg-white/5 p-3 rounded-lg border border-white/5">
                              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-secondary/20 text-secondary flex items-center justify-center text-sm mr-3 mt-0.5">
                                {i + 1}
                              </span>
                              <span className="text-white/80">{point}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'chat' && (
                  <div className="flex flex-col h-full h-[500px]">
                    <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2 custom-scrollbar">
                      {chatHistory.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-white/30">
                          <MessageSquare className="w-12 h-12 mb-2 opacity-50" />
                          <p>Ask questions about the scraped content</p>
                        </div>
                      )}
                      {chatHistory.map((msg, i) => (
                        <div
                          key={i}
                          className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-[80%] p-4 rounded-2xl ${msg.role === 'user'
                              ? 'bg-primary text-white rounded-br-none'
                              : 'bg-white/10 text-white/90 rounded-bl-none'
                              }`}
                          >
                            <div className="prose prose-invert prose-sm">
                              <ReactMarkdown>
                                {msg.content}
                              </ReactMarkdown>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="flex gap-2 mt-auto">
                      <Input
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        placeholder="Ask a question..."
                        onKeyPress={(e) => e.key === 'Enter' && handleChat()}
                      />
                      <Button onClick={handleChat} disabled={!chatInput}>Send</Button>
                    </div>
                  </div>
                )}

                {activeTab === 'forms' && (
                  <div className="space-y-6">
                    {!detectedForms && (
                      <div className="text-center py-12">
                        <Button onClick={handleDetectForms} isLoading={loading}>
                          Detect Forms on Page
                        </Button>
                      </div>
                    )}

                    {detectedForms?.map((form, i) => (
                      <div key={i} className="bg-white/5 p-6 rounded-xl border border-white/10">
                        <h4 className="text-lg font-semibold mb-4 flex justify-between items-center">
                          <span>Form #{i + 1}</span>
                          <span className="text-xs bg-white/10 px-2 py-1 rounded">
                            {form.method}
                          </span>
                        </h4>
                        <div className="space-y-2">
                          {form.fields.map((field, j) => (
                            <div key={j} className="flex items-center text-sm text-white/60 bg-black/20 p-2 rounded">
                              <span className="w-24 font-mono text-accent">{field.type}</span>
                              <span className="flex-1">{field.name}</span>
                              {field.required && (
                                <span className="text-xs text-error bg-error/10 px-1.5 py-0.5 rounded">Required</span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </Card>

              {/* Sidebar Info */}
              <div className="space-y-6">
                <Card>
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-white/40 mb-4">
                    Scrape Details
                  </h3>
                  <div className="space-y-4">
                    <div className="space-y-1">
                      <p className="text-xs text-white/40">Status</p>
                      <div className={`flex items-center ${result.status === 'FAILED' ? 'text-error' : 'text-success'}`}>
                        <span className={`w-2 h-2 rounded-full mr-2 ${result.status === 'FAILED' ? 'bg-error' : 'bg-success animate-pulse'}`} />
                        {result.status || 'Completed'}
                      </div>
                      {result.error_message && (
                        <p className="text-xs text-error mt-1">{result.error_message}</p>
                      )}
                    </div>
                    <div className="space-y-1">
                      <p className="text-xs text-white/40">Method Used</p>
                      <p className="font-mono text-sm">{result.scrape_method}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-xs text-white/40">AI Provider</p>
                      <p className="font-mono text-sm capitalize">{result.ai_provider}</p>
                    </div>
                  </div>
                </Card>

                {result.entities && (
                  <Card>
                    <h3 className="text-sm font-semibold uppercase tracking-wider text-white/40 mb-4">
                      Detected Entities
                    </h3>
                    <div className="space-y-4">
                      {Object.entries(result.entities).map(([key, values]) => {
                        if (!values || values.length === 0) return null;
                        return (
                          <div key={key}>
                            <p className="text-xs text-secondary capitalize mb-2">{key}</p>
                            <div className="flex flex-wrap gap-2">
                              {values.slice(0, 5).map((v, k) => (
                                <span key={k} className="text-xs bg-white/5 px-2 py-1 rounded border border-white/5">
                                  {v}
                                </span>
                              ))}
                              {values.length > 5 && (
                                <span className="text-xs text-white/40 px-1">+{values.length - 5} more</span>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </Card>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
    </Suspense >
  );
}
