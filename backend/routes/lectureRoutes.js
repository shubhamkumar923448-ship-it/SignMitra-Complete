import express from 'express';
import multer from 'multer';
import { uploadLecture, getMyLectures, deleteLecture, getAllLectures } from '../controllers/lectureController.js';
import { verifyToken } from '../middleware/authMiddleware.js';

const router = express.Router();

const upload = multer({ storage: multer.memoryStorage() });

router.post('/upload', verifyToken, upload.single('videoFile'), uploadLecture);
router.post('/upload', verifyToken, uploadLecture);
router.get('/my', verifyToken, getMyLectures);
router.delete('/:id', verifyToken, deleteLecture);
router.get('/', verifyToken, getAllLectures);

export default router;