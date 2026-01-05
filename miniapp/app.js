// Example plain-JS demo integrating TON Connect and emitting analytics events.
// This is a minimal demo — adapt to the official TON Connect SDK and analytics library.

const log = (msg) => { document.getElementById('log').textContent += msg + '\n'; }
const status = (s) => { document.getElementById('status').textContent = s; }

// Placeholders — replace with official SDK usage per docs
let tonConnect = null;
let connectedAccount = null;

async function init() {
  status('Ready');
  log('Mini App loaded.');
  // Initialize analytics (placeholder)
  log('Analytics: initialized (placeholder)');
  // Track miniapp_open
  log('Analytics event: miniapp_open');
}

async function connectWallet() {
  status('Connecting...');
  log('Requesting TON Connect connection (placeholder)');

  // PSEUDOCODE: integrate official TON Connect SDK here
  // See https://docs.ton.org/v3/guidelines/ton-connect/overview for SDK usage

  try {
    // Simulate a successful connection for demo
    connectedAccount = { address: 'EQC_DEMO_ADDRESS', name: 'DemoWallet' };
    status('Connected: ' + connectedAccount.address);
    document.getElementById('sendTx').disabled = false;
    log('Connected address: ' + connectedAccount.address);
    log('Analytics event: wallet_connect – ' + connectedAccount.name);
  } catch (err) {
    status('Connection failed');
    log('Error connecting: ' + err);
    log('Analytics event: error – connect');
  }
}

async function sendDemoTx() {
  if (!connectedAccount) return;
  status('Sending demo tx...');
  log('Preparing demo transaction (placeholder)');

  try {
    // PSEUDOCODE: request user to sign and send tx using TON Connect
    const fakeTxHash = '0xDEMO_TX_HASH';
    log('Transaction submitted, txHash: ' + fakeTxHash);
    status('Tx sent: ' + fakeTxHash);
    log('Analytics event: tx_sent – ' + fakeTxHash);
  } catch (err) {
    status('Tx failed');
    log('Error sending tx: ' + err);
    log('Analytics event: error – tx');
  }
}

document.getElementById('connect').addEventListener('click', connectWallet);
document.getElementById('sendTx').addEventListener('click', sendDemoTx);
window.addEventListener('load', init);
