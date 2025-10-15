import React from 'react';

interface ToastProps {
  message: string;
  type: string;
}

const Toast: React.FC<ToastProps> = ({ message, type }) => {
  return (
    <div className={`toast toast-${type}`}>
      <span>{message}</span>
    </div>
  );
};

export default Toast;
