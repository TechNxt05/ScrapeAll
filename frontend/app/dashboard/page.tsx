'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, Clock, Search, ExternalLink, Trash2 } from 'lucide-react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import Button from '@/components/Button';
import Card from '@/components/Card';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { Project } from '@/lib/types';

export default function DashboardPage() {
    const { user, isAuthenticated, loading: authLoading } = useAuth();
    const router = useRouter();
    const [projects, setProjects] = useState<Project[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!authLoading && !isAuthenticated) {
            router.push('/login');
            return;
        }

        if (isAuthenticated) {
            fetchProjects();
        }
    }, [isAuthenticated, authLoading, router]);

    const fetchProjects = async () => {
        try {
            const data = await api.get('/api/projects').then(res => res.data);
            setProjects(data);
        } catch (e) {
            console.error("Failed to fetch projects", e);
        } finally {
            setLoading(false);
        }
    };

    const deleteProject = async (id: number) => {
        if (!confirm('Are you sure you want to delete this project?')) return;
        try {
            await api.delete(`/api/projects/${id}`);
            setProjects(projects.filter(p => p.id !== id));
        } catch (e) {
            console.error("Failed to delete", e);
        }
    };

    if (authLoading || loading) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-black text-white relative font-sans">
            <Navbar />

            <main className="pt-32 px-6 max-w-7xl mx-auto pb-20">
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-10 gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-white mb-2">Project Manager</h1>
                        <p className="text-white/40">Manage your scraping workspaces and history.</p>
                    </div>

                    <Link href="/?new=true">
                        <Button variant="primary" icon={Plus}>
                            Create Project
                        </Button>
                    </Link>
                </div>

                {projects.length === 0 ? (
                    <div className="text-center py-20 border border-dashed border-white/10 rounded-2xl bg-white/5">
                        <Search className="w-12 h-12 text-white/20 mx-auto mb-4" />
                        <h3 className="text-xl font-medium text-white mb-2">No projects yet</h3>
                        <p className="text-white/40 mb-6">Start your first scraping project to see it here.</p>
                        <Link href="/?new=true">
                            <Button variant="outline">Start Scraping</Button>
                        </Link>
                    </div>
                ) : (
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {projects.map((project) => (
                            <Card key={project.id} className="relative group hover:border-primary/50 transition-colors">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="p-2 rounded-lg bg-primary/10">
                                        <Search className="w-5 h-5 text-primary" />
                                    </div>
                                    <button
                                        onClick={(e) => { e.preventDefault(); deleteProject(project.id); }}
                                        className="p-2 text-white/20 hover:text-error transition-colors"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>

                                <h3 className="text-lg font-semibold text-white mb-2 truncate">
                                    {project.name}
                                </h3>

                                <div className="flex items-center gap-2 text-sm text-white/40 mb-4">
                                    <ExternalLink className="w-3 h-3" />
                                    <span className="truncate max-w-[200px]">{project.url}</span>
                                </div>

                                <div className="flex items-center justify-between mt-auto pt-4 border-t border-white/5">
                                    <div className="flex items-center gap-1.5 text-xs text-white/30">
                                        <Clock className="w-3 h-3" />
                                        <span>{new Date(project.created_at).toLocaleDateString()}</span>
                                    </div>
                                    <Link href={`/?project=${project.id}`} className="text-xs font-medium text-primary hover:text-white transition-colors">
                                        View Workspace →
                                    </Link>
                                </div>
                            </Card>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}
