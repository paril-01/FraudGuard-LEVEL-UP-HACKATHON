import { ErrorOutline as ErrorIcon } from '@mui/icons-material';
import Layout from '../components/Layout';

const BlockedTransactions = () => {
  return (
    <Layout title="Blocked Fraudulent Transactions">
      {/* UPI Transactions Section */}
      <div className="card mb-4">
        <h3 className="section-title">Upi</h3>
        
        <div className="blocked-transaction">
          <div className="blocked-transaction-details">
            <div className="blocked-transaction-header">
              <span className="blocked-transaction-id">ID: upi1 | Timestamp: 2024-04-05 10:00:00</span>
            </div>
            <div className="blocked-transaction-amount">₹4,17,500.00</div>
            <div className="blocked-transaction-reason">Reason: Suspicious activity pattern</div>
          </div>
        </div>
        
        <div className="blocked-transaction">
          <div className="blocked-transaction-details">
            <div className="blocked-transaction-header">
              <span className="blocked-transaction-id">ID: upi2 | Timestamp: 2024-04-05 11:30:00</span>
            </div>
            <div className="blocked-transaction-amount">₹10,02,000.00</div>
            <div className="blocked-transaction-reason">Reason: Unusual location</div>
          </div>
        </div>
      </div>

      {/* Credit Card Transactions Section */}
      <div className="card">
        <h3 className="section-title">Credit Card</h3>
        
        <div className="blocked-transaction">
          <div className="blocked-transaction-details">
            <div className="blocked-transaction-header">
              <span className="blocked-transaction-id">ID: cc1 | Timestamp: 2024-04-05 09:15:00</span>
            </div>
            <div className="blocked-transaction-amount">₹20,87,500.00</div>
            <div className="blocked-transaction-reason">Reason: High-risk merchant</div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default BlockedTransactions; 