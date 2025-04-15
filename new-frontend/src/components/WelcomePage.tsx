import React from "react";
import "./WelcomePage.css"; 

const WelcomePage: React.FC = () => {
  return (
    <div className="welcome-page">
      <div className="welcome-container">
        <h1>Welcome to Slash</h1>
        <button className="login-button">Login</button>
      </div>
    </div>
  ); 
};

export default WelcomePage;
