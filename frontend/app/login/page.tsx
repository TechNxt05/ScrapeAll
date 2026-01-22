'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Sparkles, ArrowRight, Loader2 } from 'lucide-react';
import Button from '../../components/Button';
import Input from '../../components/Input';
import Card from '../../components/Card';
import { api } from '../../lib/api';
import { useAuth } from '../../lib/auth-context';

export default function LoginPage() {
    const { login } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // NOTE: Using the real backend API
            const response = await api.post('/api/auth/login', {
                email,
                password
            });

            if (response.data.access_token) {
                login(response.data.access_token, response.data.user);
            }
        } catch (err: any) {
            if (err.response?.status === 401) {
                setError('Invalid email or password');
            } else if (err.response?.status === 404) {
                // Just for demo purposes if backend isn't ready
                setError('Backend not connected (404)');
            } else {
                setError('Something went wrong. Is the backend running?');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="min-h-screen bg-black/90 flex flex-col items-center justify-center p-4 relative overflow-hidden">
            {/* Background Ambience */}
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[128px]" />
            <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/10 rounded-full blur-[128px]" />

            <div className="w-full max-w-md relative z-10">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center p-3 rounded-2xl bg-white/5 border border-white/10 mb-4 backdrop-blur-xl">
                        <Sparkles className="w-8 h-8 text-primary" />
                    </div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                        Welcome Back
                    </h1>
                    <p className="text-white/40 mt-2">Sign in to your ScrapeAll account</p>
                </div>

                <Card className="backdrop-blur-xl bg-white/5 border-white/10">
                    <form onSubmit={handleLogin} className="space-y-6">
                        <Input
                            label="Email"
                            type="email"
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />

                        <Input
                            label="Password"
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />

                        {error && (
                            <div className="text-error text-sm bg-error/10 p-3 rounded-lg border border-error/20 flex items-center">
                                <span className="mr-2">⚠️</span>
                                {error}
                            </div>
                        )}

                        <Button
                            type="submit"
                            className="w-full"
                            isLoading={loading}
                            disabled={loading}
                        >
                            Sign In
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                    </form>

                    <div className="mt-6 text-center text-sm text-white/40">
                        Don't have an account?{' '}
                        <Link href="/register" className="text-primary hover:text-white transition-colors">
                            Create one
                        </Link>
                    </div>
                </Card>
            </div>
        </main>
    );
}
