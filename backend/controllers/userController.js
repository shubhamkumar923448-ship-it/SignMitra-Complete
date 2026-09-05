import User from '../models/User.js';
import imagekit from '../config/imagekit.js';
import bcrypt from 'bcryptjs';

// 1. Upload/Update Profile Picture
export const updateProfilePic = async (req, res) => {
    try {
        if (!req.file) return res.status(400).json({ error: 'No image provided.' });

        // ImageKit par upload karein
        const response = await imagekit.upload({
            file: req.file.buffer, // Coming from Multer
            fileName: `profile_${req.user.id}_${Date.now()}.jpg`,
            folder: '/signmitra_profiles'
        });

        // DB me URL update karein
        const updatedUser = await User.findByIdAndUpdate(
            req.user.id, 
            { profilePicUrl: response.url }, 
            { new: true }
        ).select('-passwordHash'); // Password hash ko response me na bhejein

        res.json({ success: true, user: updatedUser });
    } catch (err) {
        console.error("Profile Pic Upload Error:", err);
        res.status(500).json({ error: 'Failed to update profile picture.' });
    }
};

// 2. Update Password
export const updatePassword = async (req, res) => {
    try {
        const { newPassword } = req.body;
        if (!newPassword || newPassword.length < 6) {
            return res.status(400).json({ error: 'Password must be at least 6 characters long.' });
        }

        const salt = await bcrypt.genSalt(10);
        const passwordHash = await bcrypt.hash(newPassword, salt);

        await User.findByIdAndUpdate(req.user.id, { passwordHash });

        res.json({ success: true, message: 'Password updated successfully!' });
    } catch (err) {
        res.status(500).json({ error: 'Failed to update password.' });
    }
};