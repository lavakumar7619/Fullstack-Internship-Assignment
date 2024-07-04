import React, { useState, useRef, useEffect } from 'react'
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { FaRegFilePdf, FaRobot } from "react-icons/fa6";
import { LuSendHorizonal } from "react-icons/lu";
import { IoPersonCircle } from "react-icons/io5";
import axios from 'axios'
function Services() {
    const fileInputRef = useRef(null);
    const [uploadedFile, setuploadedFile] = useState()
    const [inputValue, setInputValue] = useState('');
    const [Question, setQuestion] = useState(null)
    const [UploadStatus, setUploadStatus] = useState()
    const [socket, setSocket] = useState(null);
    const [messages, setMessages] = useState([]);

     useEffect(() => {
        console.log(messages);
    //     const ws = new WebSocket('ws://localhost:8000/ws');
    //     setSocket(ws);

    //     ws.onmessage = (event) => {
    //         const message = event.data;
    //         setMessages(prevMessages => [...prevMessages, message]);
    //         //setMessages(message)

    //     };
    //     return () => {
    //         ws.close();
    //     };
    }, []);


    const handleFileChange = async (event) => {
        const selectedFile = event.target.files[0]
        if (!selectedFile || selectedFile == undefined) {
            toast.error('No file selected.');
            return;
        }

        const fileType = selectedFile.type;
        if (fileType !== 'application/pdf') {
            toast.error('Only PDF files are allowed.');
            return;
        }
        const formData = new FormData();
        formData.append('pdfFile', selectedFile);
        try {
            const response = await axios.post('http://localhost:8000/upload/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            if (response.status === 200) {
                setuploadedFile(selectedFile);
                toast.success(`File uploaded successfully: ${response.data.message}`)
            }
        } catch (error) {
            console.log(error);
            setuploadedFile(null)
            setInputValue('')
            setMessages([])
            setQuestion(null)
            toast.error(`Failed to Upload ${selectedFile} Try again...`)
        }
    };

    const handleButtonClick = () => {
        fileInputRef.current.click();
        setuploadedFile(null)
    };
    const handleChange = (e) => {
        setInputValue(e.target.value);
    };
    const handelQuestion = async (e) => {
        e.preventDefault();

        if (!inputValue.trim()) {
            toast.warning("Please Enter the Question...!")
            return
        }
        setQuestion(inputValue)
        // if (!socket || socket.readyState !== WebSocket.OPEN) return;
        // socket.send(inputValue);

        try {
            const answer = await axios.post("http://localhost:8000/query/",
                { "question": Question }
            )


            console.log(answer.data);
            const message = answer.data
            setMessages(prevMessages => [...prevMessages, message]);


        } catch (error) {
            console.log(error);
            toast.error("Unable to get data")
        }

        console.log(messages);
        setInputValue('')
        console.log('Input value:', inputValue);
    }
    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handelQuestion(e);
            setInputValue('')
        }
    };
    return (
        <section>
            <section className="header">
                <div className="logo">
                    <span>Planet</span>
                    <small>formerly EPN</small>
                </div>
                <div className="actions">
                    {uploadedFile && <a className="file-link"><FaRegFilePdf /> {uploadedFile?.name}</a>}
                    <div>
                        <input
                            type="file"
                            ref={fileInputRef}
                            style={{ display: 'none' }}
                            onChange={handleFileChange}
                        />
                        <button onClick={handleButtonClick} className="upload-button">Upload PDF</button>
                    </div>
                </div>
            </section>
            <section className='chat-box'>
                <section className="chat-messages">

                    {messages.map((message, index) => (
                        <div key={index}>
                            <div className="chat-message">
                                <span><IoPersonCircle size={45} color='blue' /></span>
                                <p>{message.question}</p>
                            </div>
                            <div key={index} className="chat-message">
                                <span><FaRobot size={45} color="red" /></span>
                                <p>{message.answer}</p>
                            </div>
                        </div>
                    ))}
                </section>
                <section className="chat-input">
                    <input type="text"
                        id="chat-input-field"
                        placeholder="Ask Question here..."
                        value={inputValue}
                        onChange={handleChange}
                        onKeyPress={handleKeyPress} />
                    {uploadedFile && <LuSendHorizonal id="send-btn" onClick={handelQuestion} size={30} />}
                </section>
            </section>
            <ToastContainer
                position="bottom-center"
                autoClose={2500}
                hideProgressBar={false}
                newestOnTop={false}
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
                theme="light"
            />
        </section>
    )
}

export default Services