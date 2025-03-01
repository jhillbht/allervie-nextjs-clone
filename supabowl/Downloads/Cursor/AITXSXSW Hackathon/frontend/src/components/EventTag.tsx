
import { EventTag as TagType } from "../models/event";
import { cn } from "@/lib/utils";

interface EventTagProps {
  tag: TagType;
  onClick?: () => void;
  selected?: boolean;
}

const EventTag = ({ tag, onClick, selected }: EventTagProps) => {
  const baseClasses = "tag transition-all duration-300 text-lg font-semibold py-2.5 px-5 shadow-sm";
  const tagClasses = {
    energetic: "tag-energetic",
    informative: "tag-informative",
  };
  
  const displayText = {
    energetic: "Energetic",
    informative: "Informative",
  };

  return (
    <span 
      className={cn(
        baseClasses, 
        tagClasses[tag],
        onClick && "cursor-pointer hover:opacity-90",
        selected && "ring-2 ring-offset-2 ring-offset-white ring-gray-400"
      )}
      onClick={onClick}
    >
      {displayText[tag]}
    </span>
  );
};

export default EventTag;
