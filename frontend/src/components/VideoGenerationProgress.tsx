import { useState, useEffect } from "react";
import EmbeddedVideo from "./EmbeddedVideo";

interface VideoGenerationProgressProps {
  query: string;
  onComplete: () => void;
  videoId: string;
  videoTitle: string;
}

const GENERATION_STAGES = [
  { name: "Analyzing query", duration: 1000 },
  { name: "Researching physics concepts", duration: 1200 },
  { name: "Extracting key trajectory formulas", duration: 1200 },
  { name: "Generating equation visualizations", duration: 1500 },
  { name: "Creating trajectory animations", duration: 1500 },
  { name: "Finalizing video", duration: 1500 },
];

export default function VideoGenerationProgress({
  query,
  onComplete,
  videoId,
  videoTitle,
}: VideoGenerationProgressProps) {
  const [currentStage, setCurrentStage] = useState(0);
  const [progress, setProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    
    const runStages = () => {
      if (currentStage < GENERATION_STAGES.length) {
        const stage = GENERATION_STAGES[currentStage];
        
        // For each stage, animate the progress
        let startTime = Date.now();
        const duration = stage.duration;
        
        const updateProgress = () => {
          const elapsed = Date.now() - startTime;
          const newProgress = Math.min(elapsed / duration, 1);
          setProgress(newProgress);
          
          if (newProgress < 1) {
            // Continue animation if not complete
            requestAnimationFrame(updateProgress);
          } else {
            // Move to next stage
            timeoutId = setTimeout(() => {
              if (currentStage === GENERATION_STAGES.length - 1) {
                // If this is the last stage, mark as complete
                setIsComplete(true);
                onComplete();
              } else {
                // Otherwise move to next stage
                setCurrentStage(prev => prev + 1);
                setProgress(0);
              }
            }, 300);
          }
        };
        
        requestAnimationFrame(updateProgress);
      } else {
        // All stages complete
        setIsComplete(true);
        onComplete();
      }
    };
    
    if (currentStage < GENERATION_STAGES.length) {
      runStages();
    }
    
    return () => {
      clearTimeout(timeoutId);
    };
  }, [currentStage, onComplete]);

  // Immediately force completion if somehow we're past all stages
  useEffect(() => {
    if (currentStage >= GENERATION_STAGES.length && !isComplete) {
      setIsComplete(true);
      onComplete();
    }
  }, [currentStage, isComplete, onComplete]);

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      {isComplete ? (
        <EmbeddedVideo videoId={videoId} title={videoTitle} />
      ) : (
        <div className="p-5 bg-gray-50 dark:bg-gray-800">
          <div className="mb-4">
            <h3 className="text-lg font-medium mb-1">Generating your video</h3>
            <p className="text-sm text-gray-500">
              Creating a video about "{query}"
            </p>
          </div>
          
          <div className="space-y-4">
            {GENERATION_STAGES.map((stage, index) => {
              const isActive = index === currentStage;
              const isCompleted = index < currentStage;
              
              return (
                <div key={index} className="relative">
                  <div className="flex items-center">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center mr-3 ${
                      isCompleted 
                        ? "bg-green-500 text-white" 
                        : isActive 
                          ? "bg-blue-500 text-white" 
                          : "bg-gray-200 dark:bg-gray-700"
                    }`}>
                      {isCompleted ? (
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                      ) : (
                        <span className="text-xs">{index + 1}</span>
                      )}
                    </div>
                    <div className="flex-grow">
                      <p className={`text-sm font-medium ${
                        isActive ? "text-blue-500" : isCompleted ? "text-gray-500" : "text-gray-400"
                      }`}>
                        {stage.name}
                      </p>
                      {isActive && (
                        <div className="mt-1.5 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 overflow-hidden">
                          <div 
                            className="h-full bg-blue-500 rounded-full transition-all duration-300"
                            style={{ width: `${progress * 100}%` }}
                          ></div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          
          <div className="mt-6 flex items-center justify-between">
            <div className="text-sm text-gray-500">
              {Math.round((currentStage / GENERATION_STAGES.length) * 100)}% complete
            </div>
            <div className="flex items-center">
              <div className="animate-pulse h-2 w-2 bg-blue-500 rounded-full mr-1"></div>
              <div className="animate-pulse h-2 w-2 bg-blue-500 rounded-full animate-delay-100 mr-1"></div>
              <div className="animate-pulse h-2 w-2 bg-blue-500 rounded-full animate-delay-200"></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Add custom CSS for animation delay
const style = document.createElement('style');
style.innerHTML = `
  .animate-delay-100 {
    animation-delay: 100ms;
  }
  .animate-delay-200 {
    animation-delay: 200ms;
  }
`;
document.head.appendChild(style); 