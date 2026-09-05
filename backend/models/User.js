import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
    name: { type: String, required: true },
    username: { type: String, required: true, unique: true },
    passwordHash: { type: String, required: true },
    role: { type: String, enum: ['teacher', 'student', 'admin'], required: true },
    patternCode: { type: String, default: null }, 
    profilePicUrl: { type: String, default: 'https://placehold.co/150x150/7c3aed/ffffff?text=U' }, 
    createdAt: { type: Date, default: Date.now }
});

export default mongoose.model('User', userSchema);