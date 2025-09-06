import React from 'react';

interface FormattedLLMTextProps {
  text: string;
}

const FormattedLLMText: React.FC<FormattedLLMTextProps> = ({ text }) => {
  // Split text into lines for processing
  const lines = text.split('\n');
  
  const renderLine = (line: string, index: number) => {
    const trimmedLine = line.trim();
    
    // Empty lines
    if (!trimmedLine) {
      return <div key={index} className="h-2"></div>;
    }
    
    // Main headers (### **Header**)
    if (trimmedLine.startsWith('### **') && trimmedLine.endsWith('**')) {
      const headerText = trimmedLine.replace(/^### \*\*/, '').replace(/\*\*$/, '');
      return (
        <h3 key={index} className="text-lg font-bold text-gray-900 mt-6 mb-3 border-b border-gray-200 pb-2">
          {headerText}
        </h3>
      );
    }
    
    // Sub-headers (**Header:**)
    if (trimmedLine.startsWith('**') && trimmedLine.includes(':**')) {
      const headerText = trimmedLine.replace(/^\*\*/, '').replace(/:\*\*.*$/, '');
      const content = trimmedLine.replace(/^\*\*[^:]+:\*\*\s*/, '');
      return (
        <div key={index} className="mt-4 mb-2">
          <h4 className="font-semibold text-gray-800 mb-1">{headerText}:</h4>
          {content && <p className="text-gray-700">{content}</p>}
        </div>
      );
    }
    
    // Bullet points
    if (trimmedLine.startsWith('• ') || trimmedLine.startsWith('- ')) {
      const bulletText = trimmedLine.replace(/^[•-]\s*/, '');
      return (
        <li key={index} className="text-gray-700 mb-1 ml-4">
          {formatInlineText(bulletText)}
        </li>
      );
    }
    
    // Numbered lists
    if (/^\d+\.\s/.test(trimmedLine)) {
      const listText = trimmedLine.replace(/^\d+\.\s*/, '');
      return (
        <li key={index} className="text-gray-700 mb-2 ml-4 list-decimal">
          {formatInlineText(listText)}
        </li>
      );
    }
    
    // Product listings or bold items
    if (trimmedLine.startsWith('**') && trimmedLine.includes('**')) {
      return (
        <div key={index} className="mb-2">
          {formatInlineText(trimmedLine)}
        </div>
      );
    }
    
    // Regular paragraphs
    return (
      <p key={index} className="text-gray-700 mb-2 leading-relaxed">
        {formatInlineText(trimmedLine)}
      </p>
    );
  };
  
  // Helper function to format inline text (bold, etc.)
  const formatInlineText = (text: string) => {
    // Split by bold markers
    const parts = text.split(/(\*\*[^*]+\*\*)/);
    
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        const boldText = part.replace(/^\*\*/, '').replace(/\*\*$/, '');
        return (
          <strong key={index} className="font-semibold text-gray-900">
            {boldText}
          </strong>
        );
      }
      return part;
    });
  };
  
  return (
    <div className="prose prose-sm max-w-none">
      {lines.map((line, index) => renderLine(line, index))}
    </div>
  );
};

export default FormattedLLMText;
