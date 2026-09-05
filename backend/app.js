import express from 'express';
import cors from 'cors';
import authRoutes from './routes/authRoutes.js';
import classRoutes from './routes/classRoutes.js'; 
import doubtRoutes from './routes/doubtRoutes.js';
import lectureRoutes from './routes/lectureRoutes.js';
import userRoutes from './routes/userRoutes.js'


const app = express();

// Allows frontend to communicate with backend
app.use(cors({
    origin: '*', 
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));
// Parses incoming JSON payloads
app.use(express.json()); 

// This is useful to check if backend is alive and for Python to verify connection
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'OK', message: 'SignMitra Core Backend is running' });
});

// We will import and use our routes here in the next steps (Auth, Classes, etc.)
// Mount Auth Routes
app.use('/api/auth', authRoutes); 
app.use('/api/classes', classRoutes); // Mount Class Routes for verification and creation
app.use('/api/doubts', doubtRoutes); // Mount Doubt Routes for asking and answering doubts
app.use('/api/lectures', lectureRoutes); // Mount Lecture Routes for uploading and managing lectures
app.use('/api/users', userRoutes); //

export default app;