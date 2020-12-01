import React from "react";

interface LinkFieldProps {
  caption: string;
  url?: string;
  text?: string;
  external?: boolean;
}

function LinkField({ caption, url, text, external = false }: LinkFieldProps) {
  return (
    <div className="mt-4">
      {caption}
      <div className="text-black">
        {text == null ? (
          "N/A"
        ) : (
          <span className="text-monospace text-info">
            <a href={url} target="_blank" rel="noopener noreferrer">
              {text} {external && <i className="fa fa-external-link" />}
            </a>
          </span>
        )}
      </div>
    </div>
  );
}

export default LinkField;
