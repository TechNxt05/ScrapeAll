import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';
import { ButtonHTMLAttributes, forwardRef } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    isLoading?: boolean;
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, children, isLoading, variant = 'primary', ...props }, ref) => {
        const variants = {
            primary: 'bg-gradient-to-r from-primary to-accent text-white hover:shadow-lg hover:shadow-primary/30 border-transparent',
            secondary: 'bg-white/10 text-white hover:bg-white/20 border-white/10',
            outline: 'bg-transparent border-white/20 text-white hover:bg-white/5',
            ghost: 'bg-transparent border-transparent text-white/70 hover:text-white hover:bg-white/5',
        };

        return (
            <button
                ref={ref}
                className={cn(
                    'relative inline-flex items-center justify-center rounded-xl px-6 py-3 font-semibold transition-all duration-300 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed border',
                    variants[variant],
                    className
                )}
                disabled={isLoading || props.disabled}
                {...props}
            >
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {children}
            </button>
        );
    }
);

Button.displayName = 'Button';

export default Button;
