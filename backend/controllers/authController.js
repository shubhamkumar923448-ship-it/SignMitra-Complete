import User from '../models/User.js';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';


// User Registration Logic
export const register = async (req, res) => {
    try {
        const { name, username, password, role } = req.body;
        
        // Check if user already exists
        const existingUser = await User.findOne({ username });
        if (existingUser) return res.status(400).json({ error: 'User already exists.' });

        // Hash password
        const salt = await bcrypt.genSalt(10);
        const passwordHash = await bcrypt.hash(password, salt);

        // Save new user
        const newUser = new User({ name, username, passwordHash, role });
        await newUser.save();
        
        res.status(201).json({ message: 'User registered successfully.' });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

// User Login Logic
export const login = async (req, res) => {
    try {
        const { username, password } = req.body;
        
        // Find user by username
        const user = await User.findOne({ username });
        if (!user) return res.status(404).json({ error: 'User not found.' });

        // Check password
        const isMatch = await bcrypt.compare(password, user.passwordHash);
        if (!isMatch) return res.status(401).json({ error: 'Invalid credentials.' });

        // Generate JWT Token
        const token = jwt.sign(
            { id: user._id, role: user.role, name: user.name }, 
            process.env.JWT_SECRET, 
            { expiresIn: '7d' }
        );
        
        // Send success response with token
        res.json({ 
            token, 
            user: { id: user._id, name: user.name, username: user.username, role: user.role } 
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

export const getTeachers = async (req, res) => {
    try {
        const teachers = await User.find({ role: 'teacher' }).select('name _id');
        res.json(teachers);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

export const setPattern = async (req, res) => {
    try {
        const { patternCode } = req.body;
        if (!patternCode || patternCode.length < 3) return res.status(400).json({ error: 'Pattern too short.' });

        // Ensure pattern unique ho (taaki 2 baccho ka same pattern na ho)
        const existing = await User.findOne({ patternCode });
        if (existing && existing._id.toString() !== req.user.id) {
            return res.status(400).json({ error: 'This pattern is already taken. Try another.' });
        }

        await User.findByIdAndUpdate(req.user.id, { patternCode });
        res.json({ message: 'Pattern saved successfully!' });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};


export const patternLogin = async (req, res) => {
    try {
        const { patternCode } = req.body;
        
        // Pattern se student ko dhoondho
        const user = await User.findOne({ patternCode, role: 'student' });
        if (!user) return res.status(404).json({ error: 'Invalid Pattern. No student found.' });

        // Agar mil gaya toh token de do
        const token = jwt.sign({ id: user._id, role: user.role, name: user.name }, process.env.JWT_SECRET, { expiresIn: '7d' });
        
        res.json({ token, user: { id: user._id, name: user.name, username: user.username, role: user.role } });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};
