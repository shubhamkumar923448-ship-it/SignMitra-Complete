import Doubt from '../models/Doubt.js';
import User from '../models/User.js';
import imagekit from '../config/imagekit.js';


// 1. Student Asks Doubt (With Video & Smart Merge)
export const askDoubt = async (req, res) => {
    try {
        if (req.user.role !== 'student') return res.status(403).json({ error: 'Only students can ask doubts.' });

        const { teacherId, typedText, rawSigns } = req.body;
        let questionVideoUrl = "";

        
        let signsList = rawSigns ? JSON.parse(rawSigns) : [];
        let signsString = signsList.join(" ");
        
        let finalQuestionText = typedText || "";
        if (signsString && typedText) {
            finalQuestionText = `Sign Gestures: "${signsString}" | Note: ${typedText}`;
        } else if (signsString) {
            finalQuestionText = signsString;
        } else if (!finalQuestionText) {
            finalQuestionText = "Video Doubt Attached";
        }

    
        if (req.file) {
            console.log("📥 Receiving Doubt Video...");
            const fileBase64 = req.file.buffer.toString('base64');
            const safeName = `doubt_${Date.now()}_${req.file.originalname.replace(/[^a-zA-Z0-9.]/g, '_')}`;

            const response = await imagekit.upload({
                file: fileBase64,
                fileName: safeName,
                folder: "/signmitra_doubts"
            });
            questionVideoUrl = response.url;
            console.log("✅ Doubt Video Uploaded:", questionVideoUrl);
        }

        const newDoubt = new Doubt({
            studentId: req.user.id,
            teacherId,
            questionText: finalQuestionText, 
            questionVideoUrl
        });

        await newDoubt.save();
        res.status(201).json({ success: true, doubt: newDoubt });
    } catch (err) {
        console.error("🔥 ASK DOUBT ERROR:", err);
        res.status(500).json({ error: err.message });
    }
};


export const getMyDoubts = async (req, res) => {
    try {
        const doubts = await Doubt.find({ studentId: req.user.id })
            .populate('teacherId', 'name')
            .sort({ createdAt: -1 }); // Naye doubts upar dikhenge
        res.json(doubts);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};


export const getPendingDoubtsForTeacher = async (req, res) => {
    try {
        if (req.user.role !== 'teacher') return res.status(403).json({ error: 'Unauthorized.' });

        const doubts = await Doubt.find({ teacherId: req.user.id })
            .populate('studentId', 'name username')
            .sort({ createdAt: -1 });
        res.json(doubts);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};


export const answerDoubt = async (req, res) => {
    try {
        if (req.user.role !== 'teacher') return res.status(403).json({ error: 'Unauthorized.' });
        
        const { doubtId } = req.params;
        const { answerText } = req.body;
        let answerVideoUrl = ""; 

        
        if (req.file) {
            console.log("🎙️ Receiving Teacher Audio Reply...");
            const fileBase64 = req.file.buffer.toString('base64');
            
            const response = await imagekit.upload({
                file: fileBase64,
                fileName: `reply_${Date.now()}_audio.webm`,
                folder: "/signmitra_replies"
            });
            answerVideoUrl = response.url;
            console.log("✅ Audio Reply Uploaded:", answerVideoUrl);
        }

        const updatedDoubt = await Doubt.findByIdAndUpdate(
            doubtId,
            { answerText, answerVideoUrl, status: 'resolved' },
            { new: true }
        );
        
        res.json({ success: true, doubt: updatedDoubt });
    } catch (err) {
        console.error("🔥 ANSWER DOUBT ERROR:", err);
        res.status(500).json({ error: err.message });
    }
};