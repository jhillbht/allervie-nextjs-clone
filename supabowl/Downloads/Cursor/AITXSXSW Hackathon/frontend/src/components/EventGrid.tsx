
import { useEffect, useRef } from "react";
import { Event } from "../models/event";
import EventCard from "./EventCard";

interface EventGridProps {
  events: Event[];
  selectedEventId: string | null;
  onSelectEvent: (eventId: string) => void;
}

const EventGrid = ({ events, selectedEventId, onSelectEvent }: EventGridProps) => {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (events.length === 0 || !scrollContainerRef.current || selectedEventId) return;
    
    let animationId: number;
    let scrollPosition = 0;
    const scrollSpeed = 0.5; // pixels per frame (adjust for faster/slower scrolling)
    const containerWidth = scrollContainerRef.current.scrollWidth;
    const viewportWidth = scrollContainerRef.current.clientWidth;
    
    const scroll = () => {
      if (!scrollContainerRef.current) return;
      
      // Increment scroll position
      scrollPosition += scrollSpeed;
      
      // Reset scroll position when we've scrolled through all content
      if (scrollPosition >= containerWidth - viewportWidth) {
        scrollPosition = 0;
      }
      
      scrollContainerRef.current.scrollLeft = scrollPosition;
      animationId = requestAnimationFrame(scroll);
    };
    
    // Start the animation
    animationId = requestAnimationFrame(scroll);
    
    // Pause scrolling when user interacts with the container
    const pauseScroll = () => cancelAnimationFrame(animationId);
    const resumeScroll = () => {
      // Only resume if no event is selected
      if (!selectedEventId) {
        scrollPosition = scrollContainerRef.current?.scrollLeft || 0;
        animationId = requestAnimationFrame(scroll);
      }
    };
    
    const container = scrollContainerRef.current;
    container.addEventListener('mouseenter', pauseScroll);
    container.addEventListener('mouseleave', resumeScroll);
    container.addEventListener('touchstart', pauseScroll);
    container.addEventListener('touchend', resumeScroll);
    
    // Clean up on component unmount
    return () => {
      cancelAnimationFrame(animationId);
      container.removeEventListener('mouseenter', pauseScroll);
      container.removeEventListener('mouseleave', resumeScroll);
      container.removeEventListener('touchstart', pauseScroll);
      container.removeEventListener('touchend', resumeScroll);
    };
  }, [events.length, selectedEventId]);

  if (events.length === 0) {
    return (
      <div className="text-center py-10">
        <p className="text-gray-500">No events found. Try adjusting your filters.</p>
      </div>
    );
  }

  const selectedEvent = selectedEventId ? events.find(event => event.id === selectedEventId) : null;
  const relatedEvents = selectedEvent 
    ? events.filter(event => 
        event.id !== selectedEventId && 
        event.tags.some(tag => selectedEvent.tags.includes(tag))
      )
    : [];

  return (
    <div className="w-full overflow-hidden mb-8">
      <div 
        ref={scrollContainerRef}
        className="overflow-x-auto pb-4 scrollbar-hide"
      >
        <div className="flex space-x-6 px-2">
          {events.map((event, index) => (
            <div
              key={event.id}
              className="flex-shrink-0 w-[300px]"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <EventCard
                event={event}
                selected={event.id === selectedEventId}
                onClick={() => onSelectEvent(event.id)}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Related events section */}
      {selectedEvent && relatedEvents.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-white mb-4">Related Events with Similar Tags</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {relatedEvents.map((event) => (
              <div key={event.id}>
                <EventCard
                  event={event}
                  selected={false}
                  onClick={() => onSelectEvent(event.id)}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default EventGrid;
