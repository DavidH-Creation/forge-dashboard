import { useState } from 'react';

interface ArtifactViewerProps {
  name: string;
  content: string;
  format?: string;
}

export function ArtifactViewer({
  name,
  content,
  format = 'json',
}: ArtifactViewerProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="artifact-viewer">
      <div className="artifact-viewer__header">
        <span className="artifact-viewer__name">{name}</span>
        <span className="artifact-viewer__format">{format}</span>
        <button
          className="artifact-viewer__copy"
          onClick={handleCopy}
          type="button"
        >
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <pre className="artifact-viewer__code">
        <code>{content}</code>
      </pre>
    </div>
  );
}
