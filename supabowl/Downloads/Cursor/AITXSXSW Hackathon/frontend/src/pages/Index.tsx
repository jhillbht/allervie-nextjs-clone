
import { useState, useEffect } from "react";
import Header from "@/components/Header";
import EventGrid from "@/components/EventGrid";
import FilterBar from "@/components/FilterBar";
import MicButton from "@/components/MicButton";
import { Event, EventTag } from "@/models/event";
import { mockEvents } from "@/data/mockEvents";
import { useToast } from "@/hooks/use-toast";

const Index = () => {
  const [events, setEvents] = useState<Event[]>(mockEvents);
  const [filteredEvents, setFilteredEvents] = useState<Event[]>(mockEvents);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [activeFilters, setActiveFilters] = useState<EventTag[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const { toast } = useToast();

  useEffect(() => {
    let result = [...events];
    
    if (activeFilters.length > 0) {
      result = result.filter(event => 
        activeFilters.some(filter => event.tags.includes(filter))
      );
    }
    
    if (searchQuery.trim() !== "") {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        event =>
          event.name.toLowerCase().includes(query) ||
          event.description.toLowerCase().includes(query) ||
          event.location.toLowerCase().includes(query)
      );
    }
    
    setFilteredEvents(result);
  }, [events, activeFilters, searchQuery]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    
    if (query.trim() !== "") {
      toast({
        title: "Searching for events",
        description: `Showing results for "${query}"`,
      });
    } else {
      setFilteredEvents(events);
    }
  };

  const handleVoiceSearch = (transcript: string) => {
    setSearchQuery(transcript);
    handleSearch(transcript);
  };

  const handleFilterByTag = (tag: EventTag) => {
    setActiveFilters(prev => {
      if (prev.includes(tag)) {
        return prev.filter(t => t !== tag);
      }
      return [...prev, tag];
    });
  };

  const handleSelectEvent = (eventId: string) => {
    setSelectedEventId(prev => prev === eventId ? null : eventId);
    
    const selectedEvent = events.find(event => event.id === eventId);
    if (selectedEvent) {
      toast({
        title: "Event Selected",
        description: `You selected "${selectedEvent.name}"`,
      });
      
      // Auto-apply tags from the selected event as filters
      if (selectedEvent.tags.length > 0 && selectedEventId !== eventId) {
        setActiveFilters(selectedEvent.tags);
      }
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header onSearch={handleSearch} />
      
      <main className="container mx-auto px-6 py-10">
        <div className="bg-card/80 backdrop-blur-sm max-w-6xl mx-auto p-8 rounded-2xl shadow-lg border border-border">
          <h2 className="text-2xl font-semibold mb-6 text-foreground">SXSW Event Vibe Check</h2>
          
          <FilterBar 
            onFilterByTag={handleFilterByTag} 
            activeFilters={activeFilters} 
          />
          
          <EventGrid 
            events={filteredEvents}
            selectedEventId={selectedEventId}
            onSelectEvent={handleSelectEvent}
          />
          
          <MicButton onVoiceSearch={handleVoiceSearch} />
        </div>
      </main>
    </div>
  );
};

export default Index;
