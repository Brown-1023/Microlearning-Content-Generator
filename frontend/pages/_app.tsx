import React from 'react';
import type { AppProps } from 'next/app';
import '../styles/globals.css';
import '../utils/axios-config'; // Configure axios to bypass ngrok warning

function MyApp({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}

export default MyApp;
