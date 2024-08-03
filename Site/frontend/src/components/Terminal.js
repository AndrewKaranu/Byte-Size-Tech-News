import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './Styles/Terminal.css';
import './Styles/Window.css'

const Terminal = ({ onClose }) => {
    const [input, setInput] = useState('');
    const [output, setOutput] = useState([]);
    const [email, setEmail] = useState('');
    const [awaitingEmail, setAwaitingEmail] = useState(false);
    const [awaitingLanguage, setAwaitingLanguage] = useState(false);

    useEffect(() => {
        const openingMessage = [
            "Welcome to Byte Sized Tech News Terminal!",
            "",
            "  ____        _       ____  _              _   ",
            " |  _ \\      | |     / ___|| |_ _   _  ___| |_ ",
            " | |_) |_   _| |_ ___\\___ \\| __| | | |/ _ \\ __|",
            " |  _ <| | | | __/ _ \\___) | |_| |_| |  __/ |_ ",
            " |_| \\_\\ |_|_|\\__\\___/____/ \\__|\\__, |\\___|\\__|",
            "                                |___/         ",
            "",
            "Type 'help' for a list of available commands.",
            ""
        ];
        setOutput(openingMessage);

        // Add a small delay to ensure the server is ready
        setTimeout(() => {
            axios.get('http://localhost:5000/health')
                .then(() => console.log('Server is ready'))
                .catch(error => console.error('Server not ready:', error));
        }, 1000);
    }, []);

    const handleInputChange = (e) => {
        setInput(e.target.value);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            processCommand(input);
            setInput('');
        }
    };

    const processCommand = useCallback(async (input) => {
        let newOutput = [...output, `user@bytesized~$ ${input}`];

        if (awaitingEmail) {
            setEmail(input);
            setAwaitingEmail(false);
            setAwaitingLanguage(true);
            newOutput.push("Great! Now, please enter your preferred language (e.g., 'en' for English, 'es' for Spanish):");
        } else if (awaitingLanguage) {
            setAwaitingLanguage(false);
            try {
                const response = await axios.post('http://localhost:5000/signup', { email, language: input });
                newOutput.push(response.data.message);
            } catch (error) {
                console.error('Signup error:', error);
                newOutput.push('An error occurred during signup. Please try again.');
                if (error.response) {
                    newOutput.push(`Error: ${error.response.data.error || 'Unknown error'}`);
                }
            }
        } else {
            const commandParts = input.split(' ');
            const command = commandParts[0].toLowerCase();

            switch (command) {
                case 'help':
                    newOutput.push(
                        "Available commands:",
                        "  signup - Start the newsletter signup process",
                        "  info   - Display information about Byte Sized Tech News",
                        "  clear  - Clear the terminal screen",
                        "  date   - Display the current date and time",
                        "  echo   - Repeat the given text",
                        "  fortune - Display a random fortune",
                        "  whoami - Display current user information"
                    );
                    break;
                case 'signup':
                    setAwaitingEmail(true);
                    newOutput.push("Please enter your email address:");
                    break;
                case 'info':
                    newOutput.push('Byte Sized Tech News: Stay updated with the latest tech news. Sign up to receive weekly updates.');
                    break;
                case 'clear':
                    setOutput([]);
                    return;
                case 'date':
                    newOutput.push(new Date().toString());
                    break;
                case 'echo':
                    newOutput.push(commandParts.slice(1).join(' '));
                    break;
                case 'fortune':
                    const fortunes = [
                        "You will encounter a curious SQL query in your future.",
                        "A debugger is in your future. Use it wisely.",
                        "You will soon find the semicolon you've been missing.",
                        "Your code will compile without errors... eventually.",
                        "A breakthrough in your project is just around the corner."
                    ];
                    newOutput.push(fortunes[Math.floor(Math.random() * fortunes.length)]);
                    break;
                case 'whoami':
                    newOutput.push("You are a curious tech enthusiast exploring the Byte Sized world!");
                    break;
                default:
                    newOutput.push(`Unknown command: ${command}`);
            }
        }

        setOutput(newOutput);
    }, [output, email, awaitingEmail, awaitingLanguage]);

    return (
        <div className="window terminal-window">
            <div className="title-bar">
                <div className="title-bar-text">Terminal</div>
                <div className="title-bar-controls">
                    <button aria-label="Close" onClick={onClose}></button>
                </div>
            </div>
            <div className="window-body">
                <div className="terminal">
                    <div className="output">
                        {output.map((line, index) => (
                            <div key={index}>{line}</div>
                        ))}
                    </div>
                    <div className="input-line">
                        <span className="prompt">user@bytesize~$</span>
                        <input
                            type="text"
                            value={input}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            autoFocus
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Terminal;