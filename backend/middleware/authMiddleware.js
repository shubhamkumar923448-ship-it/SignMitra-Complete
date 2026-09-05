import jwt from 'jsonwebtoken';

export const verifyToken = (req, res, next) => {
    // Frontend token bhejega usko hum read karenge
    const authHeader = req.headers['authorization'];
    if (!authHeader) return res.status(401).json({ error: 'Access denied. No token provided.' });
    
    const token = authHeader.split(' ')[1];
    
    try {
        // Token ko secret key se verify karenge
        const verified = jwt.verify(token, process.env.JWT_SECRET);
        req.user = verified; // Verified user ka data req me daal denge
        next(); // Agle function ko pass kar denge
    } catch (err) {
        res.status(403).json({ error: 'Invalid or expired token.' });
    }
};