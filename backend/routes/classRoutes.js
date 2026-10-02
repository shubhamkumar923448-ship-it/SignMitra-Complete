import express from 'express';
import { createClass, verifyClassCode, getMyClasses, endClass } from '../controllers/classController.js';
import { verifyToken } from '../middleware/authMiddleware.js'; 

const router = express.Router();


router.post('/', verifyToken, createClass);
router.get('/my', verifyToken, getMyClasses);
router.get('/:code', verifyClassCode);
router.post('/:code/end', verifyToken, endClass);

export default router;