import mongoose from 'mongoose';

const doubtSchema = new mongoose.Schema({
    studentId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    teacherId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    
    
    questionText: { type: String, required: true }, 
    questionVideoUrl: { type: String, default: '' }, 
    
    status: { type: String, enum: ['unresolved', 'resolved'], default: 'unresolved' },
    
    
    answerText: { type: String, default: '' },
    answerVideoUrl: { type: String, default: '' },
    
    createdAt: { type: Date, default: Date.now }
});

export default mongoose.model('Doubt', doubtSchema);