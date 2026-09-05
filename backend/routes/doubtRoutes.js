import express from 'express';
import multer from 'multer';
import { askDoubt, getMyDoubts, getPendingDoubtsForTeacher, answerDoubt } from '../controllers/doubtController.js';
import { verifyToken } from '../middleware/authMiddleware.js';

const router = express.Router();
const upload = multer({ storage: multer.memoryStorage() });
// Student Routes
router.post('/ask', verifyToken,upload.single('mediaFile'), askDoubt);
router.get('/my-doubts', verifyToken, getMyDoubts);

// Teacher Routes
router.get('/teacher-inbox', verifyToken, getPendingDoubtsForTeacher);
router.post('/:doubtId/answer', verifyToken, upload.single('mediaFile'), answerDoubt);

export default router;