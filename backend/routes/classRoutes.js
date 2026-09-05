import express from 'express';
import { createClass, verifyClassCode, getMyClasses, endClass } from '../controllers/classController.js';
import { verifyToken } from '../middleware/authMiddleware.js'; // Auth middleware import kiya

const router = express.Router();

// Class create karne ke liye pehle token verify hoga, fir controller chalega
router.post('/', verifyToken, createClass);
router.get('/my', verifyToken, getMyClasses);
router.get('/:code', verifyClassCode);
router.post('/:code/end', verifyToken, endClass);

export default router;