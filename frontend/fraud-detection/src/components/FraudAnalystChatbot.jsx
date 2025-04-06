import { useState, useRef, useEffect } from 'react';
import { 
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Search as SearchIcon
} from '@mui/icons-material';

const FraudAnalystChatbot = ({ transaction, onAnalyze }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Hello! I\'m your Fraud Detection Assistant. I can help you understand transaction patterns, explain risk factors, or investigate specific transactions. How can I help you today?',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Sample responses for demo purposes
  const sampleResponses = {
    'explain': () => `This transaction has been flagged due to several risk factors including unusual amount, transaction time outside normal activity hours, and geographic anomaly. The risk score is primarily influenced by the transaction amount being significantly higher than user's typical pattern.`,
    'why': () => `The transaction was flagged because it matches known fraud patterns in our database. Specifically, it includes a combination of unusual timing, abnormal amount, and location inconsistency with the user's profile.`,
    'how': () => `Our fraud detection system uses machine learning algorithms that analyze multiple data points including transaction history, geographic location, device information, and behavioral patterns to identify suspicious activity.`,
    'risk': () => `The primary risk factors for this transaction are: 1) Transaction amount (35% impact), 2) Geographic location (20% impact), 3) Time of transaction (15% impact), 4) Frequency pattern (20% impact), and 5) Account history (10% impact).`,
    'analyze': () => {
      if (transaction) {
        return `Based on my analysis of transaction #${transaction.id}, I've identified potential fraud indicators. The transaction amount of $${transaction.amount} is 3.5x higher than the account's typical spending pattern, and it occurred outside normal hours for this user.`;
      }
      return 'To analyze a specific transaction, please provide a transaction ID or select one from the transactions list.';
    },
    'help': () => `I can help you with the following:
1. Explain why a transaction was flagged
2. Analyze specific transaction patterns
3. Provide risk factor explanations
4. Suggest investigation approaches
5. Compare with similar fraud cases

Try asking something like "Why was this transaction flagged?" or "Analyze this transaction pattern"`,
    'default': () => `I'm not sure I understand fully. Could you rephrase your question about fraud detection or transaction analysis?`
  };
  
  // Scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    // Add user message
    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: input,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);
    
    // Simulate bot thinking
    setTimeout(() => {
      const botResponse = generateResponse(input);
      
      const botMessage = {
        id: messages.length + 2,
        type: 'bot',
        content: botResponse,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
      
      // If the user asked to analyze the transaction, notify parent component
      if (input.toLowerCase().includes('analyze') && transaction && onAnalyze) {
        onAnalyze(transaction);
      }
    }, 1500);
  };
  
  const generateResponse = (query) => {
    query = query.toLowerCase();
    
    // Check for matches with sample response triggers
    if (query.includes('explain') || query.includes('what is')) {
      return sampleResponses.explain();
    } else if (query.includes('why')) {
      return sampleResponses.why();
    } else if (query.includes('how')) {
      return sampleResponses.how();
    } else if (query.includes('risk') || query.includes('factor')) {
      return sampleResponses.risk();
    } else if (query.includes('analyze') || query.includes('check')) {
      return sampleResponses.analyze();
    } else if (query.includes('help')) {
      return sampleResponses.help();
    } else {
      return sampleResponses.default();
    }
  };
  
  return (
    <div className="card">
      <div className="card-header">
        <h3>
          <BotIcon style={{ marginRight: '8px' }} />
          Fraud Analyst Assistant
        </h3>
      </div>
      
      <div className="chatbot-container">
        <div className="chat-messages">
          {messages.map(message => (
            <div 
              key={message.id}
              className={`message ${message.type}-message`}
            >
              {message.type === 'bot' ? (
                <BotIcon className="message-avatar" />
              ) : (
                <PersonIcon className="message-avatar" />
              )}
              <div className="message-content">
                <p>{message.content}</p>
                <span className="message-time">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="message bot-message typing">
              <BotIcon className="message-avatar" />
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        <form onSubmit={handleSubmit} className="chat-input">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about fraud detection or transaction analysis..."
          />
          <button type="submit" className="send-btn" disabled={!input.trim()}>
            <SendIcon />
          </button>
        </form>
      </div>
      
      <div className="chatbot-suggestions">
        <p>Try asking:</p>
        <div className="suggestion-buttons">
          <button 
            className="suggestion-btn"
            onClick={() => {
              setInput('Why was this transaction flagged as suspicious?');
              setTimeout(() => handleSubmit({ preventDefault: () => {} }), 100);
            }}
          >
            <WarningIcon fontSize="small" />
            Why is this transaction suspicious?
          </button>
          
          <button 
            className="suggestion-btn"
            onClick={() => {
              setInput('Analyze this transaction pattern');
              setTimeout(() => handleSubmit({ preventDefault: () => {} }), 100);
            }}
          >
            <SearchIcon fontSize="small" />
            Analyze this transaction
          </button>
          
          <button 
            className="suggestion-btn"
            onClick={() => {
              setInput('What are the main risk factors?');
              setTimeout(() => handleSubmit({ preventDefault: () => {} }), 100);
            }}
          >
            <CheckCircleIcon fontSize="small" />
            What are the risk factors?
          </button>
        </div>
      </div>
    </div>
  );
};

export default FraudAnalystChatbot; 