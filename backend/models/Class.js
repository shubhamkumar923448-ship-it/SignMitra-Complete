import mongoose from 'mongoose';

const classSchema = new mongoose.Schema({
    teacherId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    subject: { type: String, required: true },
    joinCode: { type: String, required: true, unique: true }, // Jaise NEXUS-A1B2
    status: { type: String, enum: ['active', 'ended'], default: 'active' },
    createdAt: { type: Date, default: Date.now }
});

export default mongoose.model('Class', classSchema);