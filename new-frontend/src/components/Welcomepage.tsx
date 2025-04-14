import React from "react";
import "./WelcomePage.css"; // Import the CSS file for styling

const WelcomePage: React.FC = () => {
  return (
    <div className="welcome-container">
      <h1>Welcome to Slash</h1>
      <button className="login-button">Login</button>
    </div>
  );
};

export default WelcomePage;
