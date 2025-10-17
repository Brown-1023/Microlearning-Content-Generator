import axios from 'axios';

// Check if we're using ngrok by looking at the API URL
const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
const isNgrok = apiUrl.includes('ngrok') || apiUrl.includes('ngrok-free.app');

// Only add ngrok header if we're actually using ngrok
if (isNgrok) {
  // Configure axios defaults to bypass ngrok warning
  axios.defaults.headers.common['ngrok-skip-browser-warning'] = 'true';

  // Also set it for specific methods to ensure it's always included
  axios.defaults.headers.get['ngrok-skip-browser-warning'] = 'true';
  axios.defaults.headers.post['ngrok-skip-browser-warning'] = 'true';
  axios.defaults.headers.put['ngrok-skip-browser-warning'] = 'true';
  axios.defaults.headers.delete['ngrok-skip-browser-warning'] = 'true';
  axios.defaults.headers.patch['ngrok-skip-browser-warning'] = 'true';
}

export default axios;
export { isNgrok };
