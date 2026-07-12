import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { CitationLink } from './CitationLink';

interface StreamingTextProps {
  text: string;
  loading: boolean;
  sources?: any[];
}

export function StreamingText({ text, loading, sources = [] }: StreamingTextProps) {
  return (
    <div className="chat-prose">
      <ReactMarkdown 
        remarkPlugins={[remarkGfm, remarkBreaks]}
        components={{
          a: (props) => <CitationLink {...props} sources={sources} />
        }}
      >
        {text}
      </ReactMarkdown>
      {loading && (
        <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse align-middle" />
      )}
    </div>
  );
}
