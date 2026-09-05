import Lecture from '../models/Lecture.js';
import imagekit from '../config/imagekit.js'; 


// 1. Upload new lecture (Video details saving)
export const uploadLecture = async (req, res) => {
    try {
        if (req.user.role !== 'teacher') return res.status(403).json({ error: 'Only teachers can upload.' });
        
        // Debugging logs to see what arrived
        console.log("📥 Received Form Data (Body):", req.body);
        console.log("📁 Received File:", req.file ? req.file.originalname : "No File");

        const { title, subject, grade } = req.body;
        const file = req.file;

        if (!file) return res.status(400).json({ error: "Please upload a video file." });
        if (!title || !subject || !grade) return res.status(400).json({ error: "Title, Subject, and Grade are required." });

        const safeFileName = `lecture_${Date.now()}_${file.originalname.replace(/[^a-zA-Z0-9.]/g, '_')}`;
        
        // Convert Buffer to base64 for ImageKit
        const fileBase64 = file.buffer.toString('base64');

        // Upload to ImageKit
        const response = await imagekit.upload({
            file: fileBase64,
            fileName: safeFileName,
            folder: "/signmitra_lectures" 
        });

        console.log("☁️ ImageKit Upload Success:", response.url);

        // Save to Database
        const newLecture = new Lecture({
            teacherId: req.user.id,
            title, 
            subject, 
            grade, 
            videoUrl: response.url
        });
        
        await newLecture.save();
        console.log("✅ Database Save Success!");
        
        res.status(201).json({ success: true, lecture: newLecture });

    } catch (err) {
        console.error("🔥 BACKEND UPLOAD ERROR:", err);
        res.status(500).json({ error: err.message });
    }
};
// 2. Get Teacher's own videos
export const getMyLectures = async (req, res) => {
    try {
        const lectures = await Lecture.find({ teacherId: req.user.id }).sort({ createdAt: -1 });
        res.json(lectures);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

// 3. Delete a Video
export const deleteLecture = async (req, res) => {
    try {
        if (req.user.role !== 'teacher') return res.status(403).json({ error: 'Unauthorized.' });

        const lectureId = req.params.id;
        await Lecture.findByIdAndDelete(lectureId);
        // Future: ImageKit API call yahan aayegi cloud se video delete karne ke liye

        res.json({ success: true, message: 'Lecture deleted.' });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

//get all lecture for student 
export const getAllLectures = async (req, res) => {
    try {
        // .populate() se hume teacher ka naam bhi mil jayega
        const lectures = await Lecture.find()
            .populate('teacherId', 'name')
            .sort({ createdAt: -1 }); // Naye videos upar dikhenge
            
        res.json(lectures);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};