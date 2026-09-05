import ImageKit from 'imagekit';
import dotenv from 'dotenv';

dotenv.config(); // Ensure env variables are loaded

// 1. You MUST use 'new ImageKit' to create the instance
const imagekit = new ImageKit({
    publicKey: process.env.IMAGEKIT_PUBLIC_KEY,
    privateKey: process.env.IMAGEKIT_PRIVATE_KEY,
    urlEndpoint: process.env.IMAGEKIT_URL_ENDPOINT
});

// 2. Export this specific instance, NOT the ImageKit class
export default imagekit;