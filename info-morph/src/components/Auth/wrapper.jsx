const AuthWrapper = ({ children }) => {
  return (
    <div className="flex-1 flex items-center justify-center">
      <div className="flex flex-col items-center">{children}</div>
    </div>
  );
};

export default AuthWrapper;
