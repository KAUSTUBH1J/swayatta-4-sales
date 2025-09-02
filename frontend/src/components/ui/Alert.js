import React from 'react';

const Alert = React.forwardRef(({ className = '', variant = 'default', ...props }, ref) => {
  const variants = {
    default: 'bg-white border-gray-200',
    destructive: 'border-red-200 bg-red-50 text-red-900',
    success: 'border-green-200 bg-green-50 text-green-900',
    warning: 'border-yellow-200 bg-yellow-50 text-yellow-900',
  };

  return (
    <div
      ref={ref}
      role="alert"
      className={`relative w-full rounded-lg border p-4 ${variants[variant]} ${className}`}
      {...props}
    />
  );
});
Alert.displayName = 'Alert';

const AlertDescription = React.forwardRef(({ className = '', ...props }, ref) => (
  <div
    ref={ref}
    className={`text-sm [&_p]:leading-relaxed ${className}`}
    {...props}
  />
));
AlertDescription.displayName = 'AlertDescription';

export { Alert, AlertDescription };