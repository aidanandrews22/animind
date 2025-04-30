import { useState, useEffect, useRef } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  oneDark,
  oneLight,
} from "react-syntax-highlighter/dist/cjs/styles/prism";
import "katex/dist/katex.min.css"; // Import KaTeX CSS
import { useSupabase } from "../hooks/useSupabase";
import { 
  getChatMessagesBySessionId, 
  addChatMessage, 
  createChatSession,
  getChatSessionById
} from "../services/chatService";
import AnimationGenerationProgress from "./VideoGenerationProgress";
import EmbeddedVideo from "./EmbeddedVideo";

// Import CheckIcon and ClipboardIcon as SVG components to avoid lucide-react dependency
const CheckIcon = ({ size = 24, className = "" }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
);

const ClipboardIcon = ({ size = 24, className = "" }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
    <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
  </svg>
);

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

interface ChatInterfaceProps {
  courseId: string;
  sessionId?: string | null;
}

// Define a custom interface for code component props
interface CodeComponentProps {
  node: React.ReactNode;
  inline?: boolean;
  className?: string;
  children: React.ReactNode;
}

// Custom hook for dark mode detection
function useDarkMode() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Check initial color scheme
    const checkColorScheme = () => {
      const isDark =
        document.documentElement.classList.contains("force-dark") ||
        (document.documentElement.classList.contains("color-scheme-adaptive") &&
          window.matchMedia("(prefers-color-scheme: dark)").matches);
      setIsDarkMode(isDark);
    };

    // Check on mount
    checkColorScheme();

    // Set up listeners for theme changes
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = () => checkColorScheme();
    mediaQuery.addEventListener("change", handleChange);

    // Observer for class changes on html element
    const observer = new MutationObserver(checkColorScheme);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });

    return () => {
      mediaQuery.removeEventListener("change", handleChange);
      observer.disconnect();
    };
  }, []);

  return isDarkMode;
}

// Code block component with copy button and syntax highlighting
const CodeBlock = ({
  children,
  className,
  onCopy,
  isCopied,
}: {
  children?: React.ReactNode;
  className?: string;
  onCopy: (text: string) => void;
  isCopied: boolean;
}) => {
  const language = className ? className.replace(/language-/, "") : "";
  const codeContent = typeof children === "string" ? children : "";
  const isDarkMode = useDarkMode();

  return (
    <div className="relative group rounded-lg overflow-hidden">
      <SyntaxHighlighter
        style={isDarkMode ? oneDark : oneLight}
        language={language || "text"}
        PreTag="div"
        className="!rounded-lg !m-0"
        customStyle={{
          borderRadius: "0.5rem",
          margin: 0,
        }}
      >
        {codeContent}
      </SyntaxHighlighter>
      <button
        onClick={() => onCopy(codeContent)}
        className="absolute top-2 right-2 bg-[color-mix(in_oklch,var(--color-primary,#6c47ff)_20%,transparent)] px-2 py-1 rounded text-sm hover:opacity-80 transition-opacity opacity-0 group-hover:opacity-100"
        aria-label="Copy code"
      >
        {isCopied ? "Copied!" : "Copy"}
      </button>
    </div>
  );
};

