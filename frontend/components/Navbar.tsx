'use client';

// Add useAuth import
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { Sparkles, Github, Twitter, LayoutDashboard, LogOut } from 'lucide-react';
import Button from './Button';

export default function Navbar() {
    const { isAuthenticated, logout } = useAuth();

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-black/20 backdrop-blur-xl">
            <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                <Link href="/" className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-gradient-to-br from-primary to-accent">
                        <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <span className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70">
                        ScrapeAll
                    </span>
                </Link>

                <div className="hidden md:flex items-center gap-8 text-sm font-medium text-white/60">
                    <Link href="/features" className="hover:text-white transition-colors">Features</Link>
                    <Link href="/how-it-works" className="hover:text-white transition-colors">How it Works</Link>
                    <Link href="https://github.com" target="_blank" className="hover:text-white transition-colors">
                        <Github className="w-5 h-5" />
                    </Link>
                </div>

                <div className="flex items-center gap-4">
                    {isAuthenticated ? (
                        <>
                            <Link href="/dashboard">
                                <Button variant="secondary" className="h-9 px-4 text-sm rounded-lg flex items-center gap-2">
                                    <LayoutDashboard className="w-4 h-4" />
                                    Dashboard
                                </Button>
                            </Link>
                            <button
                                onClick={logout}
                                className="text-sm font-medium text-white/60 hover:text-error transition-colors flex items-center gap-2"
                            >
                                <LogOut className="w-4 h-4" />
                                Sign Out
                            </button>
                        </>
                    ) : (
                        <>
                            <Link href="/login" className="hidden md:block text-sm font-medium text-white/60 hover:text-white transition-colors">
                                Sign In
                            </Link>
                            <Link href="/register">
                                <Button variant="primary" className="h-9 px-4 text-sm rounded-lg">
                                    Get Started
                                </Button>
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
}
