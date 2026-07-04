import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface StreamingTextProps {
  text: string;
  loading: boolean;
}

export function StreamingText({ text, loading }: StreamingTextProps) {
  return (
    <div className="prose prose-invert max-w-none text-sm">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {text}
      </ReactMarkdown>
      {loading && (
        <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse align-middle" />
      )}
    </div>
  );
}
