'use client';

import { Sparkles, Zap, Brain, Shield, Lock, FileText } from 'lucide-react';
import Card from '@/components/Card';
import Navbar from '@/components/Navbar';

export default function FeaturesPage() {
    const features = [
        {
            icon: Brain,
            title: "AI-Powered Extraction",
            description: "Our multi-model AI engine (Llama 3, Gemini, Mixtral) intelligently understands page structure to extract key data points, summaries, and entities without manual rules."
        },
        {
            icon: Zap,
            title: "Smart Fallback System",
            description: "Never fail a scrape again. We automatically rotate between Static (Requests), Playwright, and Selenium methods to bypass anti-bot protections."
        },
        {
            icon: Shield,
            title: "Enterprise Reliability",
            description: "Built for scale with automatic retries, error recovery, and detailed logs. Perfect for critical data pipelines."
        },
        {
            icon: FileText,
            title: "Form Automation",
            description: "Detect and fill forms automatically using AI agents. Handle login pages, search forms, and contact forms with ease."
        },
        {
            icon: Lock,
            title: "Secure Workspaces",
            description: "Organize scrapes into projects. Your data is isolated and protected. (Authentication required for persistent storage)."
        },
        {
            icon: Sparkles,
            title: "RAG Chat",
            description: "Chat with your scraped data. Ask questions like 'What is the pricing?' and get instant answers sourced from the website content."
        }
    ];

    return (
        <div className="min-h-screen bg-black text-white relative overflow-hidden font-sans">
            <Navbar />

            {/* Background Ambience */}
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[128px]" />
                <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-secondary/10 rounded-full blur-[128px]" />
            </div>

            <main className="relative z-10 pt-32 px-6 max-w-7xl mx-auto pb-20">
                <div className="text-center max-w-3xl mx-auto mb-20">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-sm font-medium text-white/60 mb-6">
                        <Sparkles className="w-4 h-4 text-primary" />
                        <span>Next-Gen Web Scraping</span>
                    </div>
                    <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60 mb-6">
                        Powerful Features for Modern Data Teams
                    </h1>
                    <p className="text-xl text-white/40">
                        Stop writing fragile selectors. Start extracting data with intelligence.
                    </p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {features.map((feature, i) => (
                        <Card key={i} className="bg-white/5 border-white/10 hover:border-primary/50 transition-colors group">
                            <div className="p-2 w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-6 group-hover:bg-primary/20 transition-colors">
                                <feature.icon className="w-6 h-6 text-white/80 group-hover:text-primary transition-colors" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
                            <p className="text-white/50 leading-relaxed">
                                {feature.description}
                            </p>
                        </Card>
                    ))}
                </div>
            </main>
        </div>
    );
}
