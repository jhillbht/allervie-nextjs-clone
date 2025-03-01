
import { Mic } from "lucide-react";
import { useState } from "react";
import { toast } from "@/hooks/use-toast";

interface MicButtonProps {
  onVoiceSearch: (transcript: string) => void;
}

const MicButton = ({ onVoiceSearch }: MicButtonProps) => {
  const [isListening, setIsListening] = useState(false);

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast({
        title: "Speech Recognition Not Available",
        description: "Your browser doesn't support speech recognition.",
        variant: "destructive",
      });
      return;
    }

    setIsListening(true);
    
    // Use the appropriate Speech Recognition API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onVoiceSearch(transcript);
      toast({
        title: "You said:",
        description: transcript,
      });
    };
    
    recognition.onerror = (event) => {
      console.error('Speech recognition error', event.error);
      toast({
        title: "Error",
        description: `Speech recognition error: ${event.error}`,
        variant: "destructive",
      });
      setIsListening(false);
    };
    
    recognition.onend = () => {
      setIsListening(false);
    };
    
    recognition.start();
  };

  return (
    <div className="flex justify-center w-full my-8">
      <button
        onClick={startListening}
        className={`p-4 rounded-full shadow-lg transition-all duration-300 ${
          isListening 
            ? "bg-red-500 animate-pulse-soft"
            : "bg-gradient-sxsw hover:shadow-xl"
        }`}
        disabled={isListening}
        aria-label="Voice Search"
      >
        <Mic className="h-6 w-6 text-white" />
      </button>
    </div>
  );
};

export default MicButton;
