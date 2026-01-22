'use client';

import { useState } from 'react';
import Link from 'next/link';
import { UserPlus, ArrowRight } from 'lucide-react';
import Button from '@/components/Button';
import Input from '@/components/Input';
import Card from '@/components/Card';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';

export default function RegisterPage() {
    const { login } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        setLoading(true);

        try {
            // 1. Register
            const registerRes = await api.post('/api/auth/register', {
                email,
                password
            });

            if (registerRes.data) {
                // 2. Auto Login after register
                const loginRes = await api.post('/api/auth/login', {
                    email,
                    password
                });

                if (loginRes.data.access_token) {
                    login(loginRes.data.access_token, loginRes.data.user);
                }
            }
        } catch (err: any) {
            if (err.response?.status === 400) {
                setError(err.response.data.detail || 'Email already registered');
            } else {
                setError('Registration failed. Please try again.');
                console.error(err);
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
                        <UserPlus className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                        Create Account
                    </h1>
                    <p className="text-white/40 mt-2">Join ScrapeAll to manage your projects</p>
                </div>

                <Card className="backdrop-blur-xl bg-white/5 border-white/10">
                    <form onSubmit={handleRegister} className="space-y-6">
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
                            minLength={6}
                        />

                        <Input
                            label="Confirm Password"
                            type="password"
                            placeholder="••••••••"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
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
                            Sign Up
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                    </form>

                    <div className="mt-6 text-center text-sm text-white/40">
                        Already have an account?{' '}
                        <Link href="/login" className="text-primary hover:text-white transition-colors">
                            Sign In
                        </Link>
                    </div>
                </Card>
            </div>
        </main>
    );
}
