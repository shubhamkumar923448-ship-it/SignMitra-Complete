import Class from '../models/Class.js';

export const createClass = async (req, res) => {
    try {
        // Sirf Teacher hi class bana sakta hai
        if (req.user.role !== 'teacher') return res.status(403).json({ error: 'Only teachers can create classes.' });
        
        const { subject } = req.body;
        
        // Random 4-digit code generate karein
        const randomId = Math.random().toString(36).substring(2, 6).toUpperCase();
        const joinCode = `NEXUS-${randomId}`;

        // Database me save karein
        const newClass = new Class({ 
            teacherId: req.user.id, 
            subject, 
            joinCode 
        });
        
        await newClass.save();
        
        // Success response
        res.status(201).json(newClass);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

export const getMyClasses = async (req, res) => {
    try {
        const filter = req.user.role === 'teacher' ? { teacherId: req.user.id } : {};
        const classes = await Class.find(filter).populate('teacherId', 'name username');
        res.json(classes);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

export const endClass = async (req, res) => {
    try {
        if (req.user.role !== 'teacher') {
            return res.status(403).json({ error: 'Only teachers can end classes.' });
        }
        
        const { code } = req.params;
        const updatedClass = await Class.findOneAndUpdate(
            { joinCode: code.toUpperCase() },
            { status: 'ended' },
            { new: true }
        );
        
        res.json({ success: true, message: "Session terminated permanently.", class: updatedClass });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

export const verifyClassCode = async (req, res) => {
    try {
        const { code } = req.params;
        const foundClass = await Class.findOne({ joinCode: code.toUpperCase() });
        
        if (!foundClass) {
            return res.status(404).json({ error: 'Invalid session code. Class does not exist.' });
        }
        
        if (foundClass.status === 'ended') {
            return res.status(400).json({ error: 'This session has been terminated by the educator.' });
        }

        res.status(200).json({ success: true, class: foundClass });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};