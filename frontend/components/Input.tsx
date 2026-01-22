import { cn } from '../lib/utils';
import { InputHTMLAttributes, forwardRef } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
    ({ className, label, error, ...props }, ref) => {
        return (
            <div className="w-full">
                {label && (
                    <label className="mb-2 block text-sm font-medium text-white/70">
                        {label}
                    </label>
                )}
                <input
                    ref={ref}
                    className={cn(
                        'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:border-primary/50 focus:bg-white/10 transition-all duration-300 disabled:opacity-50',
                        error && 'border-error/50 focus:border-error',
                        className
                    )}
                    {...props}
                />
                {error && <p className="mt-1 text-sm text-error">{error}</p>}
            </div>
        );
    }
);

Input.displayName = 'Input';

export default Input;
