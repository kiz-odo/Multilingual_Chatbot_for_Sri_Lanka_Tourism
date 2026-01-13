/**
 * useIntersectionObserver - Lazy loading and infinite scroll
 */

import { useEffect, useRef, useState, RefObject } from 'react';

interface IntersectionObserverOptions {
    threshold?: number | number[];
    root?: Element | null;
    rootMargin?: string;
    freezeOnceVisible?: boolean;
}

export function useIntersectionObserver<T extends Element>(
    options: IntersectionObserverOptions = {}
): [RefObject<T>, boolean, IntersectionObserverEntry | undefined] {
    const {
        threshold = 0,
        root = null,
        rootMargin = '0px',
        freezeOnceVisible = false,
    } = options;

    const elementRef = useRef<T>(null);
    const [entry, setEntry] = useState<IntersectionObserverEntry>();
    const [isIntersecting, setIsIntersecting] = useState(false);

    const frozen = freezeOnceVisible && isIntersecting;

    useEffect(() => {
        const element = elementRef.current;
        const hasIOSupport = !!window.IntersectionObserver;

        if (!hasIOSupport || frozen || !element) {
            return;
        }

        const observerCallback: IntersectionObserverCallback = ([entry]) => {
            setEntry(entry);
            setIsIntersecting(entry.isIntersecting);
        };

        const observerOptions: IntersectionObserverInit = {
            threshold,
            root,
            rootMargin,
        };

        const observer = new IntersectionObserver(observerCallback, observerOptions);
        observer.observe(element);

        return () => {
            observer.disconnect();
        };
    }, [threshold, root, rootMargin, frozen]);

    return [elementRef, isIntersecting, entry];
}

/**
 * useLazyLoad - Simple lazy loading hook
 */
export function useLazyLoad<T extends Element>(): [RefObject<T>, boolean] {
    const [ref, isVisible] = useIntersectionObserver<T>({
        threshold: 0.1,
        freezeOnceVisible: true,
    });

    return [ref, isVisible];
}

/**
 * useInfiniteScroll - Infinite scroll hook
 */
export function useInfiniteScroll<T extends Element>(
    callback: () => void,
    options: { threshold?: number; rootMargin?: string } = {}
): RefObject<T> {
    const [ref, isIntersecting] = useIntersectionObserver<T>({
        threshold: options.threshold || 0.1,
        rootMargin: options.rootMargin || '100px',
    });

    useEffect(() => {
        if (isIntersecting) {
            callback();
        }
    }, [isIntersecting, callback]);

    return ref;
}
