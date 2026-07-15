import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { CitationLink } from './CitationLink';

interface StreamingTextProps {
  text: string;
  loading: boolean;
  sources?: any[];
}

const normalizeCitations = (text: string) => {
  if (!text) return text;
  let normalized = text.replace(/\[Source\s*(\d+)[^\]]*\]/gi, '[$1](#source-$1)');
  normalized = normalized.replace(/Source\s*(\d+)\s*\([^\)]+\)/gi, '[$1](#source-$1)');
  return normalized;
};

export function StreamingText({ text, loading, sources = [] }: StreamingTextProps) {
  return (
    <>
      <ReactMarkdown 
        remarkPlugins={[remarkGfm, remarkBreaks]}
        components={{
          a: (props) => <CitationLink {...props} sources={sources} />
        }}
      >
        {normalizeCitations(text)}
      </ReactMarkdown>
      {loading && (
        <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse align-middle" />
      )}
    </>
  );
}
