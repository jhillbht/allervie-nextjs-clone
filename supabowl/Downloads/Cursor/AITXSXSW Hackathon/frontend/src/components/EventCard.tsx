
import { Event } from "../models/event";
import EventTag from "./EventTag";
import { Calendar, MapPin } from "lucide-react";
import { cn } from "@/lib/utils";

interface EventCardProps {
  event: Event;
  selected: boolean;
  onClick: () => void;
}

const EventCard = ({ event, selected, onClick }: EventCardProps) => {
  return (
    <div
      className={cn(
        "event-card bg-card/80 backdrop-blur-sm p-5 cursor-pointer animate-slide-up border border-white/10",
        selected && "event-card-selected"
      )}
      onClick={onClick}
    >
      <div className="mb-3">
        <h3 className="text-lg font-semibold text-white mb-1">{event.name}</h3>
        <p className="text-sm text-gray-300 line-clamp-2">{event.description}</p>
      </div>
      
      <div className="flex items-center text-xs text-gray-400 mb-3 space-x-4">
        <div className="flex items-center">
          <Calendar size={14} className="mr-1" />
          <span>{new Date(event.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
        </div>
        <div className="flex items-center">
          <MapPin size={14} className="mr-1" />
          <span className="truncate">{event.location}</span>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-2">
        {event.tags.map((tag) => (
          <EventTag key={tag} tag={tag} />
        ))}
      </div>
    </div>
  );
};

export default EventCard;
