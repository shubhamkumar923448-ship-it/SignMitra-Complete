import express from 'express';
import { updateProfilePic, updatePassword } from '../controllers/userController.js';
import { verifyToken } from '../middleware/authMiddleware.js';
import multer from 'multer';

const router = express.Router();
const upload = multer({ storage: multer.memoryStorage() }); // RAM me save karega ImageKit ke liye

router.post('/profile-pic', verifyToken, upload.single('profileImage'), updateProfilePic);
router.post('/update-password', verifyToken, updatePassword);

export default router;