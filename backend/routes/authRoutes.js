import express from 'express';
import { register, login, getTeachers, setPattern, patternLogin} from '../controllers/authController.js';
import { verifyToken } from '../middleware/authMiddleware.js';
const router = express.Router();

router.post('/register', register);
router.post('/login', login);
router.get('/teachers', verifyToken, getTeachers);
router.post('/set-pattern', verifyToken, setPattern);
router.post('/pattern-login', patternLogin); 
export default router;