'use client';

import { ArrowRight, Globe, Database, Bot, ChevronRight } from 'lucide-react';
import Card from '@/components/Card';
import Navbar from '@/components/Navbar';

export default function HowItWorksPage() {
    const steps = [
        {
            step: "01",
            icon: Globe,
            title: "Enter Target URL",
            description: "Simply paste the URL of the website you want to scrape. Whether it's a static blog or a dynamic React app, we handle it."
        },
        {
            step: "02",
            icon: Bot,
            title: "AI Analysis",
            description: "Our Smart Scraper first attempts a fast static scrape. If that fails (due to JS auth or anti-bot), it upgrades to a Headless Browser with AI-powered unblocking."
        },
        {
            step: "03",
            icon: Database,
            title: "Content Extraction",
            description: "Once the HTML is retrieved, our LLM engine parses the messy DOM to extract clean, structured data: summaries, entities, and key points."
        },
        {
            step: "04",
            icon: ArrowRight,
            title: "Chat & Export",
            description: "Interact with the data immediately via our RAG Chat, or export it to your projects history for later analysis."
        }
    ];

    return (
        <div className="min-h-screen bg-black text-white relative overflow-hidden font-sans">
            <Navbar />

            <main className="relative z-10 pt-32 px-6 max-w-7xl mx-auto pb-20">
                <div className="text-center max-w-3xl mx-auto mb-20">
                    <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60 mb-6">
                        How ScrapeAll Works
                    </h1>
                    <p className="text-xl text-white/40">
                        From URL to structured data in seconds. No coding required.
                    </p>
                </div>

                <div className="relative">
                    {/* Connector Line (Desktop) */}
                    <div className="hidden lg:block absolute top-1/2 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-y-1/2" />

                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {steps.map((step, i) => (
                            <Card key={i} className="relative bg-black/40 border-white/10 backdrop-blur-md">
                                <span className="absolute -top-4 -right-4 text-6xl font-bold text-white/5 select-none">
                                    {step.step}
                                </span>
                                <div className="relative z-10">
                                    <div className="w-12 h-12 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center mb-6">
                                        <step.icon className="w-6 h-6 text-primary" />
                                    </div>
                                    <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                                        {step.title}
                                        {i < steps.length - 1 && (
                                            <ChevronRight className="w-4 h-4 text-white/20 lg:hidden" />
                                        )}
                                    </h3>
                                    <p className="text-white/50 text-sm leading-relaxed">
                                        {step.description}
                                    </p>
                                </div>
                            </Card>
                        ))}
                    </div>
                </div>
            </main>
        </div>
    );
}