export default function ChatInterface({ courseId, sessionId }: ChatInterfaceProps) {
  const { userId } = useSupabase();
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(sessionId || null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [copiedText, setCopiedText] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messageContainerRef = useRef<HTMLDivElement>(null);
  const [showScrollBottom, setShowScrollBottom] = useState(false);
  const [endSpacerHeight, setEndSpacerHeight] = useState(64);
  const [lastMessageCount, setLastMessageCount] = useState(0);
  
  // Video generation state
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [videoGenerationQuery, setVideoGenerationQuery] = useState("");
  const [videoGenerationComplete, setVideoGenerationComplete] = useState(false);
  const [videoGenerationStatus, setVideoGenerationStatus] = useState("");
  const [videoId, setVideoId] = useState<string | null>(null);
  const [isVideoModeEnabled, setIsVideoModeEnabled] = useState(false);

  // Animation generation suggestion prompts
  const videoSuggestions = [
    "Create an animation showing a circle rolling on a flat surface without slipping",
    "Generate an animation of a pendulum with varying length over time",
    "Visualize projectile motion with air resistance",
    "Create an animation explaining the concept of partial derivatives with a 3D surface",
    "Animate the solution to the wave equation in 2D",
    "Show how to find trajectories in physics using integrals"
  ];

  // Load messages when sessionId changes
  useEffect(() => {
    const loadMessages = async () => {
      if (!sessionId) {
        // Clear messages if no session is selected
        setMessages([]);
        setCurrentSessionId(null);
        return;
      }
      
      setIsLoading(true);
      
      try {
        // Load messages for the selected session
        const chatMessages = await getChatMessagesBySessionId(sessionId);
        
        // Convert DB messages to UI messages
        const formattedMessages = chatMessages.map(msg => ({
          id: msg.id,
          role: msg.role as "user" | "assistant",
          content: msg.content,
          timestamp: new Date(msg.timestamp).getTime()
        }));
        
        setMessages(formattedMessages);
        setLastMessageCount(formattedMessages.length);
        setCurrentSessionId(sessionId);
      } catch (error) {
        console.error("Error loading chat messages:", error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadMessages();
  }, [sessionId]);

  useEffect(() => {
    // Set up resize observer to recalculate heights when window resizes
    const resizeObserver = new ResizeObserver(() => {
      calculateSpacerHeight();
    });

    // Add scroll event listener
    const handleScroll = () => {
      if (messageContainerRef.current) {
        const { scrollTop, scrollHeight, clientHeight } =
          messageContainerRef.current;
        const isAtBottom = scrollHeight - scrollTop - clientHeight < 100;
        setShowScrollBottom(!isAtBottom);
      }
      calculateSpacerHeight();
    };

    // Fix React hooks exhaustive-deps warning
    const currentMessageContainer = messageContainerRef.current;

    if (currentMessageContainer) {
      resizeObserver.observe(currentMessageContainer);
      currentMessageContainer.addEventListener("scroll", handleScroll, {
        passive: true,
      });
    }

    // Initial scroll position
    scrollToBottom("auto");
    calculateSpacerHeight();

    return () => {
      resizeObserver.disconnect();
      currentMessageContainer?.removeEventListener("scroll", handleScroll);
    };
  }, []);

  useEffect(() => {
    if (isLoading && streamingContent) {
      scrollToBottom();
    }
  }, [streamingContent, isLoading]);

  const scrollToBottom = (behavior: ScrollBehavior = "smooth") => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior });
    }
  };

  // Calculate the appropriate spacing based on content
  const calculateSpacerHeight = () => {
    if (!messageContainerRef.current || !messagesEndRef.current) return;

    const containerHeight = messageContainerRef.current.clientHeight;
    const messagesEndHeight = messagesEndRef.current.clientHeight || 0;
    const scrollHeight = messageContainerRef.current.scrollHeight;
    const contentHeight = scrollHeight - messagesEndHeight;
    const chatInputHeight = 64;
    const bufferSpace = 32;

    // For small screens, keep it minimal
    const isMobileDevice = window.innerWidth < 768;

    // Calculate optimal height
    let newHeight;
    if (contentHeight > containerHeight) {
      // Content overflows, use minimal spacing
      newHeight = chatInputHeight + bufferSpace;
    } else {
      // Content fits, use larger spacing on desktop, smaller on mobile
      newHeight = isMobileDevice ? 64 : 120;
    }

    setEndSpacerHeight(newHeight);
  };

  const autoResizeTextarea = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
    }
  };

  // Function to handle animation generation
  const generateVideo = async (prompt: string, sessionId: string) => {
    if (!userId) return;
    
    try {
      setStreamingContent("Starting animation generation process...");
      
      // Generate a unique id for the animation path
      const uniqueId = crypto.randomUUID();
      const bucketPath = `animations/${userId}/${uniqueId}`;
      
      // Request body for animation generation according to API spec
      const requestBody = {
        prompt: prompt,
        output_dir: `output/${uniqueId}`,
        file_name: uniqueId,
        user_id: userId, // Must be a valid UUID
        bucket_path: bucketPath,
        title: "Manim Animation: " + (prompt.length > 30 ? prompt.substring(0, 30) + "..." : prompt),
        description: prompt,
        course_id: courseId // Optional UUID
      };
      
      // Start the animation generation
      const response = await fetch("http://localhost:2222/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      // Set up event source for progress updates (separate from the POST request)
      const eventSource = new EventSource("http://localhost:2222/stream-updates");
      
      eventSource.onmessage = (event) => {
        const data = event.data;
        
        // Parse the message according to the API spec
        if (data.startsWith('status:')) {
          const statusMessage = data.substring('status:'.length).trim();
          setVideoGenerationStatus(statusMessage);
          setStreamingContent(prev => `${prev}\n\n${statusMessage}`);
        } else if (data.startsWith('log:')) {
          const logMessage = data.substring('log:'.length).trim();
          console.log("Animation generation log:", logMessage);
        } else if (data.startsWith('error:')) {
          const errorMessage = data.substring('error:'.length).trim();
          console.error("Animation generation error:", errorMessage);
          setStreamingContent(prev => `${prev}\n\nError: ${errorMessage}`);
        } else if (data.startsWith('result:')) {
          try {
            const resultData = JSON.parse(data.substring('result:'.length).trim());
            console.log("Animation generation complete:", resultData);
            
            if (resultData.video_id) {
              setVideoId(resultData.video_id);
              
              // Add the assistant message with video embed
              const assistantMessage: ChatMessage = {
                id: Date.now().toString(),
                role: "assistant",
                content: `I've created an animation based on your request:\n\n<video-embed id="${resultData.video_id}" title="${requestBody.title}" />`,
                timestamp: Date.now(),
              };
              
              setMessages((prev) => [...prev, assistantMessage]);
              
              // Store the assistant message in Supabase
              if (sessionId) {
                addChatMessage({
                  session_id: sessionId,
                  role: 'assistant',
                  content: assistantMessage.content,
                });
              }
              
              setVideoGenerationComplete(true);
              setIsLoading(false);
              setStreamingContent("");
            }
          } catch (e) {
            console.error("Error parsing result data:", e);
          }
        } else if (data.includes('complete') || data.status === 'complete') {
          console.log("EventSource reports completion, closing connection");
          eventSource.close();
        }
      };
      
      eventSource.onerror = (error) => {
        console.error("EventSource error:", error);
        eventSource.close();
        
        if (!videoId) {
          setStreamingContent(prev => `${prev}\n\nError receiving updates from the server.`);
        }
      };
      
      // Set video generation state
      setVideoGenerationQuery(prompt);
      setIsGeneratingVideo(true);
      setVideoGenerationComplete(false);
      
      return true;
    } catch (error) {
      console.error("Error starting animation generation:", error);
      setStreamingContent(prev => `${prev}\n\nError: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !userId) return;

    // Validate current session if one exists
    if (currentSessionId) {
      const isSessionValid = await validateSession(currentSessionId);
      if (!isSessionValid) {
        // Reset session if it's not valid
        setCurrentSessionId(null);
      }
    }

    // Create user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setStreamingContent("");

    // Check if animation generation is requested
    const shouldGenerateAnimation = isVideoModeEnabled;

    try {
      // Create a new chat session if this is the first message
      if (!currentSessionId) {
        // Create a descriptive title from the first message
        const sessionTitle = createSessionTitle(input);
        
        const newSession = await createChatSession({
          user_id: userId,
          course_id: courseId,
          title: sessionTitle,
        });
        
        if (!newSession) {
          throw new Error("Failed to create chat session");
        }
        
        setCurrentSessionId(newSession.id);
        
        // Store the user message in Supabase
        await addChatMessage({
          session_id: newSession.id,
          role: 'user',
          content: input,
        });
        
        if (shouldGenerateAnimation) {
          // Generate video with the new session ID
          await generateVideo(input, newSession.id);
          return;
        }
      } else {
        // Store the user message in Supabase
        await addChatMessage({
          session_id: currentSessionId,
          role: 'user',
          content: input,
        });
        
        if (shouldGenerateAnimation) {
          // Generate video with existing session ID
          await generateVideo(input, currentSessionId);
          return;
        }
      }

      // Regular flow for other inputs
      // Call API endpoint
      const response = await fetch("http://localhost:8001/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      // Set up reader for streaming response
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("Failed to get response reader");
      }

      // Setup text decoder
      const decoder = new TextDecoder();
      let accumulatedContent = "";

      // Stream the response without adding a temporary message
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        accumulatedContent += chunk;
        setStreamingContent(accumulatedContent);
      }

      // Make sure to do a final decode to catch any remaining bytes
      const finalChunk = decoder.decode();
      if (finalChunk) {
        accumulatedContent += finalChunk;
        setStreamingContent(accumulatedContent);
      }

      // Add the final assistant message only after streaming is complete
      const assistantMessage: ChatMessage = {
        id: Date.now().toString(),
        role: "assistant",
        content: accumulatedContent,
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      
      // Store the assistant message in Supabase
      const savedMessage = await addChatMessage({
        session_id: currentSessionId as string,
        role: 'assistant',
        content: accumulatedContent,
      });
      
      // If saving fails, log the error but don't break the UI
      if (!savedMessage) {
        console.error("Failed to save assistant message to database");
      }
      
      setIsLoading(false);
      setStreamingContent("");
    } catch (error) {
      console.error("Error sending message:", error);
      setIsLoading(false);

      // Add error message
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        role: "assistant",
        content:
          "Sorry, there was an error processing your request. Please try again.",
        timestamp: Date.now(),
      };
      
      setMessages((prev) => [...prev, errorMessage]);
      
      // Store the error message in Supabase
      if (currentSessionId) {
        await addChatMessage({
          session_id: currentSessionId,
          role: 'assistant',
          content: errorMessage.content,
        });
      }
      
      setStreamingContent("");
    }
  };

  // Handle video generation completion
  const handleVideoGenerationComplete = async () => {
    console.log("Video generation complete, displaying video");
    setVideoGenerationComplete(true);
    setIsLoading(false);
    // Keep isGeneratingVideo true so the component stays visible
  };

  // Validate that a session still exists in the database
  const validateSession = async (sessionId: string): Promise<boolean> => {
    try {
      const session = await getChatSessionById(sessionId);
      return !!session;
    } catch (error) {
      console.error("Error validating session:", error);
      return false;
    }
  };

  // Create a descriptive title from the first message
  const createSessionTitle = (message: string) => {
    // Truncate long messages and add ellipsis
    if (message.length > 50) {
      return message.substring(0, 47) + "...";
    }
    // For very short messages, add "Chat about" prefix
    if (message.length < 20) {
      return "Chat about " + message;
    }
    return message;
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
    autoResizeTextarea();
  };

  const handleCopyCode = (text: string) => {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        setCopiedText(text);
        setTimeout(() => setCopiedText(null), 2000);
      })
      .catch((err) => console.error("Failed to copy text: ", err));
  };

  // Format timestamp for display
  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Common Markdown rendering component to ensure consistency
  const renderMarkdown = (content: string) => {
    // Check for video embed tags
    if (content.includes("<video-embed")) {
      // This is a very simple regex parser - a more robust solution would use proper HTML parsing
      const videoEmbedRegex = /<video-embed\s+id="([^"]+)"\s+title="([^"]+)"\s*\/>/g;
      const parts = [];
      let lastIndex = 0;
      let match;
      
      while ((match = videoEmbedRegex.exec(content)) !== null) {
        // Add text before the video embed
        if (match.index > lastIndex) {
          parts.push(
            <Markdown
              key={`text-${lastIndex}`}
              remarkPlugins={[remarkGfm, remarkMath]}
              rehypePlugins={[rehypeRaw, rehypeKatex]}
              components={{
                code: (props) => {
                  const { inline, className, children, ...rest } =
                    props as CodeComponentProps;
                  const match = /language-(\w+)/.exec(className || "");

                  if (!inline && match) {
                    return (
                      <CodeBlock
                        className={className}
                        onCopy={handleCopyCode}
                        isCopied={
                          copiedText === (typeof children === "string" ? children : "")
                        }
                      >
                        {typeof children === "string"
                          ? children.replace(/\n$/, "")
                          : children}
                      </CodeBlock>
                    );
                  }

                  return (
                    <code
                      className={`${inline ? "bg-[color-mix(in_oklch,var(--color-primary,#6c47ff)_10%,transparent)] px-1.5 py-0.5 rounded" : ""} ${className || ""}`}
                      {...rest}
                    >
                      {children}
                    </code>
                  );
                },
                pre: ({ node, children, ...rest }) => (
                  <pre
                    {...rest}
                    className="bg-background !p-0 !m-0 overflow-hidden w-full max-w-full"
                  >
                    {children}
                  </pre>
                ),
                table: ({ children, ...props }) => (
                  <div className="overflow-x-auto w-full">
                    <table {...props} className="w-full table-auto">
                      {children}
                    </table>
                  </div>
                ),
              }}
            >
              {content.substring(lastIndex, match.index)}
            </Markdown>
          );
        }
        
        // Add the video embed component
        parts.push(
          <div key={`video-${match[1]}`} className="my-4">
            {isGeneratingVideo && videoGenerationComplete ? (
              <EmbeddedVideo videoId={match[1]} title={match[2]} />
            ) : isGeneratingVideo ? (
              <AnimationGenerationProgress
                query={videoGenerationQuery}
                videoId={match[1]}
                videoTitle={match[2]}
                onComplete={handleVideoGenerationComplete}
              />
            ) : (
              <div className="rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                <div className="aspect-video flex items-center justify-center bg-gray-100 dark:bg-gray-900">
                  <div className="text-center p-4">
                    <svg
                      width="48"
                      height="48"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      className="mx-auto text-gray-400 mb-3"
                    >
                      <path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14v-4z"></path>
                      <rect x="3" y="6" width="12" height="12" rx="2" ry="2"></rect>
                    </svg>
                    <p className="font-medium">{match[2]}</p>
                    <p className="text-sm text-gray-500 mt-1">Video from Supabase</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        );
        
        lastIndex = match.index + match[0].length;
      }
      
      // Add any remaining text after the last video embed
      if (lastIndex < content.length) {
        parts.push(
          <Markdown
            key={`text-${lastIndex}`}
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[rehypeRaw, rehypeKatex]}
            components={{
              code: (props) => {
                const { inline, className, children, ...rest } =
                  props as CodeComponentProps;
                const match = /language-(\w+)/.exec(className || "");

                if (!inline && match) {
                  return (
                    <CodeBlock
                      className={className}
                      onCopy={handleCopyCode}
                      isCopied={
                        copiedText === (typeof children === "string" ? children : "")
                      }
                    >
                      {typeof children === "string"
                        ? children.replace(/\n$/, "")
                        : children}
                    </CodeBlock>
                  );
                }

                return (
                  <code
                    className={`${inline ? "bg-[color-mix(in_oklch,var(--color-primary,#6c47ff)_10%,transparent)] px-1.5 py-0.5 rounded" : ""} ${className || ""}`}
                    {...rest}
                  >
                    {children}
                  </code>
                );
              },
              pre: ({ node, children, ...rest }) => (
                <pre
                  {...rest}
                  className="bg-background !p-0 !m-0 overflow-hidden w-full max-w-full"
                >
                  {children}
                </pre>
              ),
              table: ({ children, ...props }) => (
                <div className="overflow-x-auto w-full">
                  <table {...props} className="w-full table-auto">
                    {children}
                  </table>
                </div>
              ),
            }}
          >
            {content.substring(lastIndex)}
          </Markdown>
        );
      }
      
      return <>{parts}</>;
    }
    
    // Regular markdown rendering for content without video embeds
    return (
      <Markdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeRaw, rehypeKatex]}
        components={{
          code: (props) => {
            const { inline, className, children, ...rest } =
              props as CodeComponentProps;
            const match = /language-(\w+)/.exec(className || "");

            if (!inline && match) {
              return (
                <CodeBlock
                  className={className}
                  onCopy={handleCopyCode}
                  isCopied={
                    copiedText === (typeof children === "string" ? children : "")
                  }
                >
                  {typeof children === "string"
                    ? children.replace(/\n$/, "")
                    : children}
                </CodeBlock>
              );
            }

            return (
              <code
                className={`${inline ? "bg-[color-mix(in_oklch,var(--color-primary,#6c47ff)_10%,transparent)] px-1.5 py-0.5 rounded" : ""} ${className || ""}`}
                {...rest}
              >
                {children}
              </code>
            );
          },
          pre: ({ node, children, ...rest }) => (
            <pre
              {...rest}
              className="bg-background !p-0 !m-0 overflow-hidden w-full max-w-full"
            >
              {children}
            </pre>
          ),
          table: ({ children, ...props }) => (
            <div className="overflow-x-auto w-full">
              <table {...props} className="w-full table-auto">
                {children}
              </table>
            </div>
          ),
        }}
      >
        {content}
      </Markdown>
    );
  };

  // Animation for streamed content
  const pulseAnimation = `
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .animate-fadeIn {
      animation: fadeIn 0.3s ease-out forwards;
    }
    
    /* Custom prose overrides to fix overflow issues */
    .prose pre {
      overflow-x: auto;
      max-width: 100%;
    }
    
    .prose .overflow-hidden {
      max-width: 100%;
    }
    
    .prose code {
      word-break: break-word;
    }
    
    .prose blockquote {
      overflow-wrap: break-word;
    }
    
    .prose table {
      display: block;
      overflow-x: auto;
    }
  `;

  // If lastMessageCount is truly not used, we can use it in the scroll effect
  useEffect(() => {
    if (messages.length > lastMessageCount) {
      scrollToBottom();
      setLastMessageCount(messages.length);
      calculateSpacerHeight();
    }
  }, [messages.length, lastMessageCount]);

  return (
    <div className="flex flex-col h-screen">
      {/* Style tag for animations */}
      <style>{pulseAnimation}</style>

      {/* Message container */}
      <div
        ref={messageContainerRef}
        className="flex-1 overflow-y-auto pt-4 px-4 relative scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600 scrollbar-track-transparent max-w-3xl mx-auto w-full"
      >
        <div className="w-full flex flex-col items-center justify-center">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center w-full max-w-lg">
              <div className="mb-6">
                <svg
                  width="64"
                  height="64"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  className="text-gray-300"
                >
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-medium text-gray-700 mb-2">
                Start your conversation
              </h3>
              <p className="text-gray-500 max-w-md mb-6">
                Ask any question about your course content, request
                explanations, or generate mathematical animations
              </p>

              {/* Animation suggestions */}
              <div className="max-w-lg w-full">
                <div className="text-sm font-medium text-gray-500 mb-3">
                  Try generating an animation:
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {videoSuggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      className="text-left text-sm bg-white border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors"
                      onClick={() => handleSuggestionClick(suggestion)}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`mb-8 animate-fadeIn ${message.role === "user" ? "text-right" : "text-left"}`}
                >
                  {message.role === "user" ? (
                    <div className="inline-block bg-gray-100 dark:bg-gray-800 p-4 rounded-lg text-left max-w-[90%] break-words">
                      <p>{message.content}</p>
                      <div className="text-xs text-gray-400 text-right mt-1">
                        {formatTime(message.timestamp)}
                      </div>
                    </div>
                  ) : (
                    <div className="prose prose-gray dark:prose-invert w-full max-w-full break-words">
                      {renderMarkdown(message.content)}

                      <div className="flex items-center gap-2 mt-2">
                        <button
                          onClick={() => handleCopyCode(message.content)}
                          className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-sm flex items-center"
                        >
                          {copiedText === message.content ? (
                            <>
                              <CheckIcon size={16} className="mr-1" />
                              Copied
                            </>
                          ) : (
                            <>
                              <ClipboardIcon size={16} className="mr-1" />
                              Copy
                            </>
                          )}
                        </button>
                      </div>

                      <div className="text-xs text-gray-400 mt-1">
                        {formatTime(message.timestamp)}
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {/* Streaming message - only shown during loading and not duplicated */}
              {isLoading && streamingContent && (
                <div className="mb-8 text-left animate-fadeIn">
                  <div className="prose prose-gray dark:prose-invert w-full max-w-full break-words">
                    {renderMarkdown(streamingContent)}
                  </div>
                </div>
              )}

              {/* Loading indicator - only show when no streaming content yet */}
              {isLoading && !streamingContent && (
                <div className="flex justify-start mb-8">
                  <div className="inline-block p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 rounded-full bg-gray-400 animate-pulse"></div>
                      <div className="w-2 h-2 rounded-full bg-gray-400 animate-pulse delay-150"></div>
                      <div className="w-2 h-2 rounded-full bg-gray-400 animate-pulse delay-300"></div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}

          {/* Add additional space at the end to prevent input from covering messages */}
          <div
            ref={messagesEndRef}
            style={{ height: `${endSpacerHeight}px` }}
            className="transition-height duration-300"
          ></div>
        </div>

        {/* Scroll to bottom button */}
        {showScrollBottom && (
          <button
            onClick={() => scrollToBottom()}
            className="fixed bottom-24 right-4 md:right-8 z-10 p-3 bg-gray-800 dark:bg-gray-200 text-white dark:text-black rounded-full shadow-md hover:bg-gray-700 dark:hover:bg-gray-300 transition-all duration-200 flex items-center justify-center"
            aria-label="Scroll to bottom"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
        )}
      </div>

      {/* Chat input area */}
      <form
        onSubmit={handleSubmit}
        className="bottom-4 w-full pb-4 max-w-3xl mx-auto left-0 right-0"
      >
        <div className="backdrop-blur-md rounded-2xl overflow-hidden shadow-xl border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isVideoModeEnabled ? "Describe the animation you want to generate..." : "Type your message..."}
              className="flex-1 p-4 bg-transparent outline-none resize-none min-h-[56px] max-h-[25vh] overflow-y-auto"
              disabled={isLoading}
              rows={1}
              onInput={autoResizeTextarea}
              onFocus={autoResizeTextarea}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  if (input.trim() && !isLoading) {
                    handleSubmit(e);
                  }
                }
              }}
            />
          </div>
          <div className="flex items-center px-4 py-2 justify-between">
            {/* Video generation toggle */}
            <button
              type="button"
              onClick={() => setIsVideoModeEnabled(prev => !prev)}
              className={`flex items-center text-sm transition-colors ${
                isVideoModeEnabled 
                ? "text-blue-500 hover:text-blue-600" 
                : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              }`}
              aria-label={isVideoModeEnabled ? "Disable animation generation" : "Enable animation generation"}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="mr-1"
              >
                <path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14v-4z"></path>
                <rect x="3" y="6" width="12" height="12" rx="2" ry="2"></rect>
              </svg>
              {isVideoModeEnabled ? "Animation Mode" : "Animation"}
              {isVideoModeEnabled && (
                <span className="inline-block ml-1.5 w-2 h-2 bg-blue-500 rounded-full"></span>
              )}
            </button>
            
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="p-2 bg-black text-white dark:bg-white dark:text-black rounded-full disabled:opacity-50 hover:bg-gray-800 dark:hover:bg-gray-200 transition-colors shadow-sm cursor-pointer"
            >
              {isLoading ? (
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-t-transparent border-white dark:border-black"></div>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
