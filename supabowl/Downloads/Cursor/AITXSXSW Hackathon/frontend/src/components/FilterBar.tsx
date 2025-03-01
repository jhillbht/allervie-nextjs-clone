
import { EventTag } from "../models/event";
import EventTagComponent from "./EventTag";

interface FilterBarProps {
  onFilterByTag: (tag: EventTag) => void;
  activeFilters: EventTag[];
}

const FilterBar = ({ onFilterByTag, activeFilters }: FilterBarProps) => {
  const availableTags: EventTag[] = ["energetic", "informative"];

  return (
    <div className="flex flex-col sm:flex-row sm:items-center space-y-3 sm:space-y-0 sm:space-x-2 mb-6">
      <span className="text-sm text-gray-500">Filter by:</span>
      <div className="flex flex-wrap gap-3">
        {availableTags.map((tag) => (
          <EventTagComponent
            key={tag}
            tag={tag}
            onClick={() => onFilterByTag(tag)}
            selected={activeFilters.includes(tag)}
          />
        ))}
      </div>
    </div>
  );
};

export default FilterBar;
