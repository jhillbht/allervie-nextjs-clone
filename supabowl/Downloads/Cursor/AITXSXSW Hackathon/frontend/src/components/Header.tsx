
import { Search } from "lucide-react";
import { useState } from "react";
import EventSonarLogo from "./EventSonarLogo";

interface HeaderProps {
  onSearch: (query: string) => void;
}

const Header = ({ onSearch }: HeaderProps) => {
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(searchQuery);
  };

  return (
    <header className="w-full py-6 px-6 md:px-10 animate-fade-in">
      <div className="container mx-auto">
        <div className="flex flex-col items-center justify-center mb-6">
          <EventSonarLogo size={70} />
          <h1 className="text-4xl md:text-5xl font-bold text-center mt-3 mb-2 bg-clip-text text-transparent bg-gradient-sxsw">
            Event Sonar
          </h1>
          <p className="text-lg text-center text-gray-400 mb-8">
            Discover your perfect SXSW experience
          </p>
        </div>
        
        <form onSubmit={handleSearch} className="max-w-xl mx-auto relative">
          <div className="relative">
            <input
              type="text"
              placeholder="Search events..."
              className="w-full py-3 pl-12 pr-4 rounded-xl border border-white/10 focus:outline-none focus:ring-2 focus:ring-sxsw-purple/50 transition-all duration-300 shadow-sm bg-white/10 text-white"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
          </div>
        </form>
      </div>
    </header>
  );
};

export default Header;
