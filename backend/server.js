import http from 'http';
import dotenv from 'dotenv';
import { Server } from 'socket.io';
import app from './app.js';
import connectDB from './config/database.js';
import dns from 'dns';

dns.setServers(['8.8.8.8', '1.1.1.1']); // Forces Node to bypass local ISP blocks
dotenv.config();
connectDB();



// Create standard HTTP server wrapping Express app
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

io.on('connection', (socket) => {
    console.log(`🟢 WebRTC/Socket Client Connected: ${socket.id}`);

    socket.on('join-room', (roomId, role, userName) => {
        // Room join se PEHLE dekho kaun already andar hai
        const roomSet = io.sockets.adapter.rooms.get(roomId);
        const existingSocketIds = roomSet ? Array.from(roomSet) : [];

        socket.join(roomId);

        // Apni info socket pe store karo taaki disconnect pe pata chale kis room mein tha
        socket.data.role = role;
        socket.data.userName = userName;
        socket.data.roomId = roomId;

        console.log(`👤 User [${userName}] (${role}) joined Room: ${roomId}`);

        // Send existing users' info to the newly joined user
        const existingUsers = existingSocketIds.map(id => {
            const s = io.sockets.sockets.get(id);
            return { socketId: id, role: s?.data?.role, name: s?.data?.userName };
        });
        socket.emit('existing-users', existingUsers);

        // Purana behavior: existing members ko naye joiner ke baare mein batao
        socket.to(roomId).emit('user-connected', socket.id, role, userName);
    });
    socket.on('offer', (offer, roomId) => {
        socket.to(roomId).emit('offer', offer, socket.id);
    });

    socket.on('answer', (answer, roomId) => {
        socket.to(roomId).emit('answer', answer);
    });

    socket.on('ice-candidate', (candidate, roomId) => {
        socket.to(roomId).emit('ice-candidate', candidate);
    });
    //  FORWARDING ISL TEXT & AUDIO FROM STUDENT TO TEACHER
    socket.on('send-caption', (text, roomId, audioData) => {
        // Teacher ho ya Student, text aur audio dono safe tarike se forward honge
        socket.to(roomId).emit('receive-caption', text, audioData);
    });
    //  TEACHER VOICE/CAPTION → STUDENT
    socket.on('send-teacher-caption', (text, roomId) => {
        console.log(`🎤 Teacher Caption → Room ${roomId}: ${text}`);

        socket.to(roomId).emit('receive-teacher-caption', {
            text: text
        });
    });
    //  FORWARDING ONLY AUDIO FROM STUDENT TO TEACHER
    socket.on('send-audio-only', (roomId, audioData) => {
        socket.to(roomId).emit('receive-audio-only', audioData);
    });
    socket.on('disconnect', () => {
        console.log(`🔴 Socket Client Disconnected: ${socket.id}`);
        // Notify other users in the room
        if (socket.data.roomId) {
            socket.to(socket.data.roomId).emit('user-disconnected', socket.id);
        }
    });
});

const PORT = process.env.PORT || 1307;

server.listen(PORT, '0.0.0.0', () => {
    console.log(`✅ SignMitra Backend Server with Socket.io is running on port ${PORT}`);
    console.log(`🔍 Health Check: http://localhost:${PORT}/health`);
});