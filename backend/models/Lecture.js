import mongoose from 'mongoose';

const lectureSchema = new mongoose.Schema({
    teacherId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    title: { type: String, required: true },
    subject: { type: String, required: true },
    grade: { type: Number, required: true },
    // Future me ImageKit ka direct link yahan save hoga
    videoUrl: { type: String, default: '' },
    createdAt: { type: Date, default: Date.now }
});

export default mongoose.model('Lecture', lectureSchema);