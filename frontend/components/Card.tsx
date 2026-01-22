import { cn } from '@/lib/utils';
import { HTMLAttributes, forwardRef } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
    hover?: boolean;
}

const Card = forwardRef<HTMLDivElement, CardProps>(
    ({ className, children, hover = false, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(
                    'bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 transition-all duration-300',
                    hover && 'hover:bg-white/10 hover:border-white/20 hover:-translate-y-1 hover:shadow-2xl',
                    className
                )}
                {...props}
            >
                {children}
            </div>
        );
    }
);

Card.displayName = 'Card';

export default Card;
