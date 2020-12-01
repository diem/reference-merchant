import React from "react";

interface InfoFieldProps {
  caption: string;
  value: string;
}

function InfoField({ caption, value }: InfoFieldProps) {
  return (
    <div className="mt-4">
      {caption}
      <div className="text-black">{value}</div>
    </div>
  );
}

export default InfoField;
